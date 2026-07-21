import { useState, useRef, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import toast from "react-hot-toast";
import useAuthStore from "../store/authStore";

function Navbar() {
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const navigate = useNavigate();

  const [open, setOpen] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  async function handleLogout() {
    setOpen(false);
    await logout();
    toast.success("Logged out.");
    navigate("/login");
  }

  const initials = user?.username
    ? user.username.slice(0, 2).toUpperCase()
    : "?";

  return (
    <div className="border-b border-gray-800 bg-gray-900 px-6 h-14 flex items-center justify-between">
      <Link to="/dashboard" className="flex items-center gap-2">
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          className="text-blue-400"
        >
          <path d="M9 11l3 3L22 4" />
          <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
        </svg>
        <span className="text-sm font-medium text-gray-100">Invoice Validator</span>
      </Link>

      <div className="flex items-center gap-4">
        {user?.role === "ADMIN" && (
  <Link to="/admin" className="text-sm text-gray-400 hover:text-gray-100 transition">
    Admin
  </Link>
)}

        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setOpen((v) => !v)}
            className="flex items-center gap-2 pl-1 pr-2 py-1 rounded-md border border-gray-800 hover:border-gray-700 transition"
          >
            <div className="w-6 h-6 rounded-full bg-blue-950 flex items-center justify-center text-[11px] font-medium text-blue-400">
              {initials}
            </div>
            <span className="text-sm text-gray-200">{user?.username ?? "Account"}</span>
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className="text-gray-500"
            >
              <path d="M6 9l6 6 6-6" />
            </svg>
          </button>

          {open && (
            <div className="absolute right-0 mt-1 w-40 bg-gray-900 border border-gray-800 rounded-md shadow-lg py-1 z-10">
              <button
                onClick={handleLogout}
                className="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-gray-800 transition"
              >
                Log out
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Navbar;