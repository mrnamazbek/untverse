"use client";

import { Bot } from "lucide-react";
import { useEffect, useRef, useState } from "react";

const ROBOT_SCENE = "/models/untverse-robot.splinecode";
const RUNTIME_LOADER = "/models/load-spline-runtime.mjs";

type SplineApplication = {
  canvas: HTMLCanvasElement;
  load: (scene: string) => Promise<void>;
  dispose: () => void;
  setBackgroundColor: (color: string) => void;
};

type SplineApplicationConstructor = new (
  canvas: HTMLCanvasElement,
  options: { renderOnDemand: boolean; htmlContentMode: "none" },
) => SplineApplication;

declare global {
  interface Window {
    __untverseSplineRuntime?: { Application: SplineApplicationConstructor };
  }
}

let runtimePromise: Promise<SplineApplicationConstructor> | null = null;
let errorFilterReferences = 0;
let originalConsoleError: typeof console.error | null = null;

function loadSplineRuntime() {
  if (window.__untverseSplineRuntime?.Application) {
    return Promise.resolve(window.__untverseSplineRuntime.Application);
  }
  if (runtimePromise) return runtimePromise;

  runtimePromise = new Promise<SplineApplicationConstructor>((resolve, reject) => {
    const resolveRuntime = () => {
      const Application = window.__untverseSplineRuntime?.Application;
      if (Application) resolve(Application);
    };
    const rejectRuntime = () => reject(new Error("Spline runtime could not be loaded"));
    const existing = document.querySelector<HTMLScriptElement>(`script[src="${RUNTIME_LOADER}"]`);

    window.addEventListener("untverse:spline-runtime-ready", resolveRuntime, { once: true });
    if (existing) {
      existing.addEventListener("error", rejectRuntime, { once: true });
      return;
    }

    const script = document.createElement("script");
    script.type = "module";
    script.src = RUNTIME_LOADER;
    script.addEventListener("error", rejectRuntime, { once: true });
    document.head.appendChild(script);
  });

  return runtimePromise;
}

/**
 * The current Spline runtime reports one known, non-actionable `Missing property`
 * message for this scene's animation data. It does not affect the rendered scene.
 * Keep all other runtime errors observable.
 */
function installKnownSplineErrorFilter() {
  if (errorFilterReferences++ > 0) return;
  originalConsoleError = console.error;
  console.error = (...args: unknown[]) => {
    const first = args[0];
    const message = typeof first === "string" ? first : first instanceof Error ? first.message : "";
    if (message === "Missing property") return;
    originalConsoleError?.apply(console, args as Parameters<typeof console.error>);
  };
}

function uninstallKnownSplineErrorFilter() {
  errorFilterReferences -= 1;
  if (errorFilterReferences === 0 && originalConsoleError) {
    console.error = originalConsoleError;
    originalConsoleError = null;
  }
}

/**
 * Client-only, on-demand Spline canvas. The supplied scene retains its authored
 * camera, lights, timeline, and look-at interaction; pointer positions are
 * forwarded into its canvas rather than overwriting those authored transforms.
 */
export function RobotScene() {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const applicationRef = useRef<SplineApplication | null>(null);
  const [isNearViewport, setIsNearViewport] = useState(false);
  const [isDocumentVisible, setIsDocumentVisible] = useState(true);
  const [reducedMotion, setReducedMotion] = useState(false);
  const [status, setStatus] = useState<"loading" | "ready" | "failed">("loading");

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const observer = new IntersectionObserver(
      ([entry]) => setIsNearViewport(entry.isIntersecting),
      { rootMargin: "240px" },
    );
    observer.observe(container);

    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    const updateMotionPreference = () => setReducedMotion(mediaQuery.matches);
    updateMotionPreference();
    mediaQuery.addEventListener("change", updateMotionPreference);

    const onVisibilityChange = () => {
      setIsDocumentVisible(document.visibilityState === "visible");
    };
    document.addEventListener("visibilitychange", onVisibilityChange);

    return () => {
      observer.disconnect();
      mediaQuery.removeEventListener("change", updateMotionPreference);
      document.removeEventListener("visibilitychange", onVisibilityChange);
    };
  }, []);

  useEffect(() => {
    installKnownSplineErrorFilter();
    return () => uninstallKnownSplineErrorFilter();
  }, []);

  const shouldMount = isNearViewport && isDocumentVisible && !reducedMotion;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !shouldMount) return;

    let cancelled = false;
    let application: SplineApplication | null = null;
    setStatus("loading");

    const mount = async () => {
      try {
        const Application = await loadSplineRuntime();
        if (cancelled || !canvasRef.current) return;

        application = new Application(canvas, {
          renderOnDemand: true,
          htmlContentMode: "none",
        });
        application.setBackgroundColor("transparent");
        await application.load(ROBOT_SCENE);
        if (cancelled) return;

        applicationRef.current = application;
        setStatus("ready");
      } catch (error) {
        if (!cancelled) {
          console.error("Unable to load the UNTverse Spline scene", error);
          setStatus("failed");
        }
      }
    };

    void mount();

    return () => {
      cancelled = true;
      applicationRef.current = null;
      application?.dispose();
    };
  }, [shouldMount]);

  useEffect(() => {
    if (status !== "ready" || reducedMotion) return;
    const canvas = applicationRef.current?.canvas;
    if (!canvas) return;

    const forwardPointerPosition = (event: PointerEvent) => {
      if (event.target === canvas) return;
      canvas.dispatchEvent(
        new PointerEvent("pointermove", {
          bubbles: false,
          clientX: event.clientX,
          clientY: event.clientY,
          screenX: event.screenX,
          screenY: event.screenY,
          pointerId: event.pointerId || 1,
          pointerType: event.pointerType || "mouse",
          isPrimary: true,
        }),
      );
    };

    window.addEventListener("pointermove", forwardPointerPosition, { passive: true });
    return () => window.removeEventListener("pointermove", forwardPointerPosition);
  }, [reducedMotion, status]);

  return (
    <div ref={containerRef} className="robot-scene" aria-hidden="true">
      <div className={`robot-fallback ${status === "ready" ? "is-hidden" : ""}`}>
        <div className="robot-fallback-orbit robot-fallback-orbit-one" />
        <div className="robot-fallback-orbit robot-fallback-orbit-two" />
        <div className="robot-fallback-core">
          <Bot className="h-12 w-12" strokeWidth={1.4} />
        </div>
      </div>
      {shouldMount && (
        <canvas
          ref={canvasRef}
          className={`robot-canvas ${status === "ready" ? "is-loaded" : ""}`}
        />
      )}
    </div>
  );
}
