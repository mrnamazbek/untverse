export interface Lesson {
  id: number;
  topic_id: number;
  title: string;
  slug: string;
  content: string;
  summary?: string | null;
  order_index: number;
  xp_reward: number;
  is_published: boolean;
  is_completed_by_user?: boolean;
  created_at: string;
}

export interface Topic {
  id: number;
  course_id: number;
  title: string;
  slug: string;
  description: string;
  icon?: string;
  color_accent: string;
  order_index: number;
  est_minutes: number;
  xp_reward: number;
  lessons_count?: number;
  quizzes_count?: number;
  coding_tasks_count?: number;
  user_mastery_percentage?: number;
  lessons?: Lesson[];
}

export interface Course {
  id: number;
  title: string;
  slug: string;
  description: string;
  icon?: string;
  is_published: boolean;
  order_index: number;
  topics: Topic[];
  created_at: string;
}

export interface QuestionOption {
  id: number;
  text: string;
  order_index: number;
}

export interface Question {
  id: number;
  quiz_id: number;
  text: string;
  code_snippet?: string | null;
  question_type: "single_choice" | "multiple_choice" | "true_false" | "fill_gap" | "sql" | "matching";
  difficulty: string;
  points: number;
  order_index: number;
  extra_data?: any;
  options: QuestionOption[];
}

export interface Quiz {
  id: number;
  topic_id?: number | null;
  title: string;
  description: string;
  quiz_type: "standard" | "boss_challenge" | "ranked" | "unt_mock" | "daily_training";
  time_limit_seconds: number;
  passing_score: number;
  xp_reward: number;
  is_published: boolean;
  questions?: Question[];
  questions_count?: number;
  user_best_score?: number | null;
  user_completed?: boolean;
}

export interface AnswerReview {
  question_id: number;
  question_text: string;
  question_type: string;
  is_correct: boolean;
  points_awarded: number;
  max_points: number;
  user_selected_options?: number[];
  correct_option_ids: number[];
  explanation?: string | null;
}

export interface QuizSubmitResult {
  attempt_id: number;
  quiz_id: number;
  score: number;
  max_score: number;
  percentage: float;
  passed: boolean;
  time_spent_seconds: number;
  xp_earned: number;
  new_total_xp: number;
  new_level: number;
  leveled_up: boolean;
  streak_extended: boolean;
  current_streak: number;
  answers_review: AnswerReview[];
}

export type float = number;

export interface TestCase {
  id?: number;
  input_data: string;
  expected_output: string;
  is_hidden: boolean;
  order_index: number;
  explanation?: string | null;
}

export interface CodingTask {
  id: number;
  topic_id?: number | null;
  title: string;
  slug: string;
  description: string;
  starter_code: string;
  difficulty: "easy" | "medium" | "hard";
  time_limit_seconds: number;
  memory_limit_mb: number;
  xp_reward: number;
  is_published: boolean;
  test_cases?: TestCase[];
  is_solved_by_user?: boolean;
}

export interface TestCaseResult {
  test_case_id?: number;
  input_data: string;
  expected_output: string;
  actual_output?: string | null;
  passed: boolean;
  is_hidden: boolean;
  execution_time_ms: number;
  error?: string | null;
}

export interface CodeRunResult {
  status: "accepted" | "wrong_answer" | "runtime_error" | "timeout" | "forbidden_syntax";
  passed_tests: number;
  total_tests: number;
  execution_time_ms: number;
  error_output?: string | null;
  test_results: TestCaseResult[];
  xp_earned: number;
  new_total_xp: number;
  new_level: number;
  leveled_up: boolean;
}
