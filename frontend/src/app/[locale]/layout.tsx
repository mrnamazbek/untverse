import React from "react";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { DotShaderBackground } from "@/components/visuals/DotShaderBackground";
import { SUPPORTED_LOCALES, Locale } from "@/lib/i18n";

const metadataByLocale: Record<Locale, { title: string; description: string }> = {
  kk: {
    title: "UNTverse — ҰБТ информатикасына дайындық",
    description: "Информатикадан ҰБТ-ға арналған интерактивті сабақтар, тесттер және Python практикасы.",
  },
  ru: {
    title: "UNTverse — подготовка к ЕНТ по информатике",
    description: "Интерактивные уроки, тесты и практика Python для подготовки к ЕНТ по информатике.",
  },
  en: {
    title: "UNTverse — Informatics preparation for UNT",
    description: "Interactive lessons, practice tests, and Python exercises for the Informatics UNT exam.",
  },
};

export async function generateStaticParams() {
  return SUPPORTED_LOCALES.map((locale) => ({ locale }));
}

export async function generateMetadata({
  params,
}: Pick<LocaleLayoutProps, "params">): Promise<Metadata> {
  const { locale: rawLocale } = await params;
  const locale = SUPPORTED_LOCALES.includes(rawLocale as Locale) ? rawLocale as Locale : "kk";
  const content = metadataByLocale[locale];
  const path = `/${locale}`;

  return {
    ...content,
    alternates: {
      canonical: path,
      languages: {
        "kk-KZ": "/kk",
        "ru-KZ": "/ru",
        en: "/en",
      },
    },
    openGraph: {
      title: content.title,
      description: content.description,
      locale: locale === "kk" ? "kk_KZ" : locale === "ru" ? "ru_KZ" : "en_US",
      type: "website",
    },
  };
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
    <div className="app-visual-layer relative flex min-h-screen flex-col">
      <DotShaderBackground />
      {children}
    </div>
  );
}
