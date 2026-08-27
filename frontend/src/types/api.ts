export * from "./auth";

// Backward-compatible alias for existing frontend code
export type AuthResponse = import("./auth").TokenResponse;

