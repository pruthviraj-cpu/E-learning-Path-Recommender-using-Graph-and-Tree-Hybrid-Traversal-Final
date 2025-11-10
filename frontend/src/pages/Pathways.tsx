import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import * as feather from "feather-icons";
import Navbar from "@/components/Navbar";
import { toast } from "@/hooks/use-toast";
import { UserAnswer, QuizResultCreate } from '@/types/quiz';

// interface ModuleContent {
//   video_url?: string;
//   sections?: Array<{
//     title: string;
//     content: string;
//   }>;
// }

// just for fun
interface ModuleContent {
  video_url?: string;
  short_videos?: string;
  long_videos?: string;
  sections?: Array<{ title: string; content: string }>;
  reading_materials?: Array<{ title: string; link?: string; content?: string }>;
  projects?: Array<{ title: string; description: string; link?: string }>;
}


interface Assessment {
  id: string;
  type: string;
  questions: string[];
  options: string[];
  correct_answer: number;
  explanation?: string;
  points: number;
}

interface Module {
  id: string;
  title: string;
  description?: string;
  content?: ModuleContent;
  assessments?: Assessment[];
  skills?: string[];
  difficulty?: string;
}

interface QuizConfig {
  numQuestions: number;
  difficulty: string;
  questionTypes: string[];
}

const Pathways = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentModule, setCurrentModule] = useState<Module | null>(null);
  const [activeTab, setActiveTab] = useState('content');
  const [confidenceRating, setConfidenceRating] = useState<number | null>(null);
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [userAnswers, setUserAnswers] = useState<{ [key: number]: number }>({});
  const [submitted, setSubmitted] = useState(false);
  const [currentVideoIndex, setCurrentVideoIndex] = useState(0);
  const [currentVideoType, setCurrentVideoType] = useState<'long' | 'short'>('long');
  const [userData, setUserData] = useState<any>(null);
  const [learnerType, setLearnerType] = useState<string>(''); // Add this to your state


  // Quiz state management
  const [quizConfig, setQuizConfig] = useState<QuizConfig>({
    numQuestions: 5,
    difficulty: 'beginner',
    questionTypes: ['mcq', 'true_false']
  });
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [quizStarted, setQuizStarted] = useState(false);
  const [quizCompleted, setQuizCompleted] = useState(false);
  const [quizScore, setQuizScore] = useState(0);
  const [generatingQuiz, setGeneratingQuiz] = useState(false);
  const [timeStarted, setTimeStarted] = useState<Date | null>(null);
  const [timeCompleted, setTimeCompleted] = useState<Date | null>(null);


  const [showAnalytics, setShowAnalytics] = useState(false);
  const [userAnalytics, setUserAnalytics] = useState<any>(null);

  const fetchUserAnalytics = async () => {
    try {
      const userId = localStorage.getItem('userId');
      if (!userId) return;

      const response = await fetch(`http://localhost:8000/learningpaths/user/${userId}/quiz-analytics`);
      if (response.ok) {
        const analytics = await response.json();
        setUserAnalytics(analytics);
        setShowAnalytics(true);
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  useEffect(() => {
    initializeApp();
  }, []);

  useEffect(() => {
    if (!loading) {
      feather.replace();
    }
  }, [loading, activeTab, quizStarted, quizCompleted]);


  // for learner type
  // useEffect(() => {
  //   setLoading(true);

  //   
  // },[]);

  // const initializeApp = async () => {
  //   try {
  //     const storedPath = localStorage.getItem('currentLearningPath');
  //     const storedModuleIndex = localStorage.getItem('currentModule');

  //     if (!storedPath) {
  //       navigate('/learning');
  //       return;
  //     }

  //     const path = JSON.parse(storedPath);
  //     const moduleIndex = storedModuleIndex ? parseInt(storedModuleIndex) : path.progress?.current_module || 0;

  //     if (path.path_data && path.path_data[moduleIndex]) {
  //       const module = path.path_data[moduleIndex];

  //       // Fetch module content and assessments from backend
  //       try {
  //         const response = await fetch(`http://localhost:8000/learningpaths/modules/${module.id}/content`);
  //         if (response.ok) {
  //           const moduleData = await response.json();
  //           setCurrentModule(moduleData);
  //         } else {
  //           // Fallback to basic module data
  //           setCurrentModule(module);
  //         }
  //       } catch (err) {
  //         console.error('Error fetching module details:', err);
  //         setCurrentModule(module);
  //       }
  //     } else {
  //       setError('Module not found');
  //     }

  //     setLoading(false);
  //   } catch (err) {
  //     console.error('Error loading content:', err);
  //     setError('Failed to load learning content');
  //     setLoading(false);
  //   }
  // };



// const getLearnerType = () => {
//   try {
//     const storedUser = localStorage.getItem("userData");
    
//     if (!storedUser) {
//       console.warn("No user data found in localStorage");
//       setLoading(false);
//       return;
//     }

//     let user;
//     try {
//       user = JSON.parse(storedUser);
//     } catch (parseError) {
//       console.error("Invalid JSON in userData:", parseError);
//       setLoading(false);
//       return;
//     }

//     setUserData(user);

//     if (user.learnerType) {
//       console.log(`User is a ${user.learnerType} learner`);
//       setLearnerType(user.learnerType);
      
//       // Auto-select recommended tab based on learner type
//       switch(user.learnerType.toLowerCase()) {
//         case 'visual':
//           setActiveTab('content');
//           break;
//         case 'reading':
//           setActiveTab('reading');
//           break;
//         case 'kinesthetic':
//         case 'hands-on':
//           setActiveTab('project');
//           break;
//         default:
//           setActiveTab('content'); // default fallback
//       }
//     } else {
//       console.warn("Learner type not found in user data");
//       setLearnerType('general');
//     }

//   } catch (err) {
//     console.error("Unexpected error loading user data:", err);
//   } finally {
//     setLoading(false);
//   }
// };

  const initializeApp = async () => {
    try {
      const storedPath = localStorage.getItem('currentLearningPath');
      const storedModuleIndex = localStorage.getItem('currentModule');

      if (!storedPath) {
        navigate('/learning');
        return;
      }

      const path = JSON.parse(storedPath);
      const moduleIndex = storedModuleIndex
        ? parseInt(storedModuleIndex)
        : path.progress?.current_module || 0;

      if (!(path.path_data && path.path_data[moduleIndex])) {
        setError('Module not found');
        setLoading(false);
        return;
      }

      const module = path.path_data[moduleIndex];

      // Ensure reading_materials is always an array of objects
      const transformReadingMaterials = (materials: any[]) =>
        (materials || []).map((rm: any) => ({
          title: rm.title || rm || 'No Title',
          link: rm.link || (typeof rm === 'string' ? rm : ''),
          content: rm.content || ''
        }));

      const buildModuleContent = (data: any) => ({
        long_videos: data?.long_videos || [],
        short_videos: data?.short_videos || [],
        reading_materials: transformReadingMaterials(data?.reading_materials || []),
        quizzes: data?.quizzes || [],
        projects: data?.projects || []
      });

      try {
        const response = await fetch(
          `http://localhost:8000/learningpaths/modules/${module.id}/content`
        );

        if (response.ok) {
          const moduleData = await response.json();
          setCurrentModule({
            ...moduleData,
            content: buildModuleContent(moduleData.content)
          });
        } else {
          setCurrentModule({
            ...module,
            content: buildModuleContent(module)
          });
        }
      } catch (err) {
        console.error('Error fetching module details:', err);
        setCurrentModule({
          ...module,
          content: buildModuleContent(module)
        });
      }

      setLoading(false);
    } catch (err) {
      console.error('Error loading content:', err);
      setError('Failed to load learning content');
      setLoading(false);
    }
  };


  const handleConfidenceSelect = async (rating: number) => {
    setConfidenceRating(rating);

    try {
      const userId = localStorage.getItem('userId');
      const storedPath = localStorage.getItem('currentLearningPath');

      if (userId && storedPath) {
        const path = JSON.parse(storedPath);
        await fetch(`http://localhost:8000/learningpaths/user/${userId}/confidence`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            module_id: currentModule?.id,
            confidence_rating: rating,
            path_id: path.path_id
          })
        });
      }

      toast({
        title: "Confidence Saved",
        description: `You rated your confidence as ${rating}/5`,
      });
    } catch (err) {
      console.error('Error saving confidence rating:', err);
    }
  };

  const handleAnswerSelect = (questionIndex: number, optionIndex: number) => {
    if (!submitted) {
      setUserAnswers({
        ...userAnswers,
        [questionIndex]: optionIndex
      });
    }
  };

  const handleQuizAnswerSelect = (optionIndex: number) => {
    setUserAnswers({
      ...userAnswers,
      [currentQuestionIndex]: optionIndex
    });
  };

  const submitAssessment = async () => {
    if (Object.keys(userAnswers).length < assessments.length) {
      toast({
        title: "Incomplete Assessment",
        description: "Please answer all questions before submitting.",
        variant: "destructive"
      });
      return;
    }

    setSubmitted(true);

    let correct = 0;
    assessments.forEach((assessment, index) => {
      if (userAnswers[index] === assessment.correct_answer) {
        correct++;
      }
    });

    const score = Math.round((correct / assessments.length) * 100);

    // Save assessment results
    try {
      const userId = localStorage.getItem('userId');
      const storedPath = localStorage.getItem('currentLearningPath');

      if (userId && storedPath && currentModule) {
        const path = JSON.parse(storedPath);
        await fetch(`http://localhost:8000/learningpaths/user/${userId}/assessment-results`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            module_id: currentModule.id,
            path_id: path.path_id,
            score: score,
            total_questions: assessments.length,
            correct_answers: correct,
            user_answers: userAnswers
          })
        });
      }
    } catch (err) {
      console.error('Error saving assessment results:', err);
    }

    toast({
      title: "Assessment Complete!",
      description: `You scored ${score}%. Great job!`,
    });
  };

  // Update the submitQuiz function
  const submitQuiz = async () => {
      // Ensure timeCompleted is set
      const completionTime = new Date();
      setTimeCompleted(completionTime);
      setQuizCompleted(true);
      
      let correct = 0;
      const userAnswersDetailed: UserAnswer[] = [];
      
      assessments.forEach((assessment, index) => {
        const isCorrect = userAnswers[index] === assessment.correct_answer;
        if (isCorrect) {
          correct++;
        }
        
        userAnswersDetailed.push({
          question_id: assessment.id,
          selected_option: userAnswers[index],
          is_correct: isCorrect,
          time_taken: 0 // You can implement per-question timing if needed
        });
      });

      const score = Math.round((correct / assessments.length) * 100);
      setQuizScore(score);
      
      // Calculate time spent - FIXED: Ensure we have both timestamps
      const startTime = timeStarted || new Date(); // Fallback if timeStarted is null
      const timeSpent = Math.round((completionTime.getTime() - startTime.getTime()) / 1000);

      console.log(`⏱️ Time tracking - Started: ${startTime}, Completed: ${completionTime}, Spent: ${timeSpent} seconds`);

      // Save quiz results with detailed data
      try {
        const userId = localStorage.getItem('userId');
        const storedPath = localStorage.getItem('currentLearningPath');
        
        if (userId && storedPath && currentModule) {
          const path = JSON.parse(storedPath);
          
          const quizResultData: QuizResultCreate = {
            user_id: parseInt(userId),
            module_id: currentModule.id,
            topic: currentModule.title,
            num_questions: assessments.length,
            difficulty_level: quizConfig.difficulty,
            score: score,
            correct_answers: correct,
            completion_status: "completed",
            quiz_data: {
              questions: assessments,
              quiz_title: `AI Quiz - ${currentModule.title}`,
              difficulty: quizConfig.difficulty,
              question_types: quizConfig.questionTypes
            },
            user_answers: userAnswersDetailed,
            time_taken_seconds: timeSpent, // This should now be correctly set
            confidence_rating: confidenceRating
          };

          console.log('📊 Saving quiz results:', {
            time_taken_seconds: timeSpent,
            score: score,
            correct_answers: correct
          });

          const response = await fetch(`http://localhost:8000/learningpaths/user/${userId}/assessment-results`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(quizResultData)
          });

          if (response.ok) {
            const savedResult = await response.json();
            console.log('✅ Quiz results saved:', savedResult);
            
            toast({
              title: "Quiz Completed!",
              description: `Your results have been saved. Score: ${score}%`,
            });
          } else {
            const errorText = await response.text();
            console.error('❌ Backend error:', errorText);
            throw new Error(`Backend error: ${errorText}`);
          }
        }
      } catch (err) {
        console.error('Error saving quiz results:', err);
        toast({
          title: "Warning",
          description: "Quiz completed but results couldn't be saved.",
          variant: "destructive"
        });
      }
    };

  // Update the generateAIQuiz function to include quiz data
  const generateAIQuiz = async () => {
    if (!currentModule) return;

    setGeneratingQuiz(true);
    toast({
      title: "Generating Quiz",
      description: "Creating AI-powered questions for you...",
    });

    try {
      const response = await fetch('http://localhost:8000/learningpaths/ai/generate-quiz', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: currentModule.title,
          num_questions: quizConfig.numQuestions,
          difficulty: quizConfig.difficulty,
          question_types: quizConfig.questionTypes
        })
      });

      if (response.ok) {
        const data = await response.json();
        const transformedQuestions = data.questions.map((q: any, index: number) => ({
          id: `ai_${index}`,
          type: q.type || 'mcq',
          questions: [q.question],
          options: q.type === 'mcq' ? Object.values(q.options || {}) : ['True', 'False'],
          correct_answer: q.type === 'true_false' ? (q.correct_answer === 'true' ? 0 : 1) :
            ['A', 'B', 'C', 'D'].indexOf(q.correct_answer),
          explanation: q.explanation,
          points: 1
        }));

        setAssessments(transformedQuestions);
        setUserAnswers({});
        setSubmitted(false);
        setQuizStarted(true);
        setTimeStarted(new Date());
        setCurrentQuestionIndex(0);
        setQuizCompleted(false);

        toast({
          title: "Quiz Generated!",
          description: "Your AI-powered quiz is ready.",
        });
      }
    } catch (error) {
      console.error('Error generating AI quiz:', error);
      toast({
        title: "Error",
        description: "Failed to generate quiz. Please try again.",
        variant: "destructive"
      });
    } finally {
      setGeneratingQuiz(false);
    }
  };

  const startQuiz = () => {
    setQuizStarted(true);
    setTimeStarted(new Date());
    setCurrentQuestionIndex(0);
    setUserAnswers({});
    setQuizCompleted(false);
  };

  const nextQuestion = () => {
    if (currentQuestionIndex < assessments.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const prevQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const restartQuiz = () => {
    setQuizStarted(false);
    setQuizCompleted(false);
    setUserAnswers({});
    setCurrentQuestionIndex(0);
    setQuizScore(0);
  };

  const markModuleComplete = async () => {
    if (!currentModule) return;

    try {
      const userId = localStorage.getItem('userId');
      const storedPath = localStorage.getItem('currentLearningPath');

      if (userId && storedPath) {
        const path = JSON.parse(storedPath);
        const response = await fetch(
          `http://localhost:8000/generate-path/user/${userId}/path/${path.path_id}/complete-node`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ node_id: currentModule.id })
          }
        );

        if (response.ok) {
          toast({
            title: "Module Completed!",
            description: "Great job! You've completed this module.",
          });
        }
      }
    } catch (err) {
      console.error('Error marking module complete:', err);
    }
  };

  // Quiz Configuration Component
  const QuizConfigurator = () => (
    <div className="bg-white rounded-xl shadow-md p-6 mb-6">
      <h3 className="text-xl font-bold text-gray-800 mb-4">Configure Your Quiz</h3>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Number of Questions
          </label>
          <select
            value={quizConfig.numQuestions}
            onChange={(e) => setQuizConfig({ ...quizConfig, numQuestions: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value={5}>5 Questions</option>
            <option value={10}>10 Questions</option>
            <option value={15}>15 Questions</option>
            <option value={20}>20 Questions</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Difficulty Level
          </label>
          <select
            value={quizConfig.difficulty}
            onChange={(e) => setQuizConfig({ ...quizConfig, difficulty: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Question Types
          </label>
          <div className="space-y-2">
            {['mcq', 'true_false', 'short_answer'].map((type) => (
              <label key={type} className="flex items-center">
                <input
                  type="checkbox"
                  checked={quizConfig.questionTypes.includes(type)}
                  onChange={(e) => {
                    const newTypes = e.target.checked
                      ? [...quizConfig.questionTypes, type]
                      : quizConfig.questionTypes.filter(t => t !== type);
                    setQuizConfig({ ...quizConfig, questionTypes: newTypes });
                  }}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-700 capitalize">
                  {type.replace('_', ' ')}
                </span>
              </label>
            ))}
          </div>
        </div>
      </div>

      <button
        onClick={generateAIQuiz}
        disabled={generatingQuiz}
        className={`w-full mt-6 py-3 px-4 rounded-lg font-medium transition duration-200 flex items-center justify-center ${generatingQuiz
          ? 'bg-gray-400 cursor-not-allowed'
          : 'bg-purple-600 hover:bg-purple-700 text-white'
          }`}
      >
        {generatingQuiz ? (
          <>
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            Generating Quiz...
          </>
        ) : (
          <>
            <i data-feather="zap" className="w-4 h-4 mr-2"></i>
            Generate AI Quiz
          </>
        )}
      </button>
    </div>
  );

  // Quiz Progress Component
  const QuizProgress = () => (
    <div className="mb-6">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm text-gray-600">
          Question {currentQuestionIndex + 1} of {assessments.length}
        </span>
        <span className="text-sm font-medium text-blue-600">
          Progress: {Math.round(((currentQuestionIndex + 1) / assessments.length) * 100)}%
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
          style={{ width: `${((currentQuestionIndex + 1) / assessments.length) * 100}%` }}
        ></div>
      </div>
    </div>
  );

  // Single Question Component
  const QuizQuestion = () => {
    if (!assessments[currentQuestionIndex]) return null;

    const question = assessments[currentQuestionIndex];
    const userAnswer = userAnswers[currentQuestionIndex];
    const isAnswered = userAnswer !== undefined;

    return (
      <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
        <div className="flex justify-between items-start mb-6">
          <div>
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
              Question {currentQuestionIndex + 1} of {assessments.length}
            </span>
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800 ml-2">
              {question.type.toUpperCase()}
            </span>
          </div>
          {question.points && (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
              {question.points} points
            </span>
          )}
        </div>

        <div className="mb-6">
          <h4 className="text-xl font-semibold text-gray-800 mb-4 leading-relaxed">
            {question.questions[0] || 'No question available'}
          </h4>
        </div>

        <div className="space-y-3">
          {question.options.map((option, index) => {
            const isSelected = userAnswer === index;
            const optionLetters = ['A', 'B', 'C', 'D', 'E', 'F'];

            return (
              <div
                key={index}
                onClick={() => !quizCompleted && handleQuizAnswerSelect(index)}
                className={`flex items-center space-x-4 p-4 border-2 rounded-lg cursor-pointer transition-all duration-200 ${isSelected
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-blue-300 hover:bg-blue-25'
                  } ${quizCompleted ? getOptionResultClass(question, index) : ''}`}
              >
                <div className={`flex-shrink-0 w-8 h-8 rounded-full border-2 flex items-center justify-center font-medium ${isSelected
                  ? 'border-blue-500 bg-blue-500 text-white'
                  : 'border-gray-300 text-gray-600'
                  } ${quizCompleted ? getOptionBadgeClass(question, index) : ''}`}>
                  {optionLetters[index]}
                </div>
                <label className="text-gray-700 cursor-pointer flex-1 text-lg">
                  {option}
                </label>
                {quizCompleted && getOptionResultIcon(question, index)}
              </div>
            );
          })}
        </div>

        {quizCompleted && question.explanation && (
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <h5 className="font-semibold text-gray-800 mb-2 flex items-center">
              <i data-feather="info" className="w-4 h-4 mr-2 text-blue-600"></i>
              Explanation
            </h5>
            <p className="text-gray-600">{question.explanation}</p>
          </div>
        )}
      </div>
    );
  };

  // Quiz Navigation Component
  const QuizNavigation = () => (
    <div className="mt-8 flex justify-between items-center">
      <button
        onClick={prevQuestion}
        disabled={currentQuestionIndex === 0}
        className={`bg-gray-500 text-white font-medium py-3 px-6 rounded-lg transition duration-200 flex items-center space-x-2 ${currentQuestionIndex === 0 ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-600'
          }`}
      >
        <i data-feather="arrow-left" className="w-4 h-4"></i>
        <span>Previous</span>
      </button>

      {currentQuestionIndex < assessments.length - 1 ? (
        <button
          onClick={nextQuestion}
          disabled={userAnswers[currentQuestionIndex] === undefined}
          className={`bg-blue-600 text-white font-medium py-3 px-6 rounded-lg transition duration-200 flex items-center space-x-2 ${userAnswers[currentQuestionIndex] === undefined
            ? 'opacity-50 cursor-not-allowed'
            : 'hover:bg-blue-700'
            }`}
        >
          <span>Next Question</span>
          <i data-feather="arrow-right" className="w-4 h-4"></i>
        </button>
      ) : (
        <button
          onClick={submitQuiz}
          disabled={userAnswers[currentQuestionIndex] === undefined}
          className={`bg-green-600 text-white font-medium py-3 px-6 rounded-lg transition duration-200 flex items-center space-x-2 ${userAnswers[currentQuestionIndex] === undefined
            ? 'opacity-50 cursor-not-allowed'
            : 'hover:bg-green-700'
            }`}
        >
          <i data-feather="check-circle" className="w-4 h-4"></i>
          <span>Submit Quiz</span>
        </button>
      )}
    </div>
  );

  // Quiz Results Component
  const QuizResults = () => {
    const correctAnswers = assessments.filter((assessment, index) =>
      userAnswers[index] === assessment.correct_answer
    ).length;

    const timeSpent = timeStarted && timeCompleted
      ? Math.round((timeCompleted.getTime() - timeStarted.getTime()) / 1000 / 60)
      : 0;

    const getResultMessage = () => {
      if (quizScore >= 80) return { message: "Excellent!", color: "green", icon: "award" };
      if (quizScore >= 60) return { message: "Good Job!", color: "blue", icon: "thumbs-up" };
      return { message: "Keep Practicing!", color: "yellow", icon: "trending-up" };
    };

    const result = getResultMessage();

    return (
      <div className="bg-white border border-gray-200 rounded-xl p-8 text-center">
        <div className={`w-20 h-20 rounded-full bg-${result.color}-100 flex items-center justify-center mx-auto mb-6`}>
          <i data-feather={result.icon} className={`w-10 h-10 text-${result.color}-600`}></i>
        </div>

        <h3 className="text-3xl font-bold text-gray-800 mb-2">{result.message}</h3>
        <p className="text-gray-600 mb-6">You completed the quiz with a score of {quizScore}%</p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 max-w-2xl mx-auto">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{correctAnswers}/{assessments.length}</div>
            <div className="text-sm text-gray-600">Correct Answers</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">{quizScore}%</div>
            <div className="text-sm text-gray-600">Final Score</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">{timeSpent}m</div>
            <div className="text-sm text-gray-600">Time Spent</div>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row justify-center space-y-3 sm:space-y-0 sm:space-x-4">
          <button
            onClick={() => setCurrentQuestionIndex(0)}
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-lg transition duration-200 flex items-center space-x-2 justify-center"
          >
            <i data-feather="eye" className="w-4 h-4"></i>
            <span>Review Answers</span>
          </button>
          <button
            onClick={restartQuiz}
            className="border border-gray-300 hover:bg-gray-50 text-gray-700 font-medium py-3 px-6 rounded-lg transition duration-200 flex items-center space-x-2 justify-center"
          >
            <i data-feather="refresh-cw" className="w-4 h-4"></i>
            <span>Retake Quiz</span>
          </button>
          <button
            onClick={() => setActiveTab('content')}
            className="border border-green-300 hover:bg-green-50 text-green-700 font-medium py-3 px-6 rounded-lg transition duration-200 flex items-center space-x-2 justify-center"
          >
            <i data-feather="check-circle" className="w-4 h-4"></i>
            <span>Continue Learning</span>
          </button>
        </div>
      </div>
    );
  };

  const QuizAnalyticsPanel = () => (
    <div className="bg-white rounded-xl shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-bold text-gray-800">Your Progress</h3>
        <button
          onClick={() => setShowAnalytics(false)}
          className="text-gray-500 hover:text-gray-700"
        >
          <i data-feather="x" className="w-4 h-4"></i>
        </button>
      </div>

      {userAnalytics ? (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-3 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{userAnalytics.total_quizzes_taken}</div>
              <div className="text-xs text-blue-800">Quizzes Taken</div>
            </div>
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{userAnalytics.average_score}%</div>
              <div className="text-xs text-green-800">Avg Score</div>
            </div>
          </div>

          <div className="text-center p-3 bg-purple-50 rounded-lg">
            <div className="text-xl font-bold text-purple-600">{userAnalytics.best_score}%</div>
            <div className="text-xs text-purple-800">Best Score</div>
          </div>

          <div className="border-t pt-3">
            <h4 className="font-semibold text-gray-700 mb-2">Topic Performance</h4>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Strongest:</span>
                <span className="text-green-600 font-medium">{userAnalytics.strongest_topic}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Needs Practice:</span>
                <span className="text-red-600 font-medium">{userAnalytics.weakest_topic}</span>
              </div>
            </div>
          </div>

          <button
            onClick={() => navigate('/progress')}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg transition duration-200 text-sm"
          >
            View Detailed Analytics
          </button>
        </div>
      ) : (
        <div className="text-center py-4">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 mt-2 text-sm">Loading analytics...</p>
        </div>
      )}
    </div>
  );

  // Helper functions for quiz results
  const getOptionResultClass = (question: Assessment, optionIndex: number) => {
    if (optionIndex === question.correct_answer) {
      return 'border-green-500 bg-green-50';
    } else if (optionIndex === userAnswers[assessments.indexOf(question)] && optionIndex !== question.correct_answer) {
      return 'border-red-500 bg-red-50';
    }
    return 'border-gray-200';
  };

  const getOptionBadgeClass = (question: Assessment, optionIndex: number) => {
    if (optionIndex === question.correct_answer) {
      return 'border-green-500 bg-green-500 text-white';
    } else if (optionIndex === userAnswers[assessments.indexOf(question)] && optionIndex !== question.correct_answer) {
      return 'border-red-500 bg-red-500 text-white';
    }
    return 'border-gray-300 text-gray-600';
  };

  const getOptionResultIcon = (question: Assessment, optionIndex: number) => {
    if (optionIndex === question.correct_answer) {
      return <i data-feather="check" className="w-5 h-5 text-green-500 flex-shrink-0"></i>;
    } else if (optionIndex === userAnswers[assessments.indexOf(question)] && optionIndex !== question.correct_answer) {
      return <i data-feather="x" className="w-5 h-5 text-red-500 flex-shrink-0"></i>;
    }
    return null;
  };

  if (loading) {
    return (
      <div className="bg-gray-50 font-sans min-h-screen">
        <Navbar />
        <main className="container mx-auto px-4 py-6">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Loading your learning content...</p>
          </div>
        </main>
      </div>
    );
  }

  if (error || !currentModule) {
    return (
      <div className="bg-gray-50 font-sans min-h-screen">
        <Navbar />
        <main className="container mx-auto px-4 py-6">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <i data-feather="alert-triangle" className="w-12 h-12 text-red-500 mx-auto mb-4"></i>
            <h3 className="text-lg font-medium text-red-800 mb-2">Failed to load content</h3>
            <p className="text-red-600 mb-4">{error}</p>
            <button
              onClick={initializeApp}
              className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition duration-200"
            >
              Try Again
            </button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 font-sans min-h-screen">
      <Navbar />
      <main className="container mx-auto px-4 py-6">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Learning Content */}
          <div className="lg:w-3/4 bg-white rounded-xl shadow-md overflow-hidden">
            {/* Content Tabs */}
            <div className="border-b border-gray-200">
              <nav className="flex -mb-px">
                <button
                  className={`mr-8 py-4 px-1 font-medium text-sm ${activeTab === 'content' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
                  onClick={() => setActiveTab('content')}
                >
                  <i data-feather="play" className="w-4 h-4 mr-2 inline"></i>
                  Visual
                </button>
                <button
                  className={`mr-8 py-4 px-1 font-medium text-sm ${activeTab === 'assessment' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
                  onClick={() => setActiveTab('assessment')}
                >
                  <i data-feather="check-square" className="w-4 h-4 mr-2 inline"></i>
                  Quiz
                </button>

                <button
                  className={`mr-8 py-4 px-1 font-medium text-sm ${activeTab === 'reading' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
                  onClick={() => setActiveTab('reading')}
                >
                  <i data-feather="book-open" className="w-4 h-4 mr-2 inline"></i>
                  Reading
                </button>

                <button
                  className={`mr-8 py-4 px-1 font-medium text-sm ${activeTab === 'project' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
                  onClick={() => setActiveTab('project')}
                >
                  <i data-feather="clipboard" className="w-4 h-4 mr-2 inline"></i>
                  Project
                </button>
              </nav>
            </div>

            {/* Tab Content */}
            <div className="p-6">
              {activeTab === 'content' && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-800 mb-4">{currentModule.title}</h2>
                  <p className="text-gray-600 mb-6">{currentModule.description || 'Learn about this important topic.'}</p>

                  {/* Video Section */}
                  {((currentModule.content?.long_videos?.length || 0) + (currentModule.content?.short_videos?.length || 0)) > 0 && (
                    <div className="mb-8">
                      <h3 className="text-lg font-semibold text-gray-800 mb-3">Video Lecture</h3>

                      {(() => {
                        // Combine long and short videos into one array
                        const videos = [
                          ...(currentModule.content?.long_videos || []),
                          ...(currentModule.content?.short_videos || [])
                        ];

                        if (videos.length === 0) return null;

                        const video = videos[currentVideoIndex];

                        return (
                          <div>
                            <div className="relative pb-[56.25%] h-0 overflow-hidden rounded-lg mb-4">
                              <iframe
                                className="absolute top-0 left-0 w-full h-full"
                                src={video.replace("youtu.be", "www.youtube.com/embed")}
                                title={`Video Lecture ${currentVideoIndex + 1}`}
                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                allowFullScreen
                              ></iframe>
                            </div>

                            {/* Video Navigation */}
                            <div className="flex justify-between mt-2">
                              <button
                                onClick={() => setCurrentVideoIndex(prev => Math.max(prev - 1, 0))}
                                disabled={currentVideoIndex === 0}
                                className="px-4 py-2 bg-gray-200 rounded-lg disabled:opacity-50"
                              >
                                Previous
                              </button>
                              <button
                                onClick={() => setCurrentVideoIndex(prev => Math.min(prev + 1, videos.length - 1))}
                                disabled={currentVideoIndex === videos.length - 1}
                                className="px-4 py-2 bg-gray-200 rounded-lg disabled:opacity-50"
                              >
                                Next
                              </button>
                            </div>

                            <p className="text-sm text-gray-500 mt-1">
                              Video {currentVideoIndex + 1} of {videos.length}
                            </p>
                          </div>
                        );
                      })()}
                    </div>
                  )}

                  {/* Text Content */}
                  {currentModule.content?.sections && (
                    <div className="prose max-w-none">
                      {currentModule.content.sections.map((section: any, index: number) => (
                        <div key={index} className="mb-6">
                          <h3 className="text-lg font-semibold text-gray-800 mb-2">{section.title}</h3>
                          <p className="text-gray-600">{section.content}</p>
                        </div>
                      ))}
                    </div>
                  )}

                  {!currentModule.content?.short_videos && !currentModule.content?.sections && (
                    <div className="text-center py-12">
                      <i data-feather="book-open" className="w-16 h-16 text-gray-400 mx-auto mb-4"></i>
                      <h4 className="text-lg font-medium text-gray-800 mb-2">Content Coming Soon</h4>
                      <p className="text-gray-600">Learning materials will be available here.</p>
                    </div>
                  )}

                  {/* Mark Complete Button */}
                  <div className="mt-8 pt-6 border-t">
                    <button
                      onClick={markModuleComplete}
                      className="bg-green-600 hover:bg-green-700 text-white font-medium py-3 px-6 rounded-lg transition duration-200 flex items-center"
                    >
                      <i data-feather="check-circle" className="w-4 h-4 mr-2"></i>
                      Mark Module as Complete
                    </button>
                  </div>
                </div>
              )}

              {activeTab === 'assessment' && (
                <div>
                  <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold text-gray-800">Assessment</h2>
                  </div>

                  {!quizStarted && !quizCompleted && (
                    <QuizConfigurator />
                  )}

                  {quizStarted && !quizCompleted && assessments.length > 0 && (
                    <>
                      <QuizProgress />
                      <QuizQuestion />
                      <QuizNavigation />
                    </>
                  )}

                  {quizCompleted && (
                    <QuizResults />
                  )}

                  {!quizStarted && !quizCompleted && assessments.length === 0 && (
                    <div className="text-center py-12">
                      <i data-feather="clipboard" className="w-16 h-16 text-gray-400 mx-auto mb-4"></i>
                      <h4 className="text-lg font-medium text-gray-800 mb-2">No Assessment Available</h4>
                      <p className="text-gray-600 mb-4">Configure and generate an AI-powered quiz to test your knowledge.</p>
                    </div>
                  )}
                </div>
              )}

              {activeTab === "project" && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-800 mb-4">Projects</h2>
                  {currentModule.content?.projects?.map((p, i) => (
                    <div key={i} className="mb-4 p-4 border rounded-lg bg-gray-50">
                      <h3 className="font-semibold text-gray-800">{p.title}</h3>
                      <p className="text-gray-600">{p.description}</p>
                      {p.link && (
                        <a
                          href={p.link}
                          target="_blank"
                          className="text-blue-600 hover:underline mt-2 inline-block"
                        >
                          Open Project
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {activeTab === "reading" && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-800 mb-4">
                    Reading Materials
                  </h2>
                  {currentModule.content?.reading_materials?.map((r, i) => (
                    <div key={i} className="mb-4 p-4 border rounded-lg bg-gray-50">
                      <h3 className="font-semibold text-gray-800">{r.title}</h3>
                      <p className="text-gray-600">{r.content}</p>
                      {r.link && (
                        <a
                          href={r.link}
                          target="_blank"
                          className="text-blue-600 hover:underline mt-2 inline-block"
                        >
                          Open Resource
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              )}


            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:w-1/4 space-y-6">
            {/* Confidence Check */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="font-bold text-gray-800 mb-4">How confident are you?</h3>
              <p className="text-sm text-gray-600 mb-4">Rate your understanding of this module</p>

              <div className="flex justify-between mb-4">
                {[1, 2, 3, 4, 5].map((rating) => (
                  <button
                    key={rating}
                    onClick={() => handleConfidenceSelect(rating)}
                    className={`w-12 h-12 rounded-full transition-all ${confidenceRating === rating
                      ? 'bg-blue-600 text-white scale-125'
                      : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                      }`}
                  >
                    {rating}
                  </button>
                ))}
              </div>

              {confidenceRating && (
                <div className="text-center text-sm text-gray-600">
                  Selected: {confidenceRating}/5
                </div>
              )}
            </div>

            {/* Progress Analytics */}
            {showAnalytics ? (
              <QuizAnalyticsPanel />
            ) : (
              <div className="bg-white rounded-xl shadow-md p-6">
                <h3 className="font-bold text-gray-800 mb-4">Your Progress</h3>
                <p className="text-sm text-gray-600 mb-4">Track your learning journey</p>
                <button
                  onClick={fetchUserAnalytics}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition duration-200 flex items-center justify-center"
                >
                  <i data-feather="bar-chart" className="w-4 h-4 mr-2"></i>
                  View Analytics
                </button>
              </div>
            )}

            {/* Module Info */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="font-bold text-gray-800 mb-4">Module Info</h3>
              <div className="space-y-3 text-sm">
                <div className="flex items-center text-gray-600">
                  <i data-feather="clock" className="w-4 h-4 mr-2"></i>
                  <span>30-45 minutes</span>
                </div>
                <div className="flex items-center text-gray-600">
                  <i data-feather="bar-chart" className="w-4 h-4 mr-2"></i>
                  <span>{currentModule.difficulty || 'All Levels'}</span>
                </div>
                {currentModule.skills && currentModule.skills.length > 0 && (
                  <div className="pt-3 border-t">
                    <p className="text-gray-700 font-medium mb-2">Skills Covered:</p>
                    <div className="flex flex-wrap gap-1">
                      {currentModule.skills.map((skill: string, idx: number) => (
                        <span key={idx} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Navigation */}
            <div className="bg-white rounded-xl shadow-md p-6 space-y-3">
              <button
                onClick={() => navigate('/learning')}
                className="w-full bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-4 rounded-lg transition duration-200 flex items-center justify-center"
              >
                <i data-feather="arrow-left" className="w-4 h-4 mr-2"></i>
                Back to Path
              </button>
              <button
                onClick={() => navigate('/progress')}
                className="w-full border border-blue-600 text-blue-600 hover:bg-blue-50 font-medium py-2 px-4 rounded-lg transition duration-200 flex items-center justify-center"
              >
                <i data-feather="trending-up" className="w-4 h-4 mr-2"></i>
                View Progress
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Pathways;