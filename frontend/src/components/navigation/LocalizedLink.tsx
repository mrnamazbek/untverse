"use client";

import Link, { type LinkProps } from "next/link";
import { usePathname } from "next/navigation";
import type { ComponentProps } from "react";
import { type Locale, getLocaleFromPathname, localizePath } from "@/lib/i18n";

type LocalizedLinkProps = Omit<ComponentProps<typeof Link>, "href"> & {
  href: string;
  locale?: Locale;
};

/** A single locale-aware Link for every client-side application route. */
export function LocalizedLink({ href, locale, ...props }: LocalizedLinkProps) {
  const pathname = usePathname();
  const activeLocale = locale ?? getLocaleFromPathname(pathname);
  return <Link href={localizePath(href, activeLocale)} {...props} />;
}

export type { LinkProps };
