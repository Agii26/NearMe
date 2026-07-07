const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

async function request(path, { accessToken, method = "GET", body } = {}) {
  const headers = {};
  if (body) headers["Content-Type"] = "application/json";
  if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!response.ok) {
    const responseBody = await response.json().catch(() => ({}));
    const message = responseBody.detail || `Request failed with status ${response.status}`;
    throw new Error(message);
  }
  if (response.status === 204 || response.status === 205) return null;
  return response.json();
}

export function getCategories() {
  return request("/categories/");
}

export function searchBusinesses({ lat, lng, radius, category, q }) {
  const params = new URLSearchParams({ lat, lng });
  if (radius) params.set("radius", radius);
  if (category && category !== "all") params.set("category", category);
  if (q) params.set("q", q);
  return request(`/businesses/search?${params.toString()}`);
}

export function getBusinessDetail(id) {
  return request(`/businesses/${id}/`);
}

export function claimBusiness(id, accessToken) {
  return request(`/businesses/${id}/claim/`, { method: "POST", accessToken });
}

export function updateBusiness(id, data, accessToken) {
  return request(`/businesses/${id}/`, { method: "PATCH", body: data, accessToken });
}

export function getMyBusinesses(accessToken) {
  return request("/businesses/mine/", { accessToken });
}

export function getMyClaims(accessToken) {
  return request("/businesses/claims/mine/", { accessToken });
}

export async function uploadBusinessPhoto(id, file, accessToken) {
  const formData = new FormData();
  formData.append("image", file);
  const response = await fetch(`${API_BASE_URL}/businesses/${id}/photos/`, {
    method: "POST",
    headers: { Authorization: `Bearer ${accessToken}` },
    body: formData,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Upload failed with status ${response.status}`);
  }
  return response.json();
}
