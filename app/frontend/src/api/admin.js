import apiClient from "./client";

export async function listUsers({ skip = 0, limit = 50 } = {}) {
  const response = await apiClient.get("/admin/users", { params: { skip, limit } });
  return response.data;
}

export async function updateUserRole(userId, role) {
  const response = await apiClient.patch(`/admin/users/${userId}/role`, { role });
  return response.data;
}

export async function updateUserStatus(userId, isActive) {
  const response = await apiClient.patch(`/admin/users/${userId}/status`, { is_active: isActive });
  return response.data;
}

export async function deleteUser(userId) {
  await apiClient.delete(`/admin/users/${userId}`);
}