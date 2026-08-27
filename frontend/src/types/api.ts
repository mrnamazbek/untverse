export interface User {
  id: number;
  email: string;
  role: "student" | "teacher" | "admin";
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  profile?: UserProfile;
}

export interface UserProfile {
  id: number;
  user_id: number;
  display_name: string;
  avatar_url?: string | null;
  bio?: string | null;
  target_unt_score: number;
  current_level: number;
  total_xp: number;
  rank_title: string;
  streak_count: number;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user_id: number;
  email: string;
  role: string;
  display_name: string;
  current_level: number;
  total_xp: number;
  rank_title: string;
  streak_count: number;
}
