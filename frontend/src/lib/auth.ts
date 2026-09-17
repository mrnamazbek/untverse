import { useSyncExternalStore } from "react";
import { AuthResponse } from "@/types/api";
import { User, TokenResponse } from "@/types/auth";

export const AUTH_KEY = "unt_auth_session";
export const USER_KEY = "unt_user_profile";
export const AUTH_CHANGE_EVENT = "unt_auth_change";

let cachedRawAuth: string | null = null;
let cachedParsedAuth: AuthResponse | null = null;

function dispatchAuthChange() {
  if (typeof window !== "undefined") {
    cachedRawAuth = localStorage.getItem(AUTH_KEY);
    try {
      cachedParsedAuth = cachedRawAuth ? JSON.parse(cachedRawAuth) : null;
    } catch {
      cachedParsedAuth = null;
    }
    window.dispatchEvent(new Event(AUTH_CHANGE_EVENT));
  }
}

export function saveAuth(data: AuthResponse): void {
  if (typeof window !== "undefined") {
    const raw = JSON.stringify(data);
    localStorage.setItem(AUTH_KEY, raw);
    cachedRawAuth = raw;
    cachedParsedAuth = data;
    dispatchAuthChange();
  }
}

export function getAuth(): AuthResponse | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(AUTH_KEY);
  if (raw === cachedRawAuth) return cachedParsedAuth;
  cachedRawAuth = raw;
  if (!raw) {
    cachedParsedAuth = null;
    return null;
  }
  try {
    cachedParsedAuth = JSON.parse(raw);
    return cachedParsedAuth;
  } catch {
    cachedParsedAuth = null;
    return null;
  }
}

function subscribeAuth(callback: () => void) {
  if (typeof window === "undefined") return () => {};
  window.addEventListener(AUTH_CHANGE_EVENT, callback);
  window.addEventListener("storage", callback);
  return () => {
    window.removeEventListener(AUTH_CHANGE_EVENT, callback);
    window.removeEventListener("storage", callback);
  };
}

export function useAuthSession(): AuthResponse | null {
  return useSyncExternalStore(subscribeAuth, getAuth, () => null);
}

export function clearAuth(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem(AUTH_KEY);
    localStorage.removeItem(USER_KEY);
    dispatchAuthChange();
  }
}

export function saveUser(user: User): void {
  if (typeof window !== "undefined") {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    dispatchAuthChange();
  }
}

export function getUser(): User | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function clearUser(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem(USER_KEY);
    dispatchAuthChange();
  }
}

export function updateLocalProfile(patch: Partial<AuthResponse>): void {
  const current = getAuth();
  if (current) {
    saveAuth({ ...current, ...patch });
  }
}

/**
 * Transforms a full User profile into backwards-compatible AuthResponse session.
 */
export function userToAuthSession(user: User, existingAuth?: TokenResponse | null): AuthResponse {
  return {
    access_token: existingAuth?.access_token || "",
    refresh_token: existingAuth?.refresh_token || "",
    token_type: existingAuth?.token_type || "bearer",
    expires_in: existingAuth?.expires_in || 900,
    user_id: user.id,
    email: user.email,
    role: user.role,
    display_name: user.profile?.display_name || user.email.split("@")[0],
    current_level: user.profile?.current_level ?? 1,
    total_xp: user.profile?.total_xp ?? 0,
    rank_title: user.profile?.rank_title || "Новичок Информатики",
    streak_count: user.profile?.streak_count ?? 0,
    avatar_url: user.profile?.avatar_url ?? null,
    redirect_to: existingAuth?.redirect_to,
  };
}

export function isAuthenticated(): boolean {
  return !!getAuth()?.access_token;
}

export function getAccessToken(): string | null {
  return getAuth()?.access_token || null;
}

export function getRefreshToken(): string | null {
  return getAuth()?.refresh_token || null;
}

/**
 * Sanitizes redirect target URLs to prevent Open Redirect attacks.
 * Only allows relative paths starting with a single '/' and rejects protocol-relative ('//') or external URLs.
 */
export function sanitizeRedirectUrl(url?: string | null): string {
  if (!url || typeof url !== "string") return "/dashboard";
  const trimmed = url.trim();
  if (
    !trimmed.startsWith("/") ||
    trimmed.startsWith("//") ||
    trimmed.includes("://") ||
    trimmed.toLowerCase().startsWith("javascript:")
  ) {
    return "/dashboard";
  }
  return trimmed;
}
