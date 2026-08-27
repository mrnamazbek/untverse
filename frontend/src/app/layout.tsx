import type { Metadata } from "next";
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

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ru" className="h-full antialiased">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
