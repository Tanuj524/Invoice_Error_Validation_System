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
  
    invoice = db.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(404, "Invoice not found")
    if current_user.role != UserRole.ADMIN and invoice.created_by != current_user.id:
        raise HTTPException(404, "Invoice not found")
    return invoice



@router.get("/{invoice_id}", response_model=schemas.InvoiceDetailOut)
def get_invoice(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_user)):
    return _get_owned_invoice(invoice_id, db, current_user)

@router.post("/upload", response_model=schemas.InvoiceDetailOut, status_code=201)
def create_invoice(payload: schemas.InvoiceIn, db: Session = Depends(get_db), current_user: User = Depends(require_user)):

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

    
    errors = validate_invoice(invoice)
    invoice.status = InvoiceStatus.FLAGGED if errors else InvoiceStatus.VALID
    invoice.errors = errors

    db.add(invoice)
    db.commit()

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
    query = select(Invoice).order_by(Invoice.created_at.desc())

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
    ).scalars().all()
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
       
        try:
            with db.begin_nested():

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
                db.flush() 

            results.append(schemas.BulkInvoiceResultItem(
                index=index,
                invoice_number=item.invoice_number,
                success=True,
                invoice_id=invoice.id,
                status=invoice.status,
            ))

        except IntegrityError as e:
            db.rollback()
            results.append(schemas.BulkInvoiceResultItem(
                index=index, invoice_number=item.invoice_number,
                success=False, error=str(e.orig),
        ))
        except ValueError as e:
            db.rollback()
            results.append(schemas.BulkInvoiceResultItem(
                index=index, invoice_number=item.invoice_number,
                success=False, error=str(e),
        ))
        except Exception as e:
            db.rollback()
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