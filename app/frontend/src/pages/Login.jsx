import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import toast from "react-hot-toast";
import useAuthStore from "../store/authStore";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const login = useAuthStore((state) => state.login);
  const isLoading = useAuthStore((state) => state.isLoading);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    const result = await login(email, password);

    if (result.success) {
      toast.success("Welcome back.");
      navigate("/dashboard");
    } else {
      toast.error(result.error);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950 px-4">
  <div className="w-full max-w-sm bg-gray-900 border border-gray-800 rounded-xl p-8">
    <div className="flex justify-center mb-4">
      <div className="w-10 h-10 rounded-full bg-blue-950 flex items-center justify-center">
        <span className="text-blue-400 text-lg">→</span>
      </div>
    </div>

    <h1 className="text-center text-lg font-medium text-gray-100 mb-1">Welcome back</h1>
    <p className="text-center text-sm text-gray-400 mb-6">Log in to your account</p>

    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="email" className="block text-sm text-gray-400 mb-1">Email</label>
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
        <div className="flex items-center justify-between mb-1">
          <label htmlFor="password" className="block text-sm text-gray-400">Password</label>
          <Link to="/forgot-password" className="text-xs text-blue-400 hover:underline">
            Forgot password?
          </Link>
        </div>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Enter your password"
          required
          className="w-full h-9 px-3 bg-gray-800 border border-gray-700 rounded-md text-sm text-gray-100
                     placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full h-9 bg-white text-gray-900 text-sm font-medium rounded-md
                   hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition"
      >
        {isLoading ? "Logging in..." : "Log in"}
      </button>
    </form>

    <p className="text-center text-sm text-gray-400 mt-5">
      Don't have an account?{" "}
      <Link to="/register" className="text-blue-400 hover:underline">Register</Link>
    </p>
  </div>
</div>
  );
}

export default Login;