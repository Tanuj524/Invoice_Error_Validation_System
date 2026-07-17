import { useState } from "react";
import { useNavigate, useSearchParams, Link } from "react-router-dom";
import toast from "react-hot-toast";
import useAuthStore from "../store/authStore";

function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");

  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const resetPassword = useAuthStore((state) => state.resetPassword);
  const isLoading = useAuthStore((state) => state.isLoading);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    if (isLoading) return;

    if (newPassword !== confirmPassword) {
      toast.error("Passwords don't match.");
      return;
    }

    const result = await resetPassword(token, newPassword);

    if (result.success) {
      toast.success("Password reset. You can log in now.");
      navigate("/login");
    } else {
      toast.error(result.error);
    }
  }

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
        <div className="w-full max-w-sm bg-white border border-gray-200 rounded-xl p-8 text-center">
          <p className="text-sm text-gray-600 mb-4">
            This reset link is missing a token. Request a new one to continue.
          </p>
          <Link to="/forgot-password" className="text-blue-600 text-sm hover:underline">
            Request a new link
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-sm bg-white border border-gray-200 rounded-xl p-8">
        <div className="flex justify-center mb-4">
          <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center">
            <span className="text-blue-600 text-lg">*</span>
          </div>
        </div>

        <h1 className="text-center text-lg font-medium text-gray-900 mb-1">
          Set a new password
        </h1>
        <p className="text-center text-sm text-gray-500 mb-6">
          Choose a new password for your account
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="newPassword" className="block text-sm text-gray-600 mb-1">
              New password
            </label>
            <input
              id="newPassword"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="At least 8 characters"
              minLength={8}
              required
              className="w-full h-9 px-3 border border-gray-300 rounded-md text-sm
                         focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm text-gray-600 mb-1">
              Confirm password
            </label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Re-enter your password"
              minLength={8}
              required
              className="w-full h-9 px-3 border border-gray-300 rounded-md text-sm
                         focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full h-9 bg-gray-900 text-white text-sm font-medium rounded-md
                       hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {isLoading ? "Resetting..." : "Reset password"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default ResetPassword;