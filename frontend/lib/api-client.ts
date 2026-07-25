/**
 * Centralized API client using standard fetch.
 * Handles base URL, headers, error parsing, and JWT auth.
 */

interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | undefined>;
}

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("ezoo_token");
}

async function request<T>(url: string, options: RequestOptions = {}): Promise<T | any> {
  const { params, headers: customHeaders, ...rest } = options;

  let targetUrl = url;
  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, value.toString());
      }
    });
    const queryString = searchParams.toString();
    if (queryString) {
      targetUrl += (targetUrl.includes("?") ? "&" : "?") + queryString;
    }
  }

  const token = getToken();
  const authHeaders: Record<string, string> = {};
  if (token) {
    authHeaders["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(targetUrl, {
    headers: {
      "Content-Type": "application/json",
      ...authHeaders,
      ...customHeaders,
    },
    ...rest,
  });

  if (!response.ok) {
    if (response.status === 401 || response.status === 403) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("ezoo_token");
        window.location.href = "/login";
      }
    }
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || `Request failed with status ${response.status}`);
  }

  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    return response.json();
  }

  return response.text() as any;
}

export const api = {
  get: <T>(url: string, options?: RequestOptions) => request<T>(url, { ...options, method: "GET" }),
  post: <T>(url: string, body?: any, options?: RequestOptions) => request<T>(url, { ...options, method: "POST", body: JSON.stringify(body) }),
  patch: <T>(url: string, body?: any, options?: RequestOptions) => request<T>(url, { ...options, method: "PATCH", body: JSON.stringify(body) }),
  put: <T>(url: string, body?: any, options?: RequestOptions) => request<T>(url, { ...options, method: "PUT", body: JSON.stringify(body) }),
  delete: <T>(url: string, options?: RequestOptions) => request<T>(url, { ...options, method: "DELETE" }),
};
