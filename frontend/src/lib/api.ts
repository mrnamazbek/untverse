import { getAuth, saveAuth, clearAuth } from "./auth";
import { AuthResponse } from "@/types/api";
import { getClientLocale, localeToLanguageTag } from "./i18n";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface RequestOptions extends RequestInit {
  requiresAuth?: boolean;
}

export async function fetchApi<T = unknown>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { requiresAuth = true, headers = {}, ...rest } = options;
  const auth = getAuth();
  const locale = getClientLocale();

  const customHeaders: Record<string, string> = {
    "Content-Type": "application/json",
    "Accept-Language": localeToLanguageTag(locale),
    ...(headers as Record<string, string>),
  };

  if (requiresAuth && auth?.access_token) {
    customHeaders["Authorization"] = `Bearer ${auth.access_token}`;
  }

  const url = new URL(endpoint.startsWith("http") ? endpoint : `${API_BASE_URL}${endpoint}`);
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
      const refreshRes = await fetch(`${API_BASE_URL}/auth/refresh`, {
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
