import { Application } from "https://unpkg.com/@splinetool/runtime@2.0.8/build/runtime.js";

window.__untverseSplineRuntime = { Application };
window.dispatchEvent(new Event("untverse:spline-runtime-ready"));
