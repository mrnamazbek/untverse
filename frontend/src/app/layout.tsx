import type { Metadata } from "next";
import { headers } from "next/headers";
import { ThemeProvider, themeInitializationScript } from "@/components/theme/ThemeProvider";
import "./globals.css";

export const metadata: Metadata = {
  title: "ЕНТ Информатика — Образовательная платформа подготовки 50/50",
  description:
    "Интерактивная подготовка к ЕНТ по Информатике: полная программа НЦТ, практика Python в песочнице, интервальное повторение SM-2, тесты и рейтинг Казахстана.",
  keywords: [
    "ЕНТ Информатика",
    "ҰБТ Информатика",
    "Подготовка к ЕНТ",
    "Python ЕНТ",
    "Базы данных SQL ЕНТ",
    "Тесты ЕНТ 2026",
  ],
};

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const requestHeaders = await headers();
  const locale = requestHeaders.get("x-untverse-locale");
  const lang = locale === "kk" ? "kk-KZ" : locale === "en" ? "en" : "ru-KZ";

  return (
    <html lang={lang} className="h-full antialiased" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInitializationScript }} />
      </head>
      <body className="min-h-full flex flex-col">
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
