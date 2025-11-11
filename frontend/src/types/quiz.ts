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
  quiz_data?: any; // Add this line
  user_answers?: any; // Add this line (optional since it might not always be included)
}

export interface QuizAnalytics {
  total_quizzes_taken: number;
  average_score: number; // Changed from float to number
  best_score: number;
  weakest_topic: string;
  strongest_topic: string;
  total_learning_time: number;
  completion_rate: number; // Changed from float to number
}

export interface QuizFeedback {
  quiz_title: string;
  user_id: number;
  module_id: string;
  topic: string;
  total_questions: number;
  correct_answers: number;
  score: number;
  time_taken_seconds: number | null;
  confidence_rating: number | null;
  completed_at: string;
  question_feedback: Array<{
    question_id: string;
    question_text: string;
    user_answer: string;
    correct_answer: string;
    is_correct: boolean;
    explanation: string;
    time_taken: number | null;
    user_selected_index: number;
    correct_answer_index: number;
  }>;
  strengths: string[];
  areas_for_improvement: string[];
  overall_feedback: string;
}