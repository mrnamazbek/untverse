"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useMemo,
  ReactNode,
} from "react";
import {
  User,
  TokenResponse,
  GoogleLoginResponse,
  OAuthInitResponse,
} from "@/types/auth";
import { AuthResponse } from "@/types/api";
import {
  getAuth,
  saveAuth,
  clearAuth,
  getUser,
  saveUser,
  clearUser,
  updateLocalProfile as updateLocalProfileStorage,
  userToAuthSession,
  AUTH_CHANGE_EVENT,
} from "@/lib/auth";
import {
  fetchApi,
  initGoogleOAuth as initGoogleOAuthApi,
  handleGoogleCallback as handleGoogleCallbackApi,
  refreshToken as refreshTokenApi,
  logout as logoutApi,
  logoutAll as logoutAllApi,
  setPassword as setPasswordApi,
  getCurrentUser as getCurrentUserApi,
} from "@/lib/api";
import { getClientLocale, Locale } from "@/lib/i18n";

export interface AuthContextType {
  user: User | null;
  session: TokenResponse | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  initGoogleOAuth: (locale?: string, redirectTo?: string) => Promise<OAuthInitResponse>;
  handleGoogleCallback: (code: string, state: string) => Promise<GoogleLoginResponse>;
  refreshToken: () => Promise<TokenResponse | null>;
  logout: () => Promise<void>;
  logoutAll: () => Promise<void>;
  setPassword: (newPassword: string) => Promise<{ message: string }>;
  getCurrentUser: () => Promise<User | null>;
  getMe: () => Promise<User | null>;
  login: (credentials: { email: string; password: string }) => Promise<TokenResponse>;
  register: (data: {
    display_name: string;
    email: string;
    password: string;
    role?: string;
  }) => Promise<TokenResponse>;
  updateLocalProfile: (patch: Partial<TokenResponse>) => void;
  refreshUserState: () => Promise<User | null>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [session, setSession] = useState<TokenResponse | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Sync state from storage
  const syncFromStorage = useCallback(() => {
    const storedAuth = getAuth();
    const storedUser = getUser();
    setSession(storedAuth);
    setUser(storedUser);
  }, []);

  const refreshUserState = useCallback(async (): Promise<User | null> => {
    try {
      const currentUser = await getCurrentUserApi();
      setUser(currentUser);
      saveUser(currentUser);

      // Keep session summary updated with latest profile stats
      const currentSession = getAuth();
      const syncedSession = userToAuthSession(currentUser, currentSession);
      saveAuth(syncedSession);
      setSession(syncedSession);

      return currentUser;
    } catch {
      return null;
    }
  }, []);

  // Initial authentication check on load
  useEffect(() => {
    const initAuth = async () => {
      syncFromStorage();
      const currentAuth = getAuth();
      if (currentAuth?.access_token) {
        await refreshUserState();
      }
      setIsLoading(false);
    };

    initAuth();

    const handleAuthChange = () => syncFromStorage();
    window.addEventListener(AUTH_CHANGE_EVENT, handleAuthChange);
    window.addEventListener("storage", handleAuthChange);

    return () => {
      window.removeEventListener(AUTH_CHANGE_EVENT, handleAuthChange);
      window.removeEventListener("storage", handleAuthChange);
    };
  }, [syncFromStorage, refreshUserState]);

  const initGoogleOAuth = useCallback(
    async (locale?: string, redirectTo: string = "/dashboard"): Promise<OAuthInitResponse> => {
      const targetLocale = locale || getClientLocale() || "ru";
      return initGoogleOAuthApi(targetLocale, redirectTo);
    },
    []
  );

  const handleGoogleCallback = useCallback(
    async (code: string, state: string): Promise<GoogleLoginResponse> => {
      setIsLoading(true);
      try {
        const data = await handleGoogleCallbackApi(code, state);
        saveAuth(data);
        setSession(data);
        await refreshUserState();
        return data;
      } finally {
        setIsLoading(false);
      }
    },
    [refreshUserState]
  );

  const refreshToken = useCallback(async (): Promise<TokenResponse | null> => {
    try {
      const currentAuth = getAuth();
      const newAuth = await refreshTokenApi(currentAuth?.refresh_token);
      saveAuth(newAuth);
      setSession(newAuth);
      return newAuth;
    } catch {
      clearAuth();
      setSession(null);
      setUser(null);
      return null;
    }
  }, []);

  const logout = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    try {
      const currentAuth = getAuth();
      await logoutApi(currentAuth?.refresh_token).catch(() => {});
    } finally {
      clearAuth();
      setSession(null);
      setUser(null);
      setIsLoading(false);
    }
  }, []);

  const logoutAll = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    try {
      await logoutAllApi().catch(() => {});
    } finally {
      clearAuth();
      setSession(null);
      setUser(null);
      setIsLoading(false);
    }
  }, []);

  const setPassword = useCallback(async (newPassword: string): Promise<{ message: string }> => {
    return setPasswordApi(newPassword);
  }, []);

  const getCurrentUser = useCallback(async (): Promise<User | null> => {
    return refreshUserState();
  }, [refreshUserState]);

  const getMe = useCallback(async (): Promise<User | null> => {
    return refreshUserState();
  }, [refreshUserState]);

  const login = useCallback(
    async (credentials: { email: string; password: string }): Promise<TokenResponse> => {
      setIsLoading(true);
      try {
        const data = await fetchApi<AuthResponse>("/auth/login", {
          method: "POST",
          requiresAuth: false,
          body: JSON.stringify(credentials),
        });
        saveAuth(data);
        setSession(data);
        await refreshUserState();
        return data;
      } finally {
        setIsLoading(false);
      }
    },
    [refreshUserState]
  );

  const register = useCallback(
    async (data: {
      display_name: string;
      email: string;
      password: string;
      role?: string;
    }): Promise<TokenResponse> => {
      setIsLoading(true);
      try {
        const res = await fetchApi<AuthResponse>("/auth/register", {
          method: "POST",
          requiresAuth: false,
          body: JSON.stringify({
            display_name: data.display_name,
            email: data.email,
            password: data.password,
            role: data.role || "student",
          }),
        });
        saveAuth(res);
        setSession(res);
        await refreshUserState();
        return res;
      } finally {
        setIsLoading(false);
      }
    },
    [refreshUserState]
  );

  const updateLocalProfile = useCallback((patch: Partial<TokenResponse>) => {
    updateLocalProfileStorage(patch);
    setSession((prev) => (prev ? { ...prev, ...patch } : null));
  }, []);

  const isAuthenticated = useMemo(() => !!session?.access_token, [session]);

  const contextValue = useMemo<AuthContextType>(
    () => ({
      user,
      session,
      isAuthenticated,
      isLoading,
      initGoogleOAuth,
      handleGoogleCallback,
      refreshToken,
      logout,
      logoutAll,
      setPassword,
      getCurrentUser,
      getMe,
      login,
      register,
      updateLocalProfile,
      refreshUserState,
    }),
    [
      user,
      session,
      isAuthenticated,
      isLoading,
      initGoogleOAuth,
      handleGoogleCallback,
      refreshToken,
      logout,
      logoutAll,
      setPassword,
      getCurrentUser,
      getMe,
      login,
      register,
      updateLocalProfile,
      refreshUserState,
    ]
  );

  return <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
