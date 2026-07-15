# validation.py
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from .models import Invoice, InvoiceItem, ValidationError, ErrorLevel, ErrorCategory


TOLERANCE = Decimal("0.02")  


def _round(value: Optional[Decimal]) -> Optional[Decimal]:
    if value is None:
        return None
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _diff(a: Optional[Decimal], b: Optional[Decimal]) -> Optional[Decimal]:
    if a is None or b is None:
        return None
    return abs(_round(a) - _round(b))


def _make_error(
    invoice: Invoice,
    level: ErrorLevel,
    category: ErrorCategory,
    field_name: str,
    error_message: str,
    expected_value: Decimal,
    actual_value: Decimal,
    invoice_item: Optional[InvoiceItem] = None,
) -> ValidationError:
   
    error = ValidationError(
        level=level,
        category=category,
        field_name=field_name,
        error_message=error_message,
        expected_value=str(expected_value),
        actual_value=str(actual_value),
    )
    error.invoice = invoice
    if invoice_item is not None:
        error.invoice_item = invoice_item
    return error




def _validate_item_negative_amounts(
    invoice: Invoice,
    item: InvoiceItem,
) -> list[ValidationError]:
    errors = []
    for field_name in ("fixed_rent", "sgst", "cgst", "total"):
        value = getattr(item, field_name)
        if value is not None and value < 0:
            errors.append(_make_error(
                invoice=invoice,
                level=ErrorLevel.ITEM,
                category=ErrorCategory.AMOUNT,
                field_name=field_name,
                error_message=f"Item {field_name} is negative, which is not valid for a billed amount.",
                expected_value=Decimal("0.00"),
                actual_value=value,
                invoice_item=item,
            ))
    return errors


def _validate_item_required_fields(
    invoice: Invoice,
    item: InvoiceItem,
) -> list[ValidationError]:
    """Flags any missing (null) amount fields on an item. These fields are
    needed to cross-check the item total, so a null here means that check
    can't run at all — worth surfacing as its own error rather than being
    silently skipped."""
    errors = []
    for field_name in ("fixed_rent", "sgst", "cgst", "total"):
        if getattr(item, field_name) is None:
            errors.append(_make_error(
                invoice=invoice,
                level=ErrorLevel.ITEM,
                category=ErrorCategory.MISSING_DATA,
                field_name=field_name,
                error_message=f"Item {field_name} is missing (null).",
                expected_value="<not null>",
                actual_value="null",
                invoice_item=item,
            ))
    return errors


def _validate_item_optional_field_nulls(
    invoice: Invoice,
    item: InvoiceItem,
) -> list[ValidationError]:
    """Flags nulls in the item's other nullable (Optional) columns —
    phone_number, employee_code, employee_name. These aren't used in any
    arithmetic check, but a missing identity field usually means the
    source document extraction failed to pick it up, so it's still worth
    surfacing as an error."""
    errors = []
    for field_name in ("phone_number", "employee_code", "employee_name"):
        if getattr(item, field_name) is None:
            errors.append(_make_error(
                invoice=invoice,
                level=ErrorLevel.ITEM,
                category=ErrorCategory.MISSING_DATA,
                field_name=field_name,
                error_message=f"Item {field_name} is missing (null).",
                expected_value="<not null>",
                actual_value="null",
                invoice_item=item,
            ))
    return errors


def _validate_item_sgst_cgst_symmetry(
    invoice: Invoice,
    item: InvoiceItem,
) -> list[ValidationError]:
    """Under Indian intra-state GST rules, SGST and CGST are split evenly,
    so they should be equal for a given item. A mismatch usually indicates
    an OCR/extraction error rather than a genuine tax difference."""
    errors = []
    if item.sgst is not None and item.cgst is not None:
        if _diff(item.sgst, item.cgst) > TOLERANCE:
            errors.append(_make_error(
                invoice=invoice,
                level=ErrorLevel.ITEM,
                category=ErrorCategory.AMOUNT,
                field_name="sgst",
                error_message=(
                    f"SGST and CGST are expected to be equal for intra-state billing, "
                    f"but differ (sgst={item.sgst}, cgst={item.cgst})."
                ),
                expected_value=item.cgst,
                actual_value=item.sgst,
                invoice_item=item,
            ))
    return errors


def _validate_item_amount(
    invoice: Invoice,
    item: InvoiceItem,
) -> list[ValidationError]:
    errors = []

    errors.extend(_validate_item_negative_amounts(invoice, item))
    errors.extend(_validate_item_required_fields(invoice, item))
    errors.extend(_validate_item_optional_field_nulls(invoice, item))
    errors.extend(_validate_item_sgst_cgst_symmetry(invoice, item))

    if any(v is None for v in [item.fixed_rent, item.sgst, item.cgst, item.total]):
        return errors  # already flagged as missing above; can't cross-check total

    expected_total = _round(item.fixed_rent + item.sgst + item.cgst)
    diff = _diff(expected_total, item.total)

    if diff is not None and diff > TOLERANCE:
        errors.append(_make_error(
            invoice=invoice,
            level=ErrorLevel.ITEM,
            category=ErrorCategory.AMOUNT,
            field_name="total",
            error_message=(
                f"Item total does not match fixed_rent + sgst + cgst. "
                f"({item.fixed_rent} + {item.sgst} + {item.cgst} = {expected_total})"
            ),
            expected_value=expected_total,
            actual_value=item.total,
            invoice_item=item,
        ))

    return errors




def _validate_invoice_negative_amounts(invoice: Invoice) -> list[ValidationError]:
    errors = []
    for field_name in ("subtotal", "sgst_total", "cgst_total", "grand_total"):
        value = getattr(invoice, field_name)
        if value is not None and value < 0:
            errors.append(_make_error(
                invoice=invoice,
                level=ErrorLevel.INVOICE,
                category=ErrorCategory.AMOUNT,
                field_name=field_name,
                error_message=f"Invoice {field_name} is negative, which is not valid for a billed amount.",
                expected_value=Decimal("0.00"),
                actual_value=value,
            ))
    return errors


def _validate_invoice_required_fields(invoice: Invoice) -> list[ValidationError]:
    """Flags any missing (null) amount fields on the invoice itself. These
    are needed for the sum-matches-items and grand-total checks below, so a
    null here means those checks can't run at all — worth surfacing on its
    own rather than being silently skipped."""
    errors = []
    for field_name in ("subtotal", "sgst_total", "cgst_total", "grand_total"):
        if getattr(invoice, field_name) is None:
            errors.append(_make_error(
                invoice=invoice,
                level=ErrorLevel.INVOICE,
                category=ErrorCategory.MISSING_DATA,
                field_name=field_name,
                error_message=f"Invoice {field_name} is missing (null).",
                expected_value="<not null>",
                actual_value="null",
            ))
    return errors


def _validate_invoice_optional_field_nulls(invoice: Invoice) -> list[ValidationError]:
   
    errors = []
    for field_name in ("customer_name", "source_file_path"):
        if getattr(invoice, field_name) is None:
            errors.append(_make_error(
                invoice=invoice,
                level=ErrorLevel.INVOICE,
                category=ErrorCategory.MISSING_DATA,
                field_name=field_name,
                error_message=f"Invoice {field_name} is missing (null).",
                expected_value="<not null>",
                actual_value="null",
            ))
    return errors


def _validate_invoice_sgst_cgst_symmetry(invoice: Invoice) -> list[ValidationError]:
    errors = []
    if invoice.sgst_total is not None and invoice.cgst_total is not None:
        if _diff(invoice.sgst_total, invoice.cgst_total) > TOLERANCE:
            errors.append(_make_error(
                invoice=invoice,
                level=ErrorLevel.INVOICE,
                category=ErrorCategory.AMOUNT,
                field_name="sgst_total",
                error_message=(
                    f"SGST total and CGST total are expected to be equal for intra-state "
                    f"billing, but differ (sgst_total={invoice.sgst_total}, cgst_total={invoice.cgst_total})."
                ),
                expected_value=invoice.cgst_total,
                actual_value=invoice.sgst_total,
            ))
    return errors


def _validate_invoice_amounts(invoice: Invoice) -> list[ValidationError]:
    errors = []
    errors.extend(_validate_invoice_negative_amounts(invoice))
    errors.extend(_validate_invoice_required_fields(invoice))
    errors.extend(_validate_invoice_optional_field_nulls(invoice))
    errors.extend(_validate_invoice_sgst_cgst_symmetry(invoice))
    items = invoice.items

    
    zero = Decimal("0.00")

   
    any_fixed_rent_missing = any(i.fixed_rent is None for i in items)
    any_sgst_missing = any(i.sgst is None for i in items)
    any_cgst_missing = any(i.cgst is None for i in items)

    computed_subtotal = None if any_fixed_rent_missing else _round(sum((i.fixed_rent for i in items), zero))
    computed_sgst    = None if any_sgst_missing        else _round(sum((i.sgst        for i in items), zero))
    computed_cgst    = None if any_cgst_missing        else _round(sum((i.cgst        for i in items), zero))

    checks = [
        ("subtotal",   computed_subtotal, invoice.subtotal),
        ("sgst_total", computed_sgst,     invoice.sgst_total),
        ("cgst_total", computed_cgst,     invoice.cgst_total),
    ]

    for field_name, expected, actual in checks:
        diff = _diff(expected, actual)
        if diff is not None and diff > TOLERANCE:
            errors.append(_make_error(
                invoice=invoice,
                level=ErrorLevel.INVOICE,
                category=ErrorCategory.AMOUNT,
                field_name=field_name,
                error_message=(
                    f"Invoice {field_name} does not match sum of item values. "
                    f"(computed: {expected}, stated: {actual})"
                ),
                expected_value=expected,
                actual_value=actual,
            ))

    if all(v is not None for v in [invoice.subtotal, invoice.sgst_total, invoice.cgst_total, invoice.grand_total]):
        expected_grand = _round(invoice.subtotal + invoice.sgst_total + invoice.cgst_total)
        diff = _diff(expected_grand, invoice.grand_total)
        if diff is not None and diff > TOLERANCE:
            errors.append(_make_error(
                invoice=invoice,
                level=ErrorLevel.INVOICE,
                category=ErrorCategory.AMOUNT,
                field_name="grand_total",
                error_message=(
                    f"Grand total does not match subtotal + sgst_total + cgst_total. "
                    f"({invoice.subtotal} + {invoice.sgst_total} + {invoice.cgst_total} = {expected_grand})"
                ),
                expected_value=expected_grand,
                actual_value=invoice.grand_total,
            ))

    return errors




def _validate_invoice_date_required_fields(invoice: Invoice) -> list[ValidationError]:
    """Flags any missing (null) date fields on the invoice. These are
    needed for the ordering checks below, so a null here means those checks
    can't run at all — worth surfacing on its own rather than being
    silently skipped."""
    errors = []
    for field_name in ("bill_date", "bill_period_start", "bill_period_end"):
        if getattr(invoice, field_name) is None:
            errors.append(_make_error(
                invoice=invoice,
                level=ErrorLevel.INVOICE,
                category=ErrorCategory.MISSING_DATA,
                field_name=field_name,
                error_message=f"Invoice {field_name} is missing (null).",
                expected_value="<not null>",
                actual_value="null",
            ))
    return errors


def _validate_invoice_dates(invoice: Invoice) -> list[ValidationError]:
    errors = []

    errors.extend(_validate_invoice_date_required_fields(invoice))

    if invoice.bill_period_start and invoice.bill_period_end:
        if invoice.bill_period_start > invoice.bill_period_end:
            errors.append(_make_error(
                invoice=invoice,
                level=ErrorLevel.INVOICE,
                category=ErrorCategory.DATE,
                field_name="bill_period_start",
                error_message="Bill period start is after bill period end.",
                expected_value=f"<= {invoice.bill_period_end}",
                actual_value=str(invoice.bill_period_start),
            ))


    if invoice.bill_date and invoice.bill_period_start:
        if invoice.bill_date < invoice.bill_period_start:
            errors.append(_make_error(
                invoice=invoice,
                level=ErrorLevel.INVOICE,
                category=ErrorCategory.DATE,
                field_name="bill_date",
                error_message="Bill date is before bill period start.",
                expected_value=f">= {invoice.bill_period_start}",
                actual_value=str(invoice.bill_date),
            ))

    if invoice.bill_date and invoice.bill_period_end:
        if invoice.bill_date < invoice.bill_period_end:
            errors.append(_make_error(
                invoice=invoice,
                level=ErrorLevel.INVOICE,
                category=ErrorCategory.DATE,
                field_name="bill_date",
                error_message="Bill date is before bill period end; invoices are normally issued on or after the period they cover ends.",
                expected_value=f">= {invoice.bill_period_end}",
                actual_value=str(invoice.bill_date),
            ))

    return errors



def validate_invoice(invoice: Invoice) -> list[ValidationError]:
    errors = []

    for item in invoice.items:
        errors.extend(_validate_item_amount(invoice, item))

    errors.extend(_validate_invoice_amounts(invoice))
    errors.extend(_validate_invoice_dates(invoice))

    return errors