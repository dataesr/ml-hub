const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api"

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE"

async function request<T>(method: HttpMethod, path: string, body?: any, options: RequestInit = {}): Promise<T> {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  }

  // const token = localStorage.getItem("access_token")
  // if (token) headers["Authorization"] = `Bearer ${token}`

  const response = await fetch(`${API_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
    ...options,
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(`HTTP ${response.status}: ${text}`)
  }

  try {
    return (await response.json()) as T
  } catch {
    return undefined as T
  }
}

export const api = {
  get: <T>(path: string, options?: RequestInit) => request<T>("GET", path, undefined, options),
  post: <T>(path: string, body?: any, options?: RequestInit) => request<T>("POST", path, body, options),
  put: <T>(path: string, body?: any, options?: RequestInit) => request<T>("PUT", path, body, options),
  patch: <T>(path: string, body?: any, options?: RequestInit) => request<T>("PATCH", path, body, options),
  delete: <T>(path: string, options?: RequestInit) => request<T>("DELETE", path, undefined, options),
}
