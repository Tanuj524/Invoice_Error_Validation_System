import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import toast from "react-hot-toast";
import { getInvoice } from "../api/invoices";
import useInvoiceStore from "../store/invoiceStore";
import Navbar from "../components/Navbar";


const STATUS_BADGE = {
  VALID: { label: "Passed", bg: "bg-green-900/30", text: "text-green-400" },
  FLAGGED: { label: "Flagged", bg: "bg-amber-900/30", text: "text-amber-400" },
  PENDING: { label: "Pending", bg: "bg-gray-800", text: "text-gray-400" },
  PROCESSING: { label: "Processing", bg: "bg-gray-800", text: "text-gray-400" },
};

function formatCurrency(value) {
  if (value === null || value === undefined) return "—";
  return `Rs ${Number(value).toLocaleString("en-IN", { minimumFractionDigits: 2 })}`;
}

function formatDate(value) {
  if (!value) return "—";
  return new Date(value).toLocaleDateString("en-IN", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}


function InvoiceDetail() {
  const { id } = useParams();
  const invoice = useInvoiceStore((state) => state.currentInvoice);
  const isLoading = useInvoiceStore((state) => state.isLoadingCurrent);
  const fetchInvoice = useInvoiceStore((state) => state.fetchInvoice);

  useEffect(() => {
    fetchInvoice(id).then((result) => {
      if (!result.success) toast.error(result.error);
    });
  }, [id, fetchInvoice]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center text-gray-400 text-sm">
        Loading invoice...
      </div>
    );
  }

  if (!invoice) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center text-gray-400 text-sm">
        Invoice not found.
      </div>
    );
  }

  const badge = STATUS_BADGE[invoice.status];
  const items = invoice.items;
  const errors = invoice.errors;

  return (
    <div className="min-h-screen bg-gray-950">
      <Navbar />
          <div className="px-6 py-8">
      <div className="max-w-7xl mx-auto">
        <Link to="/dashboard" className="text-sm text-blue-400 hover:underline">
          ← Back to invoices
        </Link>

        <div className="mt-4 mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-medium text-gray-100">{invoice.invoice_number ?? "No invoice number"}</h1>
            <p className="text-sm text-gray-400">{invoice.customer_name ?? "No customer name"}</p>
          </div>
          <span className={`text-xs px-2.5 py-1 rounded-md ${badge.bg} ${badge.text}`}>
            {badge.label}
          </span>
        </div>

        <div className="grid grid-cols-3 gap-3 mb-6">
          <InfoCard label="Bill date" value={formatDate(invoice.bill_date)} />
          <InfoCard
            label="Bill period"
            value={`${formatDate(invoice.bill_period_start)} – ${formatDate(invoice.bill_period_end)}`}
          />
          <InfoCard label="Source file" value={invoice.source_file_path ?? "—"} />
          <InfoCard label="Subtotal" value={formatCurrency(invoice.subtotal)} />
          <InfoCard
            label="SGST + CGST"
            value={`${formatCurrency(invoice.sgst_total)} / ${formatCurrency(invoice.cgst_total)}`}
          />
          <InfoCard label="Grand total" value={formatCurrency(invoice.grand_total)} />
        </div>

        {errors.length > 0 && (
          <div className="mb-6">
            <h2 className="text-sm font-medium text-gray-100 mb-2">
              Validation errors ({errors.length})
            </h2>
            <div className="bg-gray-900 border border-gray-800 rounded-xl divide-y divide-gray-800">
              {errors.map((err) => (
                <div key={err.id} className="px-4 py-3 text-sm">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-gray-100">{err.field_name ?? err.category}</span>
                    <span className="text-xs text-gray-500">{err.category}</span>
                  </div>
                  <p className="text-gray-400">{err.error_message}</p>
                  {(err.expected_value || err.actual_value) && (
                    <p className="text-xs text-gray-500 mt-1">
                      Expected: {err.expected_value ?? "—"} · Actual: {err.actual_value ?? "—"}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        <h2 className="text-sm font-medium text-gray-100 mb-2">Line items ({items.length})</h2>
        <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-900 text-left text-gray-400">
                <th className="font-medium px-4 py-2">Employee</th>
                <th className="font-medium px-4 py-2">Code</th>
                <th className="font-medium px-4 py-2">Phone</th>
                <th className="font-medium px-4 py-2 text-right">Fixed rent</th>
                <th className="font-medium px-4 py-2 text-right">SGST</th>
                <th className="font-medium px-4 py-2 text-right">CGST</th>
                <th className="font-medium px-4 py-2 text-right">Total</th>
              </tr>
            </thead>
            <tbody>
              {items.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-6 text-center text-gray-500">
                    No line items.
                  </td>
                </tr>
              ) : (
                items.map((item) => (
                  <tr key={item.id} className="border-t border-gray-800">
                    <td className="px-4 py-2 text-gray-100">{item.employee_name ?? "—"}</td>
                    <td className="px-4 py-2 text-gray-300">{item.employee_code ?? "—"}</td>
                    <td className="px-4 py-2 text-gray-300">{item.phone_number ?? "—"}</td>
                    <td className="px-4 py-2 text-right text-gray-300">{formatCurrency(item.fixed_rent)}</td>
                    <td className="px-4 py-2 text-right text-gray-300">{formatCurrency(item.sgst)}</td>
                    <td className="px-4 py-2 text-right text-gray-300">{formatCurrency(item.cgst)}</td>
                    <td className="px-4 py-2 text-right text-gray-300">{formatCurrency(item.total)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
      </div>
    </div>
  );
}

function InfoCard({ label, value }) {
  return (
    <div className="bg-gray-900 rounded-lg p-4">
      <p className="text-xs text-gray-400 mb-1">{label}</p>
      <p className="text-sm font-medium text-gray-100">{value}</p>
    </div>
  );
}

export default InvoiceDetail;