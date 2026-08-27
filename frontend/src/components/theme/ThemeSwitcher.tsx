"use client";

import { Monitor, Moon, Sun } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { ThemePreference, useTheme } from "./ThemeProvider";

const options: Array<{
  value: ThemePreference;
  label: string;
  Icon: typeof Sun;
}> = [
  { value: "light", label: "Light", Icon: Sun },
  { value: "dark", label: "Dark", Icon: Moon },
  { value: "system", label: "System", Icon: Monitor },
];

export function ThemeSwitcher() {
  const { preference, resolvedTheme, setTheme } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const CurrentIcon = resolvedTheme === "dark" ? Moon : Sun;

  useEffect(() => {
    const closeOnPointerDown = (event: MouseEvent) => {
      if (!containerRef.current?.contains(event.target as Node)) setIsOpen(false);
    };

    document.addEventListener("mousedown", closeOnPointerDown);
    return () => document.removeEventListener("mousedown", closeOnPointerDown);
  }, []);

  return (
    <div className="relative" ref={containerRef}>
      <button
        type="button"
        aria-label={`Theme: ${preference}. Change theme`}
        aria-haspopup="menu"
        aria-expanded={isOpen}
        onClick={() => setIsOpen((open) => !open)}
        onKeyDown={(event) => {
          if (event.key === "Escape") setIsOpen(false);
        }}
        className="theme-trigger"
      >
        <CurrentIcon aria-hidden="true" className="h-4 w-4" />
        <span className="hidden xl:inline">{preference}</span>
      </button>

      {isOpen && (
        <div className="theme-menu" role="menu" aria-label="Choose colour theme">
          {options.map(({ value, label, Icon }) => (
            <button
              key={value}
              type="button"
              role="menuitemradio"
              aria-checked={preference === value}
              className={`theme-menu-option ${preference === value ? "is-selected" : ""}`}
              onClick={() => {
                setTheme(value);
                setIsOpen(false);
              }}
            >
              <Icon aria-hidden="true" className="h-4 w-4" />
              <span>{label}</span>
              {preference === value && <span className="theme-menu-check" aria-hidden="true">✓</span>}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
