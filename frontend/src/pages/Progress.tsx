import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import * as feather from "feather-icons";
import Navbar from "@/components/Navbar";
import { QuizAnalytics, QuizResultResponse, QuizFeedback } from "@/types/quiz";

const Progress = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState<QuizAnalytics | null>(null);
  const [quizHistory, setQuizHistory] = useState<QuizResultResponse[]>([]);
  const [selectedTimeframe, setSelectedTimeframe] = useState<'week' | 'month' | 'all'>('month');
  const [selectedQuiz, setSelectedQuiz] = useState<QuizResultResponse | null>(null);
  const [quizFeedback, setQuizFeedback] = useState<QuizFeedback | null>(null);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [feedbackLoading, setFeedbackLoading] = useState(false);

  useEffect(() => {
    loadProgressData();
  }, [selectedTimeframe]);

  useEffect(() => {
    if (!loading) {
      feather.replace();
    }
  }, [loading, showFeedbackModal]);

  const loadProgressData = async () => {
    try {
      const userId = localStorage.getItem('userId');
      if (!userId) {
        navigate('/login');
        return;
      }

      // Load analytics
      const analyticsResponse = await fetch(
        `http://localhost:8000/learningpaths/user/${userId}/quiz-analytics`
      );
      if (analyticsResponse.ok) {
        const analyticsData = await analyticsResponse.json();
        setAnalytics(analyticsData);
      }

      // Load quiz history
      const historyResponse = await fetch(
        `http://localhost:8000/learningpaths/user/${userId}/quiz-results?limit=20`
      );
      if (historyResponse.ok) {
        const historyData = await historyResponse.json();
        setQuizHistory(historyData.quiz_results || []);
      }

      setLoading(false);
    } catch (error) {
      console.error('Error loading progress data:', error);
      setLoading(false);
    }
  };

  const handleQuizClick = async (quiz: QuizResultResponse) => {
    setSelectedQuiz(quiz);
    setFeedbackLoading(true);
    setShowFeedbackModal(true);

    try {
      const userId = localStorage.getItem('userId');
      
      // Try using quiz ID first (more reliable)
      const response = await fetch(
        `http://localhost:8000/learningpaths/user/${userId}/quiz-feedback-by-id/${quiz.id}`
      );

      if (response.ok) {
        const feedbackData = await response.json();
        setQuizFeedback(feedbackData);
      } else {
        console.error('Failed to fetch quiz feedback by ID, trying by title...');
        
        // Fallback to title-based approach with proper type checking
        const quizData = quiz.quiz_data;
        const quizTitle = quizData?.quiz_title || `Quiz - ${quiz.topic}`;
        
        const titleResponse = await fetch(
          `http://localhost:8000/learningpaths/user/${userId}/quiz-feedback/${encodeURIComponent(quizTitle)}`
        );
        
        if (titleResponse.ok) {
          const feedbackData = await titleResponse.json();
          setQuizFeedback(feedbackData);
        } else {
          console.error('Failed to fetch quiz feedback by title');
          setQuizFeedback(generateBasicFeedback(quiz));
        }
      }
    } catch (error) {
      console.error('Error fetching quiz feedback:', error);
      setQuizFeedback(generateBasicFeedback(quiz));
    } finally {
      setFeedbackLoading(false);
    }
  };

  const generateBasicFeedback = (quiz: QuizResultResponse): QuizFeedback => {
    const quizData = quiz.quiz_data;
    const questions = quizData?.questions || [];
    
    const questionFeedback = questions.map((q: any, index: number) => ({
      question_id: q.id || `q${index}`,
      question_text: q.questions?.[0] || q.question || 'Question text not available',
      user_answer: 'Answer data not available',
      correct_answer: 'Correct answer data not available',
      is_correct: false,
      explanation: q.explanation || 'No explanation available',
      time_taken: null,
      user_selected_index: 0,
      correct_answer_index: q.correct_answer || 0
    }));

    return {
      quiz_title: quizData?.quiz_title || `Quiz - ${quiz.topic}`,
      user_id: quiz.user_id,
      module_id: quiz.module_id,
      topic: quiz.topic,
      total_questions: quiz.num_questions,
      correct_answers: quiz.correct_answers,
      score: quiz.score,
      time_taken_seconds: quiz.time_taken_seconds || null,
      confidence_rating: quiz.confidence_rating || null,
      completed_at: quiz.completed_at,
      question_feedback: questionFeedback,
      strengths: ['Completed the quiz', 'Demonstrated learning effort'],
      areas_for_improvement: ['Review all concepts', 'Practice more questions'],
      overall_feedback: `You scored ${quiz.score}% on this quiz. ${quiz.score >= 70 ? 'Great job! Keep up the good work.' : 'Keep practicing to improve your understanding.'}`
    };
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const closeFeedbackModal = () => {
    setShowFeedbackModal(false);
    setSelectedQuiz(null);
    setQuizFeedback(null);
  };

  if (loading) {
    return (
      <div className="bg-gray-50 font-sans min-h-screen">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Loading your progress...</p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 font-sans min-h-screen">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Your Learning Progress</h1>
          <p className="text-gray-600">Track your performance and improvement over time</p>
        </div>

        {/* Analytics Overview */}
        {analytics && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-md p-6 text-center">
              <div className="text-2xl font-bold text-blue-600 mb-2">{analytics.total_quizzes_taken}</div>
              <div className="text-gray-600">Quizzes Taken</div>
            </div>
            <div className="bg-white rounded-xl shadow-md p-6 text-center">
              <div className="text-2xl font-bold text-green-600 mb-2">{analytics.average_score}%</div>
              <div className="text-gray-600">Average Score</div>
            </div>
            <div className="bg-white rounded-xl shadow-md p-6 text-center">
              <div className="text-2xl font-bold text-purple-600 mb-2">{analytics.best_score}%</div>
              <div className="text-gray-600">Best Score</div>
            </div>
            <div className="bg-white rounded-xl shadow-md p-6 text-center">
              <div className="text-2xl font-bold text-orange-600 mb-2">
                {Math.round(analytics.total_learning_time / 60)}h
              </div>
              <div className="text-gray-600">Total Learning</div>
            </div>
          </div>
        )}

        {/* Topic Performance */}
        {analytics && (
          <div className="bg-white rounded-xl shadow-md p-6 mb-8">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Topic Performance</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold text-gray-700 mb-3">Strongest Areas</h3>
                <div className="flex items-center space-x-2 mb-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-gray-600">{analytics.strongest_topic}</span>
                </div>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700 mb-3">Areas for Improvement</h3>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <span className="text-gray-600">{analytics.weakest_topic}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Quiz History */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-gray-800">Recent Quiz History</h2>
            <select 
              value={selectedTimeframe}
              onChange={(e) => setSelectedTimeframe(e.target.value as any)}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="week">Last Week</option>
              <option value="month">Last Month</option>
              <option value="all">All Time</option>
            </select>
          </div>

          {quizHistory.length > 0 ? (
            <div className="space-y-4">
              {quizHistory.map((quiz) => (
                <div 
                  key={quiz.id} 
                  className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition duration-200 cursor-pointer"
                  onClick={() => handleQuizClick(quiz)}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-semibold text-gray-800">{quiz.topic}</h3>
                      <p className="text-sm text-gray-600">
                        {quiz.num_questions} questions • {quiz.difficulty_level}
                      </p>
                    </div>
                    <div className={`px-3 py-1 rounded-full ${getScoreBgColor(quiz.score)} ${getScoreColor(quiz.score)} font-medium`}>
                      {quiz.score}%
                    </div>
                  </div>
                  <div className="flex justify-between items-center text-sm text-gray-500">
                    <span>Correct: {quiz.correct_answers}/{quiz.num_questions}</span>
                    <span>
                      {new Date(quiz.completed_at).toLocaleDateString()} • 
                      {quiz.time_taken_seconds ? ` ${Math.round(quiz.time_taken_seconds / 60)}m` : ' Time N/A'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <i data-feather="clipboard" className="w-16 h-16 text-gray-400 mx-auto mb-4"></i>
              <h3 className="text-lg font-medium text-gray-800 mb-2">No Quiz History</h3>
              <p className="text-gray-600 mb-4">Complete some quizzes to see your progress here.</p>
              <button 
                onClick={() => navigate('/learning')}
                className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition duration-200"
              >
                Start Learning
              </button>
            </div>
          )}
        </div>

        {/* Quiz Feedback Modal */}
        {showFeedbackModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-gray-800">
                    {feedbackLoading ? 'Loading Feedback...' : (quizFeedback?.quiz_title || 'Quiz Feedback')}
                  </h2>
                  <button 
                    onClick={closeFeedbackModal}
                    className="text-gray-500 hover:text-gray-700 transition duration-200"
                  >
                    <i data-feather="x" className="w-6 h-6"></i>
                  </button>
                </div>

                {feedbackLoading ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="text-gray-600 mt-4">Generating AI feedback...</p>
                  </div>
                ) : quizFeedback ? (
                  <div className="space-y-6">
                    {/* Overall Performance */}
                    <div className="bg-blue-50 rounded-lg p-4">
                      <div className="flex justify-between items-center mb-3">
                        <h3 className="text-lg font-semibold text-blue-800">Overall Performance</h3>
                        <div className={`text-lg font-bold ${getScoreColor(quizFeedback.score)}`}>
                          {quizFeedback.score}%
                        </div>
                      </div>
                      <p className="text-blue-700">{quizFeedback.overall_feedback}</p>
                      <div className="grid grid-cols-2 gap-4 mt-3 text-sm">
                        <div>
                          <span className="font-medium">Correct Answers:</span> {quizFeedback.correct_answers}/{quizFeedback.total_questions}
                        </div>
                        <div>
                          <span className="font-medium">Time Taken:</span> {quizFeedback.time_taken_seconds ? `${Math.round(quizFeedback.time_taken_seconds / 60)} minutes` : 'N/A'}
                        </div>
                      </div>
                    </div>

                    {/* Strengths & Improvements */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="bg-green-50 rounded-lg p-4">
                        <h4 className="font-semibold text-green-800 mb-3 flex items-center">
                          <i data-feather="check-circle" className="w-4 h-4 mr-2"></i>
                          Your Strengths
                        </h4>
                        <ul className="space-y-2">
                          {quizFeedback.strengths.map((strength, index) => (
                            <li key={index} className="text-green-700 flex items-start">
                              <i data-feather="check" className="w-4 h-4 mr-2 mt-1 flex-shrink-0"></i>
                              {strength}
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div className="bg-orange-50 rounded-lg p-4">
                        <h4 className="font-semibold text-orange-800 mb-3 flex items-center">
                          <i data-feather="alert-circle" className="w-4 h-4 mr-2"></i>
                          Areas to Improve
                        </h4>
                        <ul className="space-y-2">
                          {quizFeedback.areas_for_improvement.map((area, index) => (
                            <li key={index} className="text-orange-700 flex items-start">
                              <i data-feather="arrow-right" className="w-4 h-4 mr-2 mt-1 flex-shrink-0"></i>
                              {area}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    {/* Question-wise Feedback */}
                    <div>
                      <h4 className="text-lg font-semibold text-gray-800 mb-4">Question Analysis</h4>
                      <div className="space-y-4">
                        {quizFeedback.question_feedback.map((question, index) => (
                          <div 
                            key={question.question_id}
                            className={`border-l-4 ${question.is_correct ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'} rounded-r-lg p-4`}
                          >
                            <div className="flex justify-between items-start mb-2">
                              <h5 className="font-medium text-gray-800">
                                Q{index + 1}: {question.question_text}
                              </h5>
                              <span className={`px-2 py-1 rounded text-sm font-medium ${
                                question.is_correct ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'
                              }`}>
                                {question.is_correct ? 'Correct' : 'Incorrect'}
                              </span>
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3 text-sm">
                              <div>
                                <span className="font-medium">Your answer:</span>{' '}
                                <span className={question.is_correct ? 'text-green-700' : 'text-red-700'}>
                                  {question.user_answer}
                                </span>
                              </div>
                              {!question.is_correct && (
                                <div>
                                  <span className="font-medium">Correct answer:</span>{' '}
                                  <span className="text-green-700">{question.correct_answer}</span>
                                </div>
                              )}
                            </div>

                            <div className="bg-white rounded p-3 border">
                              <p className="text-gray-700 text-sm">
                                <span className="font-medium">Explanation:</span> {question.explanation}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex justify-end space-x-4 pt-4 border-t">
                      <button
                        onClick={closeFeedbackModal}
                        className="px-4 py-2 text-gray-600 hover:text-gray-800 transition duration-200"
                      >
                        Close
                      </button>
                      <button
                        onClick={() => navigate('/learning')}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition duration-200"
                      >
                        Practice More
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <i data-feather="alert-triangle" className="w-16 h-16 text-yellow-500 mx-auto mb-4"></i>
                    <h3 className="text-lg font-medium text-gray-800 mb-2">Feedback Not Available</h3>
                    <p className="text-gray-600">Unable to load feedback for this quiz.</p>
                    <button
                      onClick={closeFeedbackModal}
                      className="mt-4 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition duration-200"
                    >
                      Close
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default Progress;