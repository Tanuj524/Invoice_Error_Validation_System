import { useState } from "react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import useAuthStore from "../store/authStore";

function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const forgotPassword = useAuthStore((state) => state.forgotPassword);
  const isLoading = useAuthStore((state) => state.isLoading);

  async function handleSubmit(e) {
    e.preventDefault();
    const result = await forgotPassword(email);

    if (result.success) {
      setSubmitted(true);
      toast.success("If that email exists, we've sent a reset link.");
    } else {
      // network/server errors only — not "email not found", since we never say that
      toast.error(result.error);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-sm bg-white border border-gray-200 rounded-xl p-8">
        <div className="flex justify-center mb-4">
          <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center">
            <span className="text-blue-600 text-lg">?</span>
          </div>
        </div>

        <h1 className="text-center text-lg font-medium text-gray-900 mb-1">
          Forgot your password?
        </h1>
        <p className="text-center text-sm text-gray-500 mb-6">
          Enter your email and we'll send you a reset link
        </p>

        {submitted ? (
          <p className="text-center text-sm text-gray-600">
            Check your inbox for a reset link. It expires in 30 minutes.
          </p>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm text-gray-600 mb-1">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@company.com"
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
              {isLoading ? "Sending..." : "Send reset link"}
            </button>
          </form>
        )}

        <p className="text-center text-sm text-gray-500 mt-5">
          Remembered your password?{" "}
          <Link to="/login" className="text-blue-600 hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}

export default ForgotPassword;