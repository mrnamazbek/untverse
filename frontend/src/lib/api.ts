import { getAuth, saveAuth, clearAuth } from "./auth";
import { AuthResponse } from "@/types/api";
import { getClientLocale, localeToLanguageTag } from "./i18n";

export function getApiBaseUrl(): string {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  if (typeof window !== "undefined") {
    return `${window.location.origin}/api/v1`;
  }
  return "http://127.0.0.1:8000/api/v1";
}

interface RequestOptions extends RequestInit {
  requiresAuth?: boolean;
}

export async function fetchApi<T = unknown>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { requiresAuth = true, headers = {}, ...rest } = options;
  const auth = getAuth();
  const locale = getClientLocale();
  const baseUrl = getApiBaseUrl();

  const customHeaders: Record<string, string> = {
    "Content-Type": "application/json",
    "Accept-Language": localeToLanguageTag(locale),
    ...(headers as Record<string, string>),
  };

  if (requiresAuth && auth?.access_token) {
    customHeaders["Authorization"] = `Bearer ${auth.access_token}`;
  }

  const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  const fullUrl = endpoint.startsWith("http") ? endpoint : `${baseUrl}${cleanEndpoint}`;
  const url = new URL(fullUrl);
  // Locale is carried for every content endpoint. Endpoints that do not use it
  // safely ignore the query parameter; localized endpoints receive one source
  // of truth instead of each page assembling its own URL.
  if (!url.searchParams.has("locale")) {
    url.searchParams.set("locale", locale);
  }

  let response = await fetch(url, {
    ...rest,
    headers: customHeaders,
    credentials: "include",
  });

  // Handle Token Refresh on 401 if refresh token is available
  if (response.status === 401 && auth?.refresh_token && !endpoint.includes("/auth/refresh")) {
    try {
      const refreshRes = await fetch(`${baseUrl}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: auth.refresh_token }),
      });

      if (refreshRes.ok) {
        const newAuth: AuthResponse = await refreshRes.json();
        saveAuth(newAuth);
        customHeaders["Authorization"] = `Bearer ${newAuth.access_token}`;
        response = await fetch(url, {
          ...rest,
          headers: customHeaders,
          credentials: "include",
        });
      } else {
        clearAuth();
      }
    } catch {
      clearAuth();
    }
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Ошибка сети или сервера" }));
    const message = errorData.detail || "Произошла ошибка при выполнении запроса";
    throw new Error(message);
  }

  return response.json();
}
