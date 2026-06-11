const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function apiRequest(path, options = {}) {
  const token = localStorage.getItem("drinkoo_token");
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Request failed");
  }

  return response.json();
}

export async function login(username, password) {
  return apiRequest("/auth/token", {
    method: "POST",
    body: JSON.stringify({ username, password })
  });
}

export function getStates() {
  return apiRequest("/states/");
}

export function getSkus() {
  return apiRequest("/skus/");
}

export function getCustomers() {
  return apiRequest("/customers/");
}

export function ingestSales(sales) {
  return apiRequest("/sales/ingest", {
    method: "POST",
    body: JSON.stringify({ sales })
  });
}

export function createShipment(payload) {
  return apiRequest("/shipments/", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getSalesByState() {
  return apiRequest("/analytics/sales_by_state");
}

export function getSkuPerformance() {
  return apiRequest("/analytics/sku_performance");
}

export function sendChatMessage(message, sessionId, options = {}) {
  const body = { message, session_id: sessionId };
  if (options.debugSql) {
    body.debug_sql = true;
  }

  const headers = {};
  if (options.debugToken) {
    headers["X-Chatbot-Debug-Token"] = options.debugToken;
  }

  return apiRequest("/chatbot/message", {
    method: "POST",
    headers,
    body: JSON.stringify(body)
  });
}

export async function postTelemetryEvent(payload) {
  return apiRequest("/telemetry/events", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function checkBackendHealth() {
  const response = await fetch(`${API_BASE_URL}/`, {
    method: "GET",
    headers: { "Content-Type": "application/json" }
  });
  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}`);
  }
  return response.json();
}

export async function getServiceStatus() {
  const response = await fetch(`${API_BASE_URL}/status`, {
    method: "GET",
    headers: { "Content-Type": "application/json" }
  });
  if (!response.ok) {
    throw new Error(`Status check failed with status ${response.status}`);
  }
  return response.json();
}
