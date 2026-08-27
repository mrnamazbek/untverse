import { getAuth, saveAuth, clearAuth } from "./auth";
import { AuthResponse } from "@/types/api";
import {
  OAuthInitResponse,
  GoogleLoginResponse,
  TokenResponse,
  User,
  AuthErrorCode,
  LocalizedErrorMessage,
} from "@/types/auth";
import { getClientLocale, localeToLanguageTag, Locale } from "./i18n";

export class ApiError extends Error {
  code?: AuthErrorCode | string;
  status: number;
  localized?: LocalizedErrorMessage;
  details?: Record<string, unknown>;

  constructor(
    message: string,
    status: number,
    code?: AuthErrorCode | string,
    localized?: LocalizedErrorMessage,
    details?: Record<string, unknown>
  ) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.localized = localized;
    this.details = details;
  }
}
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

export async function fetchApi<T = unknown>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
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

  // Preserve locale parameter
  if (!url.searchParams.has("locale")) {
    url.searchParams.set("locale", locale);
  }

  let response = await fetch(url, {
    ...rest,
    headers: customHeaders,
    credentials: "include",
  });

  // Handle Token Refresh on 401 if refresh token is available or HttpOnly cookie is present
  if (response.status === 401 && !endpoint.includes("/auth/refresh") && !endpoint.includes("/auth/login")) {
    try {
      const refreshRes = await fetch(`${baseUrl}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(auth?.refresh_token ? { refresh_token: auth.refresh_token } : {}),
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
    const errorData = await response.json().catch(() => ({
      detail: "Ошибка сети или сервера",
    }));

    const localizedMsg =
      errorData.localized && (errorData.localized[locale] || errorData.localized.ru || errorData.localized.en);
    const message =
      localizedMsg ||
      errorData.message ||
      errorData.detail ||
      "Произошла ошибка при выполнении запроса";

    throw new ApiError(
      message,
      response.status,
      errorData.code,
      errorData.localized,
      errorData.details
    );
  }

  return response.json();
}

/**
 * Initiates Google OAuth 2.0 PKCE Authorization flow.
 * Returns authorization_url and signed JWT state.
 */
export async function initGoogleOAuth(
  locale: string = "ru",
  redirectTo: string = "/dashboard"
): Promise<OAuthInitResponse> {
  const params = new URLSearchParams({
    locale,
    redirect_to: redirectTo,
  });
  return fetchApi<OAuthInitResponse>(`/auth/oauth/google/init?${params.toString()}`, {
    requiresAuth: false,
  });
}

/**
 * Handles Google OAuth callback by exchanging authorization code and state for tokens.
 */
export async function handleGoogleCallback(
  code: string,
  state: string
): Promise<GoogleLoginResponse> {
  return fetchApi<GoogleLoginResponse>("/auth/oauth/google/callback", {
    method: "POST",
    requiresAuth: false,
    body: JSON.stringify({ code, state }),
  });
}

/**
 * Refreshes active session tokens using cookie or explicit refresh_token.
 */
export async function refreshToken(refreshTokenStr?: string): Promise<TokenResponse> {
  return fetchApi<TokenResponse>("/auth/refresh", {
    method: "POST",
    requiresAuth: false,
    body: JSON.stringify(refreshTokenStr ? { refresh_token: refreshTokenStr } : {}),
  });
}

/**
 * Logs out the current session.
 */
export async function logout(refreshTokenStr?: string): Promise<{ message: string }> {
  return fetchApi<{ message: string }>("/auth/logout", {
    method: "POST",
    requiresAuth: false,
    body: JSON.stringify(refreshTokenStr ? { refresh_token: refreshTokenStr } : {}),
  });
}

/**
 * Revokes all active sessions for the current user.
 */
export async function logoutAll(): Promise<{ message: string; revoked_sessions_count: number }> {
  return fetchApi<{ message: string; revoked_sessions_count: number }>("/auth/logout-all", {
    method: "POST",
    requiresAuth: true,
  });
}

/**
 * Sets a permanent password for the current account (e.g. for Google-only users).
 */
export async function setPassword(newPassword: string): Promise<{ message: string }> {
  return fetchApi<{ message: string }>("/auth/set-password", {
    method: "POST",
    requiresAuth: true,
    body: JSON.stringify({ new_password: newPassword }),
  });
}

/**
 * Fetches the current authenticated user's profile and accounts.
 */
export async function getCurrentUser(): Promise<User> {
  return fetchApi<User>("/auth/me", {
    requiresAuth: true,
  });
}

/**
 * Alias for getCurrentUser
 */
export async function getMe(): Promise<User> {
  return getCurrentUser();
}
