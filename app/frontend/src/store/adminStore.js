import { create } from "zustand";
import { listUsers, updateUserRole, updateUserStatus, deleteUser } from "../api/admin";

const useAdminStore = create((set, get) => ({
  users: [],
  isLoading: false,

  fetchUsers: async () => {
    set({ isLoading: true });
    try {
      const data = await listUsers({ limit: 200 });
      set({ users: data, isLoading: false });
      return { success: true };
    } catch (err) {
      set({ isLoading: false });
      return { success: false, error: "Couldn't load users." };
    }
  },

  changeRole: async (userId, role) => {
    try {
      const updated = await updateUserRole(userId, role);
      set({ users: get().users.map((u) => (u.id === userId ? updated : u)) });
      return { success: true };
    } catch (err) {
      return { success: false, error: err.response?.data?.detail || "Couldn't update role." };
    }
  },

  toggleStatus: async (userId, isActive) => {
    try {
      const updated = await updateUserStatus(userId, isActive);
      set({ users: get().users.map((u) => (u.id === userId ? updated : u)) });
      return { success: true };
    } catch (err) {
      return { success: false, error: err.response?.data?.detail || "Couldn't update status." };
    }
  },

  removeUser: async (userId) => {
    try {
      await deleteUser(userId);
      set({ users: get().users.filter((u) => u.id !== userId) });
      return { success: true };
    } catch (err) {
      return { success: false, error: err.response?.data?.detail || "Couldn't delete user." };
    }
  },
}));

export default useAdminStore;