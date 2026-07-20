import { create } from "zustand";
import { listInvoices, getInvoice } from "../api/invoices";

const useInvoiceStore = create((set, get) => ({
  invoices: [],
  isLoading: false,

  currentInvoice: null,
  isLoadingCurrent: false,

  fetchInvoices: async (params = {}) => {
    set({ isLoading: true });
    try {
      const data = await listInvoices(params);
      set({ invoices: data, isLoading: false });
      return { success: true };
    } catch (err) {
      set({ isLoading: false });
      return { success: false, error: "Couldn't load invoices." };
    }
  },

  fetchInvoice: async (id) => {
    set({ isLoadingCurrent: true, currentInvoice: null });
    try {
      const data = await getInvoice(id);
      set({ currentInvoice: data, isLoadingCurrent: false });
      return { success: true, invoice: data };
    } catch (err) {
      set({ isLoadingCurrent: false });
      return { success: false, error: "Couldn't load invoice details." };
    }
  },
}));

export default useInvoiceStore;