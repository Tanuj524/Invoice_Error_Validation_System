from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
from ..db import get_db
from .. import schemas
from ..validation import validate_invoice
from ..models import Invoice,InvoiceItem,InvoiceStatus

router=APIRouter(
    prefix="/invoices",
    tags=["Invoices"])

@router.post("/upload", response_model=schemas.InvoiceDetailOut, status_code=201)
def create_invoice(payload: schemas.InvoiceIn, db: Session = Depends(get_db)):
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

    # run validation synchronously since there's no file parsing to wait on —
    # this is pure arithmetic/date checks against data already in memory
    errors = validate_invoice(invoice)
    db.add_all(errors)
    invoice.status = InvoiceStatus.FLAGGED if errors else InvoiceStatus.VALID
    db.commit()
    db.refresh(invoice)

    return invoice
    


@router.get("/")
def get_invoices():
    pass

@router.get("/invalid")
def get_invalid_invoices():
    pass

@router.get("/{invoice_id}")
def get_invoice(invoice_id: int):
    pass

@router.get("/{invoice_id}/items")
def get_invoice_items(invoice_id: int):
    pass

@router.get("/{invoice_id}/errors")
def get_invoice_errors(invoice_id: int):
    pass

