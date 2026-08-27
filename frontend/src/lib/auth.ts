import { AuthResponse } from "@/types/api";

const AUTH_KEY = "unt_auth_session";

export function saveAuth(data: AuthResponse) {
  if (typeof window !== "undefined") {
    localStorage.setItem(AUTH_KEY, JSON.stringify(data));
  }
}

export function getAuth(): AuthResponse | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(AUTH_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function clearAuth() {
  if (typeof window !== "undefined") {
    localStorage.removeItem(AUTH_KEY);
  }
}

export function updateLocalProfile(patch: Partial<AuthResponse>) {
  const current = getAuth();
  if (current) {
    saveAuth({ ...current, ...patch });
  }
}
