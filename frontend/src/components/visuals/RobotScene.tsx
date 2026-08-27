"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";
import { Bot } from "lucide-react";

type SplineLayer = { type: string; updateTexture: (url: string) => Promise<void> };
type SplineObj = {
  name: string;
  visible: boolean;
  material?: { layers?: SplineLayer[] };
  children?: SplineObj[];
  hide?: () => void;
  show?: () => void;
};

type SplineApp = {
  findObjectByName: (name: string) => SplineObj | undefined;
  load: (scene: string) => Promise<void>;
  canvas?: HTMLCanvasElement;
  requestRender?: () => void;
  dispose?: () => void;
  setBackgroundColor?: (color: string) => void;
};

type SplineAppConstructor = new (
  canvas: HTMLCanvasElement,
  options: { renderOnDemand: boolean; htmlContentMode?: "none" }
) => SplineApp;

interface RobotSceneProps {
  scene?: string;
  className?: string;
  logoImg?: string;
  logoTarget?: string;
  trackCursor?: boolean;
}

const DEFAULT_SCENE = "/spline/scene.splinecode";

let splineFilterCount = 0;
let originalConsoleError: typeof console.error | null = null;

function installSplineErrorFilter() {
  if (splineFilterCount++ > 0) return;
  originalConsoleError = console.error;
  console.error = (...args: unknown[]) => {
    const first = args[0];
    const msg = typeof first === "string" ? first : first instanceof Error ? first.message : "";
    if (msg === "Missing property") return;
    originalConsoleError?.apply(console, args as Parameters<typeof console.error>);
  };
}

function uninstallSplineErrorFilter() {
  if (splineFilterCount > 0) splineFilterCount--;
  if (splineFilterCount === 0 && originalConsoleError) {
    console.error = originalConsoleError;
    originalConsoleError = null;
  }
}

export function RobotScene({
  scene = DEFAULT_SCENE,
  className = "w-full h-full",
  logoImg,
  logoTarget = "logo_ddc",
  trackCursor = true,
}: RobotSceneProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const appRef = useRef<SplineApp | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    installSplineErrorFilter();
    return () => uninstallSplineErrorFilter();
  }, []);

  const removeWatermark = useCallback(() => {
    const links = document.querySelectorAll('a[href*="spline.design"]');
    links.forEach((link) => {
      const parent = link.parentElement;
      if (parent && parent.style.position === "absolute") {
        parent.remove();
      } else {
        link.remove();
      }
    });

    const allLinks = document.querySelectorAll("a");
    allLinks.forEach((link) => {
      const text = link.innerText || "";
      if (
        text.toLowerCase().includes("built with spline") ||
        link.getAttribute("href")?.includes("spline.design")
      ) {
        const parent = link.parentElement;
        if (parent && parent.style.position === "absolute") {
          parent.remove();
        } else {
          link.remove();
        }
      }
    });
  }, []);

  useEffect(() => {
    let app: SplineApp | null = null;
    let cancelled = false;

    async function mount() {
      const canvas = canvasRef.current;
      if (!canvas) return;

      try {
        // Native ESM browser load from UNPKG
        // @ts-expect-error dynamic browser runtime import
        const runtime = await import(/* webpackIgnore: true */ "https://unpkg.com/@splinetool/runtime@1.12.97/build/runtime.js");
        const Application = runtime.Application as SplineAppConstructor;
        if (cancelled || !canvasRef.current || !Application) return;

        app = new Application(canvasRef.current, { renderOnDemand: true });
        app.setBackgroundColor?.("transparent");
        await app.load(scene);
        if (cancelled) return;

        // Apply custom UNTverse chest emblem texture
        if (logoImg) {
          try {
            const targets = [logoTarget, "logo_ddc", "Body"].filter(Boolean) as string[];
            for (const targetName of targets) {
              const obj = app.findObjectByName(targetName);
              if (obj && obj.material?.layers) {
                const textureLayer = obj.material.layers.find((l: SplineLayer) => l.type === "texture");
                if (textureLayer) {
                  await textureLayer.updateTexture(logoImg);
                }
              }
            }
          } catch (err) {
            console.error("Failed to update logo texture:", err);
          }
        }

        appRef.current = app;
        setIsLoaded(true);

        removeWatermark();
        const watermarkInterval = setInterval(removeWatermark, 150);
        setTimeout(() => clearInterval(watermarkInterval), 5000);
      } catch (err) {
        if (!cancelled) {
          console.error("Failed to load Spline scene:", err);
          setHasError(true);
        }
      }
    }

    mount();

    return () => {
      cancelled = true;
      app?.dispose?.();
    };
  }, [scene, logoImg, logoTarget, removeWatermark]);

  useEffect(() => {
    if (!trackCursor || !isLoaded) return;
    const app = appRef.current;
    const canvas = app?.canvas || canvasRef.current;
    if (!canvas) return;

    if (
      typeof window !== "undefined" &&
      window.matchMedia?.("(prefers-reduced-motion: reduce)").matches
    ) {
      return;
    }

    const forward = (e: PointerEvent) => {
      if (e.target === canvas) return;
      try {
        const synthetic = new PointerEvent("pointermove", {
          clientX: e.clientX,
          clientY: e.clientY,
          screenX: e.screenX,
          screenY: e.screenY,
          pointerId: e.pointerId || 1,
          pointerType: e.pointerType || "mouse",
          isPrimary: true,
          bubbles: false,
          cancelable: true,
        });
        canvas.dispatchEvent(synthetic);
      } catch {
        // Safe fallback
      }
    };

    window.addEventListener("pointermove", forward, { passive: true });
    return () => window.removeEventListener("pointermove", forward);
  }, [trackCursor, isLoaded]);

  return (
    <div className={`relative w-full h-full overflow-visible ${className}`}>
      {!isLoaded && !hasError && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="w-12 h-12 rounded-full border-2 border-blue-400/20 border-t-blue-400 animate-spin" />
        </div>
      )}

      {hasError && (
        <div className="absolute inset-0 flex items-center justify-center text-blue-300/40">
          <Bot className="w-16 h-16" strokeWidth={1.2} />
        </div>
      )}

      <canvas
        ref={canvasRef}
        className={`w-full h-full block transition-opacity duration-700 ${
          isLoaded ? "opacity-100" : "opacity-0"
        }`}
        style={{ display: "block", width: "100%", height: "100%" }}
      />
    </div>
  );
}
