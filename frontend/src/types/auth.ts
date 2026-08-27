/**
 * UNTverse Authentication Architecture & OAuth 2.0 PKCE Contracts
 * Synchronized with ADR-006 & FastAPI backend schemas.
 */

export type SupportedLocale = "kk" | "ru" | "en";
export type AuthProvider = "google" | "password" | "apple" | "github";
export type UserRole = "student" | "teacher" | "admin" | "moderator";

export type AuthErrorCode =
  | "AUTH_INVALID_CREDENTIALS"
  | "AUTH_USER_NOT_FOUND"
  | "AUTH_USER_INACTIVE"
  | "AUTH_PASSWORD_NOT_SET"
  | "AUTH_EMAIL_ALREADY_EXISTS"
  | "AUTH_OAUTH_INIT_FAILED"
  | "AUTH_OAUTH_STATE_INVALID"
  | "AUTH_OAUTH_STATE_EXPIRED"
  | "AUTH_OAUTH_CODE_EXCHANGE_FAILED"
  | "AUTH_OAUTH_EMAIL_UNVERIFIED"
  | "AUTH_SESSION_EXPIRED"
  | "AUTH_SESSION_REVOKED"
  | "AUTH_SESSION_REUSE_DETECTED"
  | "AUTH_UNAUTHORIZED"
  | "AUTH_FORBIDDEN"
  | "AUTH_INVALID_REDIRECT_URI"
  | "AUTH_CANNOT_UNLINK_LAST_PROVIDER";

export interface UserProfile {
  id: number;
  user_id: number;
  display_name: string;
  avatar_url?: string | null;
  bio?: string | null;
  target_unt_score: number;
  current_level: number;
  total_xp: number;
  rank_title: string;
  streak_count: number;
  created_at: string;
  updated_at?: string | null;
}
export interface AuthAccount {
  id: number;
  provider: AuthProvider | string;
  provider_account_id?: string;
  provider_email?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface User {
  id: number;
  email: string;
  email_verified: boolean;
  is_active: boolean;
  role: UserRole | string;
  created_at: string;
  updated_at?: string | null;
  last_login_at?: string | null;
  profile?: UserProfile | null;
  auth_accounts?: AuthAccount[];
}

export interface OAuthInitRequest {
  locale?: SupportedLocale;
  redirect_to?: string;
}

export interface OAuthInitResponse {
  authorization_url: string;
  state: string;
}

export interface OAuthCallbackRequest {
  code: string;
  state: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user_id: number;
  email: string;
  role: string;
  display_name: string;
  current_level: number;
  total_xp: number;
  rank_title: string;
  streak_count: number;
  avatar_url?: string | null;
  redirect_to?: string | null;
}

export type UnifiedTokenResponse = TokenResponse;

export interface GoogleLoginResponse extends TokenResponse {
  is_new_user: boolean;
}

export interface LocalTokenRefreshRequest {
  refresh_token?: string;
}

export interface SetPasswordRequest {
  new_password: string;
}

export interface LocalizedErrorMessage {
  kk: string;
  ru: string;
  en: string;
}

export interface LocalizedErrorResponse {
  code: AuthErrorCode;
  message: string;
  localized: LocalizedErrorMessage;
  details?: Record<string, unknown> | null;
  timestamp: string;
}

export type AuthErrorResponse = LocalizedErrorResponse;
