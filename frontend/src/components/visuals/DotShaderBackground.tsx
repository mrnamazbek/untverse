"use client";

import { useEffect, useRef } from "react";
import { useTheme } from "@/components/theme/ThemeProvider";

interface DotShaderBackgroundProps {
  className?: string;
  variant?: "ambient" | "hero";
}

const clamp = (value: number, min: number, max: number) =>
  Math.min(Math.max(value, min), max);

export function DotShaderBackground({
  className = "",
  variant = "ambient",
}: DotShaderBackgroundProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { resolvedTheme } = useTheme();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const context = canvas.getContext("2d", { alpha: true });
    if (!context) return;

    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const smallViewport = window.matchMedia("(max-width: 640px)");
    const lowPowerDevice =
      (navigator.hardwareConcurrency && navigator.hardwareConcurrency <= 4) ||
      ("deviceMemory" in navigator &&
        (navigator as Navigator & { deviceMemory?: number }).deviceMemory !== undefined &&
        (navigator as Navigator & { deviceMemory?: number }).deviceMemory! <= 4);
    const isHero = variant === "hero";
    const density = lowPowerDevice || smallViewport.matches ? 42 : isHero ? 34 : 48;
    const frameInterval = lowPowerDevice ? 1000 / 30 : 1000 / 45;
    const pointer = { x: -1000, y: -1000 };
    const settledPointer = { ...pointer };
    let animationFrame = 0;
    let lastFrame = 0;
    let isDocumentVisible = document.visibilityState === "visible";
    let isDisposed = false;

    const resize = () => {
      const bounds = canvas.getBoundingClientRect();
      const pixelRatio = Math.min(
        window.devicePixelRatio || 1,
        lowPowerDevice || smallViewport.matches ? 1.25 : 1.75,
      );
      canvas.width = Math.max(1, Math.floor(bounds.width * pixelRatio));
      canvas.height = Math.max(1, Math.floor(bounds.height * pixelRatio));
      context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
      draw(performance.now());
    };

    const draw = (now: number) => {
      const { width, height } = canvas.getBoundingClientRect();
      context.clearRect(0, 0, width, height);

      const dark = resolvedTheme === "dark";
      const baseOpacity = dark ? (isHero ? 0.35 : 0.13) : isHero ? 0.24 : 0.1;
      const glowOpacity = dark ? 0.4 : 0.28;
      const baseRgb = dark ? "115, 184, 255" : "45, 110, 183";
      const radius = isHero ? Math.min(width, height) * 0.5 : 160;
      const elapsed = now / 1000;

      for (let row = -1, y = -density; y < height + density; row += 1, y += density) {
        const rowOffset = row % 2 === 0 ? 0 : density / 2;
        for (let x = -density; x < width + density; x += density) {
          const originX = x + rowOffset;
          const originY = y;
          const distance = Math.hypot(originX - settledPointer.x, originY - settledPointer.y);
          const influence = clamp(1 - distance / radius, 0, 1);
          const easedInfluence = influence * influence * (3 - 2 * influence);
          const drift = reducedMotion.matches
            ? 0
            : Math.sin(elapsed * 0.7 + originX * 0.017 + originY * 0.02) * (isHero ? 0.75 : 0.35);
          const displacedX = originX + (originX - settledPointer.x) * easedInfluence * 0.06;
          const displacedY = originY + (originY - settledPointer.y) * easedInfluence * 0.06 + drift;
          const size = (isHero ? 1.15 : 0.9) + easedInfluence * (isHero ? 1.55 : 1.1);
          const opacity = baseOpacity + easedInfluence * glowOpacity;

          context.beginPath();
          context.arc(displacedX, displacedY, size, 0, Math.PI * 2);
          context.fillStyle = `rgba(${baseRgb}, ${opacity})`;
          context.fill();
        }
      }
    };

    const tick = (now: number) => {
      if (isDisposed || !isDocumentVisible) return;
      if (now - lastFrame >= frameInterval) {
        settledPointer.x += (pointer.x - settledPointer.x) * 0.12;
        settledPointer.y += (pointer.y - settledPointer.y) * 0.12;
        draw(now);
        lastFrame = now;
      }
      if (!reducedMotion.matches) animationFrame = window.requestAnimationFrame(tick);
    };

    const onPointerMove = (event: PointerEvent) => {
      const bounds = canvas.getBoundingClientRect();
      pointer.x = event.clientX - bounds.left;
      pointer.y = event.clientY - bounds.top;
      if (reducedMotion.matches) draw(performance.now());
    };

    const onPointerLeave = () => {
      pointer.x = -1000;
      pointer.y = -1000;
    };

    const onVisibilityChange = () => {
      isDocumentVisible = document.visibilityState === "visible";
      if (isDocumentVisible && !reducedMotion.matches) {
        lastFrame = 0;
        animationFrame = window.requestAnimationFrame(tick);
      }
    };

    const motionChange = () => {
      window.cancelAnimationFrame(animationFrame);
      draw(performance.now());
      if (!reducedMotion.matches && isDocumentVisible) {
        animationFrame = window.requestAnimationFrame(tick);
      }
    };

    const resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(canvas);
    window.addEventListener("pointermove", onPointerMove, { passive: true });
    window.addEventListener("pointerleave", onPointerLeave, { passive: true });
    document.addEventListener("visibilitychange", onVisibilityChange);
    reducedMotion.addEventListener("change", motionChange);
    resize();
    if (!reducedMotion.matches) animationFrame = window.requestAnimationFrame(tick);

    return () => {
      isDisposed = true;
      window.cancelAnimationFrame(animationFrame);
      resizeObserver.disconnect();
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerleave", onPointerLeave);
      document.removeEventListener("visibilitychange", onVisibilityChange);
      reducedMotion.removeEventListener("change", motionChange);
    };
  }, [resolvedTheme, variant]);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      className={`dot-shader ${variant === "hero" ? "dot-shader-hero" : "dot-shader-ambient"} ${className}`}
    />
  );
}
