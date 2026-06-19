from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Invoice,InvoiceItem

router=APIRouter(
    prefix="/invoices",
    tags=["Invoices"])

@router.post("/upload")
def upload_invoice():
    pass
    


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

