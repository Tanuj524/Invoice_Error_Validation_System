import { create } from "zustand";
import { registerUser, loginUser, getMe, forgotPassword as forgotPasswordApi, resetPassword as resetPasswordApi } from "../api/auth";

const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  register: async (username, email, password) => {
    set({ isLoading: true });
    try {
      const user = await registerUser(username, email, password);
      set({ isLoading: false });
      return { success: true, user };
    } catch (err) {
      set({ isLoading: false });
      return { success: false, error: extractError(err) };
    }
  },

  login: async (email, password) => {
    set({ isLoading: true });
    try {
      await loginUser(email, password);
      const user = await getMe(); // cookie is now set, fetch full profile
      set({ user, isAuthenticated: true, isLoading: false });
      return { success: true, user };
    } catch (err) {
      set({ isLoading: false });
      return { success: false, error: extractError(err) };
    }
  },

  checkAuth: async () => {
    set({ isLoading: true });
    try {
      const user = await getMe();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch {
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },
  forgotPassword: async (email) => {
  set({ isLoading: true });
  try {
    await forgotPasswordApi(email);
    set({ isLoading: false });
    return { success: true };
  } catch (err) {
    set({ isLoading: false });
    return { success: false, error: extractError(err) };
  }
},
// inside create((set) => ({ ... }))
resetPassword: async (token, newPassword) => {
  set({ isLoading: true });
  try {
    await resetPasswordApi(token, newPassword);
    set({ isLoading: false });
    return { success: true };
  } catch (err) {
    set({ isLoading: false });
    return { success: false, error: extractError(err) };
  }
},
}));

function extractError(err) {
  const status = err.response?.status;
  if (status === 401) return "Incorrect email or password.";
  if (status === 403) return "Your account is inactive.";
  if (status === 409) return "That email is already registered.";
  if (status === 400) return "This reset link is invalid or has expired.";
  if (status === 422) return "Please check your details and try again.";
  console.log(err)
  return "Something went wrong. Please try again.";
}

export default useAuthStore;