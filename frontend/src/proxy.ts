import { NextRequest, NextResponse } from "next/server";

export const LOCALES = ["kk", "ru", "en"] as const;
export type SupportedLocale = (typeof LOCALES)[number];
export const DEFAULT_LOCALE: SupportedLocale = "kk";

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Ignore internal assets, static files, and api requests
  if (
    pathname.startsWith("/_next") ||
    pathname.startsWith("/api") ||
    pathname.startsWith("/static") ||
    pathname.includes(".")
  ) {
    return NextResponse.next();
  }

  // Check if pathname already starts with a supported locale
  const pathnameHasLocale = LOCALES.some(
    (locale) => pathname.startsWith(`/${locale}/`) || pathname === `/${locale}`
  );

  if (pathnameHasLocale) {
    const currentLocale = pathname.split("/")[1] as SupportedLocale;
    const requestHeaders = new Headers(request.headers);
    requestHeaders.set("x-untverse-locale", currentLocale);
    const response = NextResponse.next({ request: { headers: requestHeaders } });
    response.cookies.set("untverse_locale", currentLocale, {
      path: "/",
      maxAge: 60 * 60 * 24 * 365, // 1 year
      sameSite: "lax",
    });
    return response;
  }

  // Detect user locale preference: 1) Cookie, 2) Accept-Language header, 3) Default 'kk'
  const cookieLocale = request.cookies.get("untverse_locale")?.value;
  let targetLocale: SupportedLocale = DEFAULT_LOCALE;

  if (cookieLocale && (LOCALES as readonly string[]).includes(cookieLocale)) {
    targetLocale = cookieLocale as SupportedLocale;
  } else {
    const acceptLanguage = request.headers.get("accept-language")?.toLowerCase() || "";
    if (acceptLanguage.startsWith("ru") || acceptLanguage.includes(",ru")) {
      targetLocale = "ru";
    } else if (acceptLanguage.startsWith("en") || acceptLanguage.includes(",en")) {
      targetLocale = "en";
    } else if (
      acceptLanguage.startsWith("kk") ||
      acceptLanguage.includes(",kk") ||
      acceptLanguage.includes("kz")
    ) {
      targetLocale = "kk";
    }
  }

  // Redirect cleanly with search params preserved
  const redirectPath = `/${targetLocale}${pathname === "/" ? "" : pathname}${request.nextUrl.search}`;
  const redirectUrl = new URL(redirectPath, request.url);
  const response = NextResponse.redirect(redirectUrl);
  response.cookies.set("untverse_locale", targetLocale, {
    path: "/",
    maxAge: 60 * 60 * 24 * 365,
    sameSite: "lax",
  });
  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\..*).*)"],
};
