from fastapi import HTTPException, Depends, APIRouter,Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import Optional
from ..db import get_db
from .. import schemas
from ..validation import validate_invoice
from ..models import Invoice,InvoiceItem,InvoiceStatus
from ..Oauth import require_admin, require_user, get_current_user
from ..models import User,UserRole




router=APIRouter(
    prefix="/invoices",
    tags=["Invoices"])


def _get_owned_invoice(invoice_id: int, db: Session, current_user: User) -> Invoice:
    """Fetch an invoice and enforce that non-admins can only access their own.
    Admins can access any invoice. Raises 404 for both "doesn't exist" and
    "not yours" so an attacker can't distinguish the two cases."""
    invoice = db.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(404, "Invoice not found")
    if current_user.role != UserRole.ADMIN and invoice.created_by != current_user.id:
        raise HTTPException(404, "Invoice not found")
    return invoice


@router.post("/upload", response_model=schemas.InvoiceDetailOut, status_code=201)
def create_invoice(payload: schemas.InvoiceIn, db: Session = Depends(get_db), current_user: User = Depends(require_user)):
    existing = db.execute(
        select(Invoice).where(Invoice.invoice_number == payload.invoice_number)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(409, f"Invoice {payload.invoice_number} already exists")

    invoice = Invoice(
        invoice_number=payload.invoice_number,
        customer_name=payload.customer_name,
        source_format=payload.source_format,
        source_file_path=payload.source_file_path,
        bill_date=payload.bill_date,
        bill_period_start=payload.bill_period_start,
        bill_period_end=payload.bill_period_end,
        subtotal=payload.subtotal,
        sgst_total=payload.sgst_total,
        cgst_total=payload.cgst_total,
        grand_total=payload.grand_total,
        status=InvoiceStatus.PROCESSING,
        created_by=current_user.id
    )
    invoice.items = [
        InvoiceItem(**item.model_dump()) for item in payload.items
    ]

    # Run validation against the in-memory object before the first commit,
    # then persist the invoice, its items, and its final status/errors in a
    # single commit. This shrinks the window where an invoice could be left
    # stuck in PROCESSING if the process crashes mid-request (previously
    # there were two separate commits).
    errors = validate_invoice(invoice)
    invoice.status = InvoiceStatus.FLAGGED if errors else InvoiceStatus.VALID
    invoice.errors = errors

    db.add(invoice)
    try:
        db.commit()
    except IntegrityError:
        # Handles the race where two requests both pass the "existing"
        # check above and then both try to insert the same invoice_number.
        db.rollback()
        raise HTTPException(409, f"Invoice {payload.invoice_number} already exists")

    db.refresh(invoice)
    return invoice
    


@router.get("/", response_model=list[schemas.InvoiceOut])
def list_invoices(
    status: Optional[InvoiceStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user)
):
    query = select(Invoice)

    # admins see all invoices, users only see their own
    if current_user.role == UserRole.ADMIN:
        pass
    else:
        query = query.where(Invoice.created_by == current_user.id)

    if status:
        query = query.where(Invoice.status == status)

    return db.execute(query.offset(skip).limit(limit)).scalars().all()



@router.get("/{invoice_id}/items", response_model=list[schemas.InvoiceItemOut])
def get_invoice_items(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_user)):
    invoice = _get_owned_invoice(invoice_id, db, current_user)
    return invoice.items



@router.get("/{invoice_id}/errors", response_model=list[schemas.ValidationErrorOut])
def get_invoice_errors(invoice_id: int, db: Session = Depends(get_db),current_user: User = Depends(require_user)):
    invoice = _get_owned_invoice(invoice_id, db, current_user)
    return invoice.errors




@router.delete("/{invoice_id}", status_code=204)
def delete_invoice(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_user)):
    invoice = _get_owned_invoice(invoice_id, db, current_user)
    db.delete(invoice)
    db.commit()


@router.get("/number/{invoice_number}", response_model=schemas.InvoiceOut)
def get_invoice_by_number(invoice_number: str, db: Session = Depends(get_db), current_user: User = Depends(require_user)):
    invoice = db.execute(
        select(Invoice).where(Invoice.invoice_number == invoice_number)
    ).scalar_one_or_none()
    if not invoice:
        raise HTTPException(404, f"Invoice {invoice_number} not found")
    if current_user.role != UserRole.ADMIN and invoice.created_by != current_user.id:
        raise HTTPException(404, f"Invoice {invoice_number} not found")
    return invoice



@router.post("/upload/bulk", response_model=schemas.BulkInvoiceOut, status_code=201)
def create_invoices_bulk(
    payload: schemas.BulkInvoiceIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    results: list[schemas.BulkInvoiceResultItem] = []

    for index, item in enumerate(payload.invoices):
        # Each invoice gets its own savepoint so one failure doesn't
        # poison the whole transaction for the rest of the batch.
        try:
            with db.begin_nested():
                existing = db.execute(
                    select(Invoice).where(Invoice.invoice_number == item.invoice_number)
                ).scalar_one_or_none()
                if existing:
                    raise ValueError(f"Invoice {item.invoice_number} already exists")

                invoice = Invoice(
                    invoice_number=item.invoice_number,
                    customer_name=item.customer_name,
                    source_format=item.source_format,
                    source_file_path=item.source_file_path,
                    bill_date=item.bill_date,
                    bill_period_start=item.bill_period_start,
                    bill_period_end=item.bill_period_end,
                    subtotal=item.subtotal,
                    sgst_total=item.sgst_total,
                    cgst_total=item.cgst_total,
                    grand_total=item.grand_total,
                    status=InvoiceStatus.PROCESSING,
                    created_by=current_user.id,
                )
                invoice.items = [
                    InvoiceItem(**line.model_dump()) for line in item.items
                ]

                errors = validate_invoice(invoice)
                invoice.status = InvoiceStatus.FLAGGED if errors else InvoiceStatus.VALID
                invoice.errors = errors

                db.add(invoice)
                db.flush()  # assigns invoice.id without committing the outer transaction

            results.append(schemas.BulkInvoiceResultItem(
                index=index,
                invoice_number=item.invoice_number,
                success=True,
                invoice_id=invoice.id,
                status=invoice.status,
            ))

        except IntegrityError as e:
            msg = f"Invoice {item.invoice_number} already exists" if "invoice_number" in str(e.orig) else str(e.orig)
            results.append(schemas.BulkInvoiceResultItem(
                index=index, invoice_number=item.invoice_number,
                success=False, error=msg,
        ))
        except ValueError as e:
            results.append(schemas.BulkInvoiceResultItem(
                index=index, invoice_number=item.invoice_number,
                success=False, error=str(e),
        ))
        except Exception as e:
            results.append(schemas.BulkInvoiceResultItem(
            index=index, invoice_number=item.invoice_number,
            success=False, error=f"Unexpected error: {e}",
    ))

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Failed to save batch: {e}")

    succeeded = sum(1 for r in results if r.success)
    return schemas.BulkInvoiceOut(
        total=len(results),
        succeeded=succeeded,
        failed=len(results) - succeeded,
        results=results,
    )