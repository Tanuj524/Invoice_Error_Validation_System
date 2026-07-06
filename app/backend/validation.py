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
    return ValidationError(
        invoice_id=invoice.id,
        invoice_item_id=invoice_item.id if invoice_item else None,
        level=level,
        category=category,
        field_name=field_name,
        error_message=error_message,
        expected_value=str(expected_value),
        actual_value=str(actual_value),
    )




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
    errors.extend(_validate_item_sgst_cgst_symmetry(invoice, item))

    if any(v is None for v in [item.fixed_rent, item.sgst, item.cgst, item.total]):
        return errors  

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
    errors.extend(_validate_invoice_sgst_cgst_symmetry(invoice))
    items = invoice.items

    # sum()'s default start value is the int 0, which would silently mix
    # int and Decimal arithmetic (and misrepresent "no items yet" as an
    # exact Decimal 0.00 match). Passing Decimal("0.00") as the start value
    # keeps the result a Decimal throughout.
    zero = Decimal("0.00")
    computed_subtotal = _round(sum((i.fixed_rent for i in items if i.fixed_rent is not None), zero))
    computed_sgst    = _round(sum((i.sgst        for i in items if i.sgst        is not None), zero))
    computed_cgst    = _round(sum((i.cgst        for i in items if i.cgst        is not None), zero))

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




def _validate_invoice_dates(invoice: Invoice) -> list[ValidationError]:
    errors = []

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

    return errors



def validate_invoice(invoice: Invoice) -> list[ValidationError]:
    errors = []

    for item in invoice.items:
        errors.extend(_validate_item_amount(invoice, item))

    errors.extend(_validate_invoice_amounts(invoice))
    errors.extend(_validate_invoice_dates(invoice))

    return errors