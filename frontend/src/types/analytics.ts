export interface TopicMastery {
  topic_id: number;
  topic_title: string;
  topic_slug: string;
  color_accent: string;
  mastery_percentage: number;
  total_answered: number;
  correct_count: number;
}

export interface MistakeLogItem {
  id: number;
  question_id: number;
  question_text: string;
  question_type: string;
  code_snippet?: string | null;
  explanation?: string | null;
  error_count: number;
  is_resolved: boolean;
  last_mistake_at: string;
}

export interface SpacedCard {
  card_id: number;
  question_id: number;
  question_text: string;
  code_snippet?: string | null;
  question_type: string;
  interval_days: number;
  repetition_number: number;
  options: { id: number; text: string }[];
}

export interface StudentDashboardAnalytics {
  total_study_time_minutes: number;
  unt_readiness_score: number;
  quizzes_completed_count: number;
  coding_tasks_solved_count: number;
  average_quiz_accuracy: number;
  strongest_topics: TopicMastery[];
  weakest_topics: TopicMastery[];
  all_topic_masteries: TopicMastery[];
  unresolved_mistakes_count: number;
  due_reviews_count: number;
  recent_activity_days: { date: string; count: number }[];
}
