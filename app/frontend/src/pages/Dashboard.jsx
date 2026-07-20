import { useEffect, useState } from "react";
import { listInvoices } from "../api/invoices";
import toast from "react-hot-toast";
import {useNavigate} from "react-router-dom";
import useInvoiceStore from "../store/invoiceStore";


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


function Dashboard() {
  const navigate = useNavigate();
  const invoices = useInvoiceStore((state) => state.invoices);
  const isLoading = useInvoiceStore((state) => state.isLoading);
  const fetchInvoices = useInvoiceStore((state) => state.fetchInvoices);

  useEffect(() => {
    fetchInvoices({ limit: 200 }).then((result) => {
      if (!result.success) toast.error(result.error);
    });
  }, [fetchInvoices]);

  const total = invoices.length;
  const passed = invoices.filter((i) => i.status === "VALID").length;
  const flagged = invoices.filter((i) => i.status === "FLAGGED").length;
  const inProgress = invoices.filter(
    (i) => i.status === "PENDING" || i.status === "PROCESSING"
  ).length;

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-400 text-sm">
        Loading invoices...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 px-6 py-8">
  <div className="max-w-7xl mx-auto">
    <div className="flex items-center justify-between mb-6">
      <div>
        <h1 className="text-xl font-medium text-gray-100">Invoices</h1>
        <p className="text-sm text-gray-400">Track uploads and validation results</p>
      </div>
    </div>

    <div className="grid grid-cols-4 gap-3 mb-6">
      <StatCard label="Total invoices" value={total} />
      <StatCard label="Passed" value={passed} valueClass="text-green-400" />
      <StatCard label="Flagged" value={flagged} valueClass="text-amber-400" />
      <StatCard label="In progress" value={inProgress} valueClass="text-gray-400" />
    </div>

    <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-gray-900 text-left text-gray-400">
            <th className="font-medium px-4 py-2">Invoice</th>
            <th className="font-medium px-4 py-2">Customer</th>
            <th className="font-medium px-4 py-2">Bill date</th>
            <th className="font-medium px-4 py-2 text-right">Grand total</th>
            <th className="font-medium px-4 py-2">Status</th>
          </tr>
        </thead>
        <tbody>
          {invoices.map((inv) => {
            const badge = STATUS_BADGE[inv.status] ?? STATUS_BADGE.PENDING;
            return (
              <tr
                key={inv.id}
                className="border-t border-gray-800 hover:bg-gray-900 cursor-pointer"
                onClick={() => navigate(`/invoices/${inv.id}`)}
              >
                <td className="px-4 py-2 text-gray-100">{inv.invoice_number}</td>
                <td className="px-4 py-2 text-gray-300">{inv.customer_name ?? "—"}</td>
                <td className="px-4 py-2 text-gray-300">{formatDate(inv.bill_date)}</td>
                <td className="px-4 py-2 text-right text-gray-300">{formatCurrency(inv.grand_total)}</td>
                <td className="px-4 py-2">
                  <span className={`inline-block text-xs px-2.5 py-1 rounded-md ${badge.bg} ${badge.text}`}>
                    {badge.label}
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  </div>
</div>
  );
}


function StatCard({ label, value, valueClass = "text-gray-100" }) {
  return (
    <div className="bg-gray-900 rounded-lg p-4">
      <p className="text-xs text-gray-400 mb-1">{label}</p>
      <p className={`text-2xl font-medium ${valueClass}`}>{value}</p>
    </div>
  );
}

export default Dashboard;