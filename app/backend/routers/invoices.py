from fastapi import HTTPException, Depends, APIRouter,Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
from ..db import get_db
from .. import schemas
from ..validation import validate_invoice
from ..models import Invoice,InvoiceItem,InvoiceStatus
from ..Oauth import require_admin, require_user, get_current_user
from ..models import User




router=APIRouter(
    prefix="/invoices",
    tags=["Invoices"])

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
        
    )
    invoice.items = [
        InvoiceItem(**item.model_dump()) for item in payload.items
    ]

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    errors = validate_invoice(invoice)
    db.add_all(errors)
    invoice.status = InvoiceStatus.FLAGGED if errors else InvoiceStatus.VALID
    db.commit()
    db.refresh(invoice)

    return invoice
    


@router.get("/", response_model=list[schemas.InvoiceOut])
def list_invoices(
    status: Optional[InvoiceStatus] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user)
):
    query = select(Invoice)
    if status:
        query = query.where(Invoice.status == status)
    return db.execute(query.offset(skip).limit(limit)).scalars().all()



@router.get("/{invoice_id}/items", response_model=list[schemas.InvoiceItemOut])
def get_invoice_items(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_user)):
    invoice = db.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(404, "Invoice not found")
    return invoice.items



@router.get("/{invoice_id}/errors", response_model=list[schemas.ValidationErrorOut])
def get_invoice_errors(invoice_id: int, db: Session = Depends(get_db),current_user: User = Depends(require_user)):
    invoice = db.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(404, "Invoice not found")
    return invoice.errors




@router.delete("/{invoice_id}", status_code=204)
def delete_invoice(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_user)):
    invoice = db.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(404, "Invoice not found")
    db.delete(invoice)
    db.commit()


@router.get("/number/{invoice_number}", response_model=schemas.InvoiceOut)
def get_invoice_by_number(invoice_number: str, db: Session = Depends(get_db), current_user: User = Depends(require_user)):
    invoice = db.execute(
        select(Invoice).where(Invoice.invoice_number == invoice_number)
    ).scalar_one_or_none()
    if not invoice:
        raise HTTPException(404, f"Invoice {invoice_number} not found")
    return invoice

