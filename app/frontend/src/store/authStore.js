import { create } from "zustand";
import { registerUser } from "../api/auth";

const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  register: async (username, email, password) => {
  set({ isLoading: true, error: null });
  try {
    const user = await registerUser(username, email, password);
    set({ isLoading: false });
    return { success: true, user };
  } catch (err) {
    const status = err.response?.status;
    let message = "Registration failed. Please try again.";

    if (status === 409) {
      message = "That email is already registered.";
    } else if (status === 422) {
      message = "Please check your username, email, and password.";
    }

    set({ isLoading: false, error: message });
    return { success: false, error: message };
  }
},
}));

export default useAuthStore;