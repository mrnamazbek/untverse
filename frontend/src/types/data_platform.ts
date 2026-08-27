export interface CurrentUntRule {
  exam_year: number;
  is_active: boolean;
  structure: {
    total_questions: number;
    maximum_score: number;
    duration_minutes: number;
    duration_formatted: string;
    passing_threshold_total: number;
    passing_threshold_per_subject: number;
  };
  informatics_specifics: {
    questions_count: number;
    max_score: number;
    format: string;
  };
  subjects_breakdown: Record<string, any>;
  profile_combinations: Record<string, any>;
  testing_periods: Array<{
    period: string;
    type: string;
    purpose: string;
    dates: string;
  }>;
  important_deadlines: Record<string, string>;
  grant_rules_summary: Record<string, any>;
  official_source_urls: string[];
  last_verified_at: string | null;
  verified_by: string;
}

export interface SpecificationTopic {
  id: number;
  code: string;
  title: string;
  learning_objectives?: Record<string, any>;
  order_index: number;
}

export interface SpecificationSection {
  id: number;
  code: string;
  title: string;
  description?: string;
  weight_percentage: number;
  question_count_est: number;
  order_index: number;
  topics: SpecificationTopic[];
}

export interface ExamSpecification {
  id: number;
  exam_year: number;
  version: string;
  title: string;
  status: string;
  valid_from: string | null;
  valid_to: string | null;
  total_questions: number;
  max_score: number;
  source_url: string;
  content_hash: string;
  sections: SpecificationSection[];
}

export interface QuestionOption {
  id: number;
  option_key: string;
  text: string;
  is_correct: boolean;
  order_index: number;
}

export interface QuestionProvenance {
  source_title: string;
  source_url: string;
  official_status: string;
  license_type?: string;
  reuse_allowed?: boolean;
  retrieved_at?: string;
}

export interface QuestionSolution {
  approach_type: string;
  complexity?: string;
  step_by_step_explanation: string;
  exam_tip?: string;
}

export interface BankQuestion {
  id: number;
  uuid: string;
  text: string;
  code_snippet?: string;
  explanation?: string;
  locale: string;
  question_type: string;
  difficulty: string;
  difficulty_score: number;
  official_status: string;
  year: number;
  maximum_score: number;
  estimated_time_seconds: number;
  topic_title?: string;
  options: QuestionOption[];
  provenance: QuestionProvenance[];
  solutions?: QuestionSolution[];
}

export interface NewsArticle {
  id: number;
  category: string;
  importance_score: number;
  relevance_score: number;
  is_breaking: boolean;
  published_at: string | null;
  last_verified_at: string | null;
  canonical_url: string;
  source_name: string;
  source_authority: string;
  title: string;
  summary: string;
  content?: string;
  locale: string;
  translation_source?: string;
  revision_count?: number;
}

export interface NewsAlert {
  id: number;
  title: string;
  summary: string;
  published_at: string | null;
  canonical_url: string;
  importance_score: number;
}
