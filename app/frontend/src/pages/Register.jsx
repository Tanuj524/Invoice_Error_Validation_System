import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import toast from "react-hot-toast";
import useAuthStore from "../store/authStore";

function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const register = useAuthStore((state) => state.register);
  const isLoading = useAuthStore((state) => state.isLoading);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    const result = await register(username, email, password);

    if (result.success) {
      toast.success("Account created. Redirecting to login...");
      setTimeout(() => navigate("/login"), 1500);
    } else {
      toast.error(result.error);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950 px-4">
      <div className="w-full max-w-sm bg-gray-900 border border-gray-800 rounded-xl p-8">
        <div className="flex justify-center mb-4">
          <div className="w-10 h-10 rounded-full bg-blue-950 flex items-center justify-center">
            <span className="text-blue-400 text-lg">+</span>
          </div>
        </div>

        <h1 className="text-center text-lg font-medium text-gray-100 mb-1">
          Create your account
        </h1>
        <p className="text-center text-sm text-gray-400 mb-6">
          Start validating invoices in minutes
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="username" className="block text-sm text-gray-400 mb-1">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="jane_doe"
              required
              className="w-full h-9 px-3 bg-gray-800 border border-gray-700 rounded-md text-sm text-gray-100
                         placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-sm text-gray-400 mb-1">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@company.com"
              required
              className="w-full h-9 px-3 bg-gray-800 border border-gray-700 rounded-md text-sm text-gray-100
                         placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm text-gray-400 mb-1">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 8 characters"
              minLength={8}
              required
              className="w-full h-9 px-3 bg-gray-800 border border-gray-700 rounded-md text-sm text-gray-100
                         placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-1">Use 8 or more characters.</p>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full h-9 bg-white text-gray-900 text-sm font-medium rounded-md
                       hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {isLoading ? "Creating account..." : "Create account"}
          </button>
        </form>

        <p className="text-center text-sm text-gray-400 mt-5">
          Already have an account?{" "}
          <Link to="/login" className="text-blue-400 hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}

export default Register;