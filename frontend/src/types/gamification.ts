export interface Achievement {
  id: number;
  code: string;
  title: string;
  description: string;
  icon: string;
  badge_color: string;
  category: string;
  xp_reward: number;
  condition_type: string;
  condition_value: number;
  is_unlocked: boolean;
  unlocked_at?: string | null;
}

export interface DailyMission {
  id: number;
  title: string;
  description: string;
  mission_type: string;
  target_count: number;
  xp_reward: number;
  icon: string;
  current_progress: number;
  is_completed: boolean;
  is_claimed: boolean;
}

export interface Streak {
  current_streak: number;
  longest_streak: number;
  last_activity_date?: string | null;
  freeze_count: number;
  is_active_today: boolean;
}

export interface LeaderboardEntry {
  rank: number;
  user_id: number;
  display_name: string;
  avatar_url?: string | null;
  level: number;
  rank_title: string;
  total_xp: number;
  streak_count: number;
}

export interface GamificationProfile {
  user_id: number;
  display_name: string;
  avatar_url?: string | null;
  current_level: number;
  current_xp: number;
  next_level_xp: number;
  level_progress_percentage: number;
  rank_title: string;
  streak: Streak;
  recent_achievements: Achievement[];
  daily_missions: DailyMission[];
}
