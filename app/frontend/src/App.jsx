import { Routes, Route, Navigate } from "react-router-dom";
import {Toaster} from "react-hot-toast";
import Register from "./pages/Register";


function Placeholder({ label }) {
  return (
    <div className="min-h-screen flex items-center justify-center text-gray-500">
      {label} — coming soon
    </div>
  );
}


function App() {
  return (
    <>
      <Toaster position="top-center" />
      <Routes>
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Placeholder label="Login" />} />
        <Route path="/forgot-password" element={<Placeholder label="Forgot password" />} />
        <Route path="/reset-password" element={<Placeholder label="Reset password" />} />

        {/* default: send root to register for now, until we have a dashboard */}
        <Route path="/" element={<Navigate to="/register" replace />} />

        {/* catch-all */}
        <Route path="*" element={<Navigate to="/register" replace />} />
      </Routes>
    </>
  );
}
  
export default App
