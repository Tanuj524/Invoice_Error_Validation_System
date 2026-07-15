# schemas.py
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from .models import SourceFormat, InvoiceStatus, ErrorLevel, ErrorCategory, UserRole

class InvoiceItemIn(BaseModel):
    phone_number: Optional[str] = None
    employee_code: Optional[str] = None
    employee_name: Optional[str] = None
    fixed_rent: Optional[Decimal] = None
    sgst: Optional[Decimal] = None
    cgst: Optional[Decimal] = None
    total: Optional[Decimal] = None


class InvoiceIn(BaseModel):
    invoice_number: str
    customer_name: Optional[str] = None
    source_format: SourceFormat
    source_file_path: Optional[str] = None
    bill_date: Optional[date] = None
    bill_period_start: Optional[date] = None
    bill_period_end: Optional[date] = None
    subtotal: Optional[Decimal] = None
    sgst_total: Optional[Decimal] = None
    cgst_total: Optional[Decimal] = None
    grand_total: Optional[Decimal] = None
    items: list[InvoiceItemIn] = []




class ValidationErrorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_id: int
    invoice_item_id: Optional[int] = None
    level: ErrorLevel
    category: ErrorCategory
    field_name: Optional[str] = None
    error_message: Optional[str] = None
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    created_at: datetime


class InvoiceItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_id: int
    phone_number: Optional[str] = None
    employee_code: Optional[str] = None
    employee_name: Optional[str] = None
    fixed_rent: Optional[Decimal] = None
    sgst: Optional[Decimal] = None
    cgst: Optional[Decimal] = None
    total: Optional[Decimal] = None


class InvoiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_number: str
    customer_name: Optional[str] = None
    source_format: SourceFormat
    bill_date: Optional[date] = None
    bill_period_start: Optional[date] = None
    bill_period_end: Optional[date] = None
    subtotal: Optional[Decimal] = None
    sgst_total: Optional[Decimal] = None
    cgst_total: Optional[Decimal] = None
    grand_total: Optional[Decimal] = None
    status: InvoiceStatus
    created_by: Optional[int] = None
    created_at: datetime


class InvoiceDetailOut(InvoiceOut):
    items: list[InvoiceItemOut] = []
    errors: list[ValidationErrorOut] = []


class UserIn(BaseModel):
    username: str
    email: EmailStr
    password: str  
    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime

class UpdateUserRole(BaseModel):
    role: UserRole

class UpdateUserStatus(BaseModel):
    is_active: bool


class ForgotPasswordIn(BaseModel):
    email: EmailStr

class ResetPasswordIn(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v
    

class BulkInvoiceIn(BaseModel):
    invoices: list[InvoiceIn]

    @field_validator("invoices")
    @classmethod
    def limit_batch_size(cls, v: list["InvoiceIn"]) -> list["InvoiceIn"]:
        if len(v) == 0:
            raise ValueError("Batch must contain at least one invoice")
        if len(v) > 100:
            raise ValueError("Batch cannot exceed 100 invoices per request")
        return v


class BulkInvoiceResultItem(BaseModel):
    index: int                     
    invoice_number: str
    success: bool
    invoice_id: Optional[int] = None
    status: Optional[InvoiceStatus] = None
    error: Optional[str] = None


class BulkInvoiceOut(BaseModel):
    total: int
    succeeded: int
    failed: int
    results: list[BulkInvoiceResultItem]