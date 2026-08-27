import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.route("**/api/v1/news/1?**", async (route) => {
    const locale = new URL(route.request().url()).searchParams.get("locale") ?? "kk";
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        id: 1,
        category: "unt",
        importance_score: 1,
        relevance_score: 1,
        is_breaking: false,
        published_at: null,
        last_verified_at: null,
        canonical_url: "https://example.test/news/1",
        source_name: "NTC",
        source_authority: "official_primary",
        title: locale === "en" ? "UNT update" : "ҰБТ жаңалығы",
        summary: "Test summary",
        content: "Test content",
        locale,
      }),
    });
  });

  await page.route("**/api/v1/courses/lessons/1?**", async (route) => {
    const locale = new URL(route.request().url()).searchParams.get("locale") ?? "kk";
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        id: 1,
        topic_id: 1,
        title: "Markdown fixture",
        slug: "markdown-fixture",
        summary: "A safe renderer regression fixture.",
        content: "# H1\n\n**bold**\n\n`inline code`\n\n```python\nprint(x)\n```\n\n> quote",
        order_index: 1,
        xp_reward: 25,
        is_published: true,
        is_completed_by_user: false,
        created_at: "2026-01-01T00:00:00Z",
        locale,
      }),
    });
  });
});

test("language switching preserves dynamic paths, query parameters, and hash fragments", async ({ page }) => {
  await page.goto("/ru/news/1?page=3&difficulty=medium#article", { waitUntil: "domcontentloaded" });
  // Wait for the client-side event handlers; the server markup is deliberately
  // available before hydration for fast first paint.
  await page.waitForTimeout(500);
  await page.getByRole("button", { name: "Қазақ тіліне ауысу" }).click();
  await expect(page).toHaveURL("/kk/news/1?page=3&difficulty=medium#article");

  await page.getByRole("button", { name: "Switch to English" }).click();
  await expect(page).toHaveURL("/en/news/1?page=3&difficulty=medium#article");
});

test("all locale landing pages render a locale-specific document language", async ({ page }) => {
  for (const [locale, lang] of [["kk", "kk-KZ"], ["ru", "ru-KZ"], ["en", "en"]] as const) {
    await page.goto(`/${locale}`, { waitUntil: "domcontentloaded" });
    await expect(page.locator("html")).toHaveAttribute("lang", lang);
  }
});

test("lesson Markdown renders semantic elements instead of raw syntax", async ({ page }) => {
  await page.goto("/en/lesson/1", { waitUntil: "domcontentloaded" });
  await expect(page.locator(".content-renderer h1")).toHaveText("H1");
  await expect(page.locator(".content-renderer strong")).toHaveText("bold");
  await expect(page.locator(".content-renderer pre")).toContainText("print(x)");
  await expect(page.locator(".content-renderer")).not.toContainText("```python");
});
