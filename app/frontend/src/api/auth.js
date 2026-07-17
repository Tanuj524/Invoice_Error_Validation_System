import apiClient from "./client.js";

export async function registerUser(username, email, password) {
  const response = await apiClient.post("/auth/register", {
    username,
    email,
    password,
  });
  return response.data;
}

export async function loginUser(email, password) {
  const params = new URLSearchParams();
  params.append("username", email);
  params.append("password", password);

  const response = await apiClient.post("/auth/login", params, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return response.data; // { access_token, token_type }
}

export async function getMe() {
  const response = await apiClient.get("/auth/me");
  return response.data; // UserOut
}

export async function forgotPassword(email) {
  const response = await apiClient.post("/auth/forgot-password", { email });
  return response.data;
}

export async function resetPassword(token, newPassword) {
  const response = await apiClient.post("/auth/reset-password", {
    token,
    new_password: newPassword,
  });
  return response.data;
}