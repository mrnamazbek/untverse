import assert from "node:assert/strict";
import test from "node:test";
import fs from "node:fs";
import path from "node:path";
import { userToAuthSession } from "../src/lib/auth";
import type { User } from "../src/types/auth";

test("userToAuthSession correctly transforms User DTO to AuthResponse session", () => {
  const mockUser: User = {
    id: 42,
    email: "student@untverse.kz",
    email_verified: true,
    is_active: true,
    role: "student",
    created_at: "2026-08-27T00:00:00Z",
    profile: {
      id: 10,
      user_id: 42,
      display_name: "Alikhan",
      avatar_url: "https://lh3.googleusercontent.com/a/mock-photo",
      bio: "Aspiring software engineer",
      target_unt_score: 50,
      current_level: 3,
      total_xp: 450,
      rank_title: "Алгоритмист",
      streak_count: 7,
      created_at: "2026-08-27T00:00:00Z",
    },
    auth_accounts: [
      {
        id: 1,
        provider: "google",
        provider_account_id: "google-sub-12345",
        created_at: "2026-08-27T00:00:00Z",
      },
    ],
  };

  const existingAuth = {
    access_token: "mock_access_jwt",
    refresh_token: "mock_refresh_jwt",
    token_type: "bearer",
    expires_in: 900,
    user_id: 42,
    email: "student@untverse.kz",
    role: "student",
    display_name: "Alikhan",
    current_level: 3,
    total_xp: 450,
    rank_title: "Алгоритмист",
    streak_count: 7,
    redirect_to: "/practice",
  };

  const session = userToAuthSession(mockUser, existingAuth);

  assert.equal(session.user_id, 42);
  assert.equal(session.email, "student@untverse.kz");
  assert.equal(session.display_name, "Alikhan");
  assert.equal(session.avatar_url, "https://lh3.googleusercontent.com/a/mock-photo");
  assert.equal(session.total_xp, 450);
  assert.equal(session.current_level, 3);
  assert.equal(session.streak_count, 7);
  assert.equal(session.access_token, "mock_access_jwt");
  assert.equal(session.redirect_to, "/practice");
});

test("JSON message dictionaries exist and contain auth, oauth, and error sections", () => {
  const locales = ["kk", "ru", "en"];
  for (const loc of locales) {
    const filePath = path.resolve(__dirname, `../messages/${loc}.json`);
    assert.ok(fs.existsSync(filePath), `File ${filePath} must exist`);

    const content = JSON.parse(fs.readFileSync(filePath, "utf-8"));
    assert.ok(content.auth, `Missing 'auth' in ${loc}.json`);
    assert.ok(content.oauth, `Missing 'oauth' in ${loc}.json`);
    assert.ok(content.errors, `Missing 'errors' in ${loc}.json`);

    assert.ok(content.auth.loginTitle, `Missing auth.loginTitle in ${loc}.json`);
    assert.ok(content.oauth.googleSignIn, `Missing oauth.googleSignIn in ${loc}.json`);
    assert.ok(content.errors.AUTH_INVALID_CREDENTIALS, `Missing error AUTH_INVALID_CREDENTIALS in ${loc}.json`);
    assert.ok(content.errors.AUTH_OAUTH_STATE_EXPIRED, `Missing error AUTH_OAUTH_STATE_EXPIRED in ${loc}.json`);
    assert.ok(content.errors.AUTH_SESSION_REUSE_DETECTED, `Missing error AUTH_SESSION_REUSE_DETECTED in ${loc}.json`);
  }
});
