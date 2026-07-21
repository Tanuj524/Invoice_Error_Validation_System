import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import useAdminStore from "../store/adminStore";
import useAuthStore from "../store/authStore";
import Navbar from "../components/Navbar";
import ConfirmDialog from "../components/ConfirmDialog";

function formatDate(value) {
  return new Date(value).toLocaleDateString("en-IN", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function AdminPanel() {
  const currentUser = useAuthStore((state) => state.user);
  const users = useAdminStore((state) => state.users);
  const isLoading = useAdminStore((state) => state.isLoading);
  const fetchUsers = useAdminStore((state) => state.fetchUsers);
  const changeRole = useAdminStore((state) => state.changeRole);
  const toggleStatus = useAdminStore((state) => state.toggleStatus);
  const removeUser = useAdminStore((state) => state.removeUser);

  const [deleteTarget, setDeleteTarget] = useState(null);

  useEffect(() => {
    fetchUsers().then((result) => {
      if (!result.success) toast.error(result.error);
    });
  }, [fetchUsers]);

  async function handleRoleChange(userId, newRole) {
    const result = await changeRole(userId, newRole);
    if (result.success) {
      toast.success("Role updated.");
    } else {
      toast.error(result.error);
    }
  }

  async function handleStatusToggle(userId, currentActive) {
    const result = await toggleStatus(userId, !currentActive);
    if (result.success) {
      toast.success(!currentActive ? "User activated." : "User deactivated.");
    } else {
      toast.error(result.error);
    }
  }

  async function confirmDelete() {
    if (!deleteTarget) return;

    const userId = deleteTarget.id;
    const username = deleteTarget.username;

    setDeleteTarget(null); // close dialog immediately, before the async call
    const result = await removeUser(userId);

    if (result.success) {
      toast.success(`${username} deleted.`);
    } else {
      toast.error(result.error);
    }
  }

  return (
    <div className="min-h-screen bg-gray-950">
      <Navbar />
      <div className="px-6 py-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6">
            <h1 className="text-xl font-medium text-gray-100">Users</h1>
            <p className="text-sm text-gray-400">Manage roles and account access</p>
          </div>

          {isLoading ? (
            <p className="text-sm text-gray-400">Loading users...</p>
          ) : (
            <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-900 text-left text-gray-400">
                    <th className="font-medium px-4 py-2">Username</th>
                    <th className="font-medium px-4 py-2">Email</th>
                    <th className="font-medium px-4 py-2">Role</th>
                    <th className="font-medium px-4 py-2">Status</th>
                    <th className="font-medium px-4 py-2">Joined</th>
                    <th className="font-medium px-4 py-2 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => {
                    const isSelf = u.id === currentUser?.id;
                    return (
                      <tr key={u.id} className="border-t border-gray-800">
                        <td className="px-4 py-2 text-gray-100">{u.username}</td>
                        <td className="px-4 py-2 text-gray-300">{u.email}</td>
                        <td className="px-4 py-2">
                          <select
                            value={u.role}
                            disabled={isSelf}
                            onChange={(e) => handleRoleChange(u.id, e.target.value)}
                            className="bg-gray-800 border border-gray-700 rounded-md text-sm text-gray-100 px-2 py-1
                                       disabled:opacity-40 disabled:cursor-not-allowed"
                          >
                            <option value="USER">User</option>
                            <option value="ADMIN">Admin</option>
                          </select>
                        </td>
                        <td className="px-4 py-2">
                          <button
                            disabled={isSelf}
                            onClick={() => handleStatusToggle(u.id, u.is_active)}
                            className={`relative inline-flex h-5 w-9 items-center rounded-full transition
                                        disabled:opacity-40 disabled:cursor-not-allowed
                                        ${u.is_active ? "bg-green-700" : "bg-gray-700"}`}
                          >
                            <span
                              className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition
                                          ${u.is_active ? "translate-x-4.5" : "translate-x-1"}`}
                            />
                          </button>
                        </td>
                        <td className="px-4 py-2 text-gray-400">{formatDate(u.created_at)}</td>
                        <td className="px-4 py-2 text-right">
                          <button
                            disabled={isSelf}
                            onClick={() => setDeleteTarget(u)}
                            className="text-sm text-red-400 hover:text-red-300 disabled:opacity-40 disabled:cursor-not-allowed transition"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete user"
        message={deleteTarget ? `This permanently deletes ${deleteTarget.username}'s account. This can't be undone.` : ""}
        confirmLabel="Delete"
        danger
        onConfirm={confirmDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}

export default AdminPanel;