const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

async function handle(response) {
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const message = body.detail || Object.values(body)[0] || `Request failed (${response.status})`;
    throw new Error(Array.isArray(message) ? message[0] : message);
  }
  return response.json();
}

export function register(username, email, password, role) {
  return fetch(`${API_BASE_URL}/auth/register/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password, role }),
  }).then(handle);
}

export function login(username, password) {
  return fetch(`${API_BASE_URL}/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  }).then(handle);
}

export function logout(accessToken, refreshToken) {
  return fetch(`${API_BASE_URL}/auth/logout/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ refresh: refreshToken }),
  }).then(handle);
}

export function getMe(accessToken) {
  return fetch(`${API_BASE_URL}/auth/me/`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  }).then(handle);
}
