import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import * as feather from "feather-icons";
import Navbar from "@/components/Navbar";
import { QuizAnalytics, QuizResultResponse } from "@/types/quiz";

const Progress = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState<QuizAnalytics | null>(null);
  const [quizHistory, setQuizHistory] = useState<QuizResultResponse[]>([]);
  const [selectedTimeframe, setSelectedTimeframe] = useState<'week' | 'month' | 'all'>('month');

  useEffect(() => {
    loadProgressData();
  }, [selectedTimeframe]);

  useEffect(() => {
    if (!loading) {
      feather.replace();
    }
  }, [loading]);

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
                <div key={quiz.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition duration-200">
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
      </main>
    </div>
  );
};

export default Progress;