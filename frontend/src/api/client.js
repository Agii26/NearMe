const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

async function request(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const message = body.detail || `Request failed with status ${response.status}`;
    throw new Error(message);
  }
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
