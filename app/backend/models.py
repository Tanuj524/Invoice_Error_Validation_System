import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Numeric,
    Text,
    ForeignKey,
    CheckConstraint,
    Enum as SAEnum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text

from .db import Base


class InvoiceStatus(str, enum.Enum):
    VALID = "VALID"           
    FLAGGED = "FLAGGED"  
    PENDING = "PENDING"      


class SourceFormat(str, enum.Enum):
    PDF = "PDF"
    EXCEL = "EXCEL"
    IMAGE = "IMAGE"


class ErrorLevel(str, enum.Enum):
    INVOICE = "INVOICE"  
    ITEM = "ITEM"         


class ErrorCategory(str, enum.Enum):
    DATE = "DATE"      
    AMOUNT = "AMOUNT"  


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)

    invoice_number = Column(String(100), nullable=False, unique=True, index=True)
    customer_name = Column(String(255))


    source_format = Column(SAEnum(SourceFormat, name="source_format"), nullable=False)
    source_file_path = Column(String(500)) 

    bill_date = Column(Date)
    bill_period_start = Column(Date)
    bill_period_end = Column(Date)

    subtotal = Column(Numeric(10, 2))
    sgst_total = Column(Numeric(10, 2))
    cgst_total = Column(Numeric(10, 2))
    grand_total = Column(Numeric(10, 2))

    status = Column(
        SAEnum(InvoiceStatus, name="invoice_status"),
        nullable=False,
        default=InvoiceStatus.PENDING,
        server_default=InvoiceStatus.PENDING.value,
    )

    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False,
        server_default=text("now()")
    )

    items = relationship(
        "InvoiceItem",
        back_populates="invoice",
        cascade="all, delete-orphan"
    )

    errors = relationship(
        "ValidationError",
        back_populates="invoice",
        cascade="all, delete-orphan"
    )



class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)

    invoice_id = Column(
        Integer,
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    phone_number = Column(String(20))
    employee_code = Column(String(20))
    employee_name = Column(String(255))

    fixed_rent = Column(Numeric(10, 2))
    sgst = Column(Numeric(10, 2))
    cgst = Column(Numeric(10, 2))
    total = Column(Numeric(10, 2))

    invoice = relationship("Invoice", back_populates="items")

    errors = relationship(
        "ValidationError",
        back_populates="invoice_item",
        cascade="all, delete-orphan"
    )


class ValidationError(Base):
    __tablename__ = "validation_errors"

    id = Column(Integer, primary_key=True, index=True)

    invoice_id = Column(
        Integer,
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

   
    invoice_item_id = Column(
        Integer,
        ForeignKey("invoice_items.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    level = Column(SAEnum(ErrorLevel, name="error_level"), nullable=False)
    category = Column(SAEnum(ErrorCategory, name="error_category"), nullable=False)

    field_name = Column(String(100))     
    error_message = Column(Text)
    expected_value = Column(String(255))
    actual_value = Column(String(255))

    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False,
        server_default=text("now()")
    )

    invoice = relationship("Invoice", back_populates="errors")
    invoice_item = relationship("InvoiceItem", back_populates="errors")

    __table_args__ = (
        CheckConstraint(
            "(level = 'ITEM' AND invoice_item_id IS NOT NULL) OR "
            "(level = 'INVOICE' AND invoice_item_id IS NULL)",
            name="ck_validation_error_level_consistency"
        ),
    )