// types/quiz.ts
export interface UserAnswer {
  question_id: string;
  selected_option: number;
  is_correct: boolean;
  time_taken?: number;
}

export interface QuizResultCreate {
  user_id: number;
  module_id: string;
  topic: string;
  num_questions: number;
  difficulty_level: string;
  score: number;
  correct_answers: number;
  completion_status: string;
  quiz_data?: any;
  user_answers: UserAnswer[];
  time_taken_seconds?: number;
  confidence_rating?: number;
}

export interface QuizResultResponse {
  id: number;
  user_id: number;
  module_id: string;
  topic: string;
  num_questions: number;
  difficulty_level: string;
  score: number;
  correct_answers: number;
  completion_status: string;
  completed_at: string;
  time_taken_seconds?: number;
  confidence_rating?: number;
  created_at: string;
}

export interface QuizAnalytics {
  total_quizzes_taken: number;
  average_score: float;
  best_score: number;
  weakest_topic: string;
  strongest_topic: string;
  total_learning_time: number;
  completion_rate: float;
}