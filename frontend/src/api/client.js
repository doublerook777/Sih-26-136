const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Universal fetch wrapper for ProcuraAI.
 * Attaches JWT token, parses JSON responses, formats errors to { detail: message },
 * and handles 401 by clearing session and redirecting to /login.
 */
export async function request(path, options = {}) {
  const token = localStorage.getItem("token");
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let url = `${BASE_URL}${path}`;
  if (options.params) {
    const queryParams = new URLSearchParams();
    Object.entries(options.params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") {
        queryParams.append(k, v);
      }
    });
    const queryString = queryParams.toString();
    if (queryString) {
      url += (url.includes("?") ? "&" : "?") + queryString;
    }
  }

  let response;
  try {
    response = await fetch(url, {
      ...options,
      headers,
    });
  } catch (networkError) {
    const err = new Error("Unable to connect to backend server");
    err.detail = "Unable to connect to backend server";
    err.status = 0;
    throw err;
  }

  if (response.status === 401) {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    if (window.location.pathname !== "/login") {
      window.location.href = "/login";
    }
    return new Promise(() => {}); // page is navigating away, never resolve
  }

  let data = null;
  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    try {
      data = await response.json();
    } catch {
      data = null;
    }
  } else {
    try {
      data = await response.text();
    } catch {
      data = null;
    }
  }

  if (!response.ok) {
    const message = (data && data.detail) || response.statusText || "Request failed";
    const err = new Error(typeof message === "string" ? message : JSON.stringify(message));
    err.status = response.status;
    err.detail = message;
    throw err;
  }

  return data;
}

export const get = (path, params) => request(path, { method: "GET", params });
export const post = (path, body) => request(path, { method: "POST", body: JSON.stringify(body) });
export const put = (path, body) => request(path, { method: "PUT", body: JSON.stringify(body) });
export const del = (path) => request(path, { method: "DELETE" });
