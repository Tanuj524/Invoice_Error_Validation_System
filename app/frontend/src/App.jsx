import { useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import Register from "./pages/Register";
import Login from "./pages/Login";
import useAuthStore from "./store/authStore";
import ProtectedRoute from "./components/ProtectedRoute";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";

function Placeholder({ label }) {
  return (
    <div className="min-h-screen flex items-center justify-center text-gray-500">
      {label} — coming soon
    </div>
  );
}

function App() {
  const checkAuth = useAuthStore((state) => state.checkAuth);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return (
    <>
      <Toaster position="top-center" />
      <Routes>
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />

        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/dashboard" element={<ProtectedRoute><Placeholder label="Dashboard" /></ProtectedRoute>} />

        <Route path="/" element={<Navigate to="/register" replace />} />
        <Route path="*" element={<Navigate to="/register" replace />} />
      </Routes>
    </>
  );
}

export default App;