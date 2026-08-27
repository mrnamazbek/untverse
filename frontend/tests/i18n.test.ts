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
