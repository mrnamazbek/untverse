import React from "react";
import { notFound } from "next/navigation";
import { SUPPORTED_LOCALES, Locale } from "@/lib/i18n";

export async function generateStaticParams() {
  return SUPPORTED_LOCALES.map((locale) => ({ locale }));
}

interface LocaleLayoutProps {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}

export default async function LocaleLayout({
  children,
  params,
}: LocaleLayoutProps) {
  const { locale } = await params;

  if (!SUPPORTED_LOCALES.includes(locale as Locale)) {
    notFound();
  }

  return (
    <div className="flex flex-col min-h-screen">
      {children}
    </div>
  );
}
