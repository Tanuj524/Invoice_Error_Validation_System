import apiClient from "./client";

export async function listInvoices({ status, skip = 0, limit = 50 } = {}) {
  const params = {};
  if (status) params.status = status;
  params.skip = skip;
  params.limit = limit;

  const response = await apiClient.get("/invoices/", { params });
  return response.data; // InvoiceOut[]
}

export async function getInvoice(invoiceId) {
  const response = await apiClient.get(`/invoices/${invoiceId}`);
  return response.data; // InvoiceDetailOut: header + items + errors
}