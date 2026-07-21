import { Navigate } from "react-router-dom";
import useAuthStore from "../store/authStore";

function AdminRoute({ children }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const isLoading = useAuthStore((state) => state.isLoading);
  const user = useAuthStore((state) => state.user);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-950 text-gray-400 text-sm">
        Checking session...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (user?.role !== "ADMIN") {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}

export default AdminRoute;