import assert from "node:assert/strict";
import test from "node:test";
import { getLocaleFromPathname, localizePath, switchLocaleUrl } from "../src/lib/i18n";

test("localizePath replaces only the locale segment and preserves route state", () => {
  assert.equal(
    localizePath("/ru/practice/python?page=3&difficulty=medium#questions", "kk"),
    "/kk/practice/python?page=3&difficulty=medium#questions",
  );
});

test("locale switching preserves dynamic lesson identifiers", () => {
  assert.equal(switchLocaleUrl("en", "/ru/lesson/number-systems"), "/en/lesson/number-systems");
  assert.equal(switchLocaleUrl("kk", "/ru/learn/python?tab=lessons"), "/kk/learn/python?tab=lessons");
});

test("unlocalized paths receive exactly one locale segment", () => {
  assert.equal(localizePath("/dashboard", "ru"), "/ru/dashboard");
  assert.equal(localizePath("/kk", "en"), "/en");
  assert.equal(getLocaleFromPathname("/en/news/42"), "en");
});

test("locale switching preserves redirect_to search params during auth flow", () => {
  assert.equal(
    switchLocaleUrl("kk", "/ru/login?redirect_to=%2Fpractice"),
    "/kk/login?redirect_to=%2Fpractice"
  );
  assert.equal(
    switchLocaleUrl("en", "/kk/auth/error?code=AUTH_OAUTH_STATE_EXPIRED&redirect_to=/dashboard"),
    "/en/auth/error?code=AUTH_OAUTH_STATE_EXPIRED&redirect_to=/dashboard"
  );
});

test("getLocalizedAuthError maps all 17 AuthErrorCode items correctly across kk, ru, en", async () => {
  const { getLocalizedAuthError, i18nDict, SUPPORTED_LOCALES } = await import("../src/lib/i18n");

  const sampleCodes = [
    "AUTH_INVALID_CREDENTIALS",
    "AUTH_USER_NOT_FOUND",
    "AUTH_USER_INACTIVE",
    "AUTH_PASSWORD_NOT_SET",
    "AUTH_EMAIL_ALREADY_EXISTS",
    "AUTH_OAUTH_INIT_FAILED",
    "AUTH_OAUTH_STATE_INVALID",
    "AUTH_OAUTH_STATE_EXPIRED",
    "AUTH_OAUTH_CODE_EXCHANGE_FAILED",
    "AUTH_OAUTH_EMAIL_UNVERIFIED",
    "AUTH_SESSION_EXPIRED",
    "AUTH_SESSION_REVOKED",
    "AUTH_SESSION_REUSE_DETECTED",
    "AUTH_UNAUTHORIZED",
    "AUTH_FORBIDDEN",
    "AUTH_INVALID_REDIRECT_URI",
    "AUTH_CANNOT_UNLINK_LAST_PROVIDER",
  ];

  for (const locale of SUPPORTED_LOCALES) {
    const dict = i18nDict[locale];
    assert.ok(dict.auth.loginButton, `Missing auth.loginButton for ${locale}`);
    assert.ok(dict.oauth.googleSignIn, `Missing oauth.googleSignIn for ${locale}`);

    for (const code of sampleCodes) {
      const msg = getLocalizedAuthError(code, locale);
      assert.ok(msg, `Error message missing for code ${code} in ${locale}`);
      assert.notEqual(msg, dict.errors.defaultError, `Code ${code} returned default error in ${locale}`);
}
  }
});
