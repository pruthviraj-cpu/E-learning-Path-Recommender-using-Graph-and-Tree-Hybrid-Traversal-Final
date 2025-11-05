import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import * as feather from "feather-icons";
import Navbar from "@/components/Navbar";
import { toast } from "@/hooks/use-toast";

const Pathways = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentModule, setCurrentModule] = useState<any>(null);
  const [activeTab, setActiveTab] = useState('content');
  const [confidenceRating, setConfidenceRating] = useState<number | null>(null);
  const [assessments, setAssessments] = useState<any[]>([]);
  const [userAnswers, setUserAnswers] = useState<{ [key: number]: number }>({});
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    initializeApp();
  }, []);

  useEffect(() => {
    if (!loading) {
      feather.replace();
    }
  }, [loading, activeTab]);

  const initializeApp = async () => {
    try {
      const storedPath = localStorage.getItem('currentLearningPath');
      const storedModuleIndex = localStorage.getItem('currentModule');
      
      // if (!storedPath) {
      //   navigate('/');
      //   return;
      // }

      const path = JSON.parse(storedPath);
      const moduleIndex = storedModuleIndex ? parseInt(storedModuleIndex) : path.progress?.current_module || 0;
      
      if (path.modules && path.modules[moduleIndex]) {
        const module = path.modules[moduleIndex];
        
        // Fetch module content if we have path_id and module title
        if (path.path_id && module.title) {
          try {
            const response = await fetch(`http://localhost:8000/learningpaths/${path.path_id}/modules/${module.title}`);
            if (response.ok) {
              const moduleData = await response.json();
              setCurrentModule(moduleData);
              
              if (moduleData.assessments) {
                setAssessments(moduleData.assessments);
              }
            } else {
              setCurrentModule(module);
            }
          } catch (err) {
            console.error('Error fetching module details:', err);
            setCurrentModule(module);
          }
        } else {
          setCurrentModule(module);
        }
      } else {
        setError('Module not found');
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error loading content:', err);
      setError('Failed to load learning content');
      setLoading(false);
    }
  };

  const handleConfidenceSelect = (rating: number) => {
    setConfidenceRating(rating);
  };

  const submitConfidence = async () => {
    if (confidenceRating === null) return;

    toast({
      title: "Progress Saved",
      description: "Your confidence rating has been recorded.",
    });
  };

  const handleAnswerSelect = (questionIndex: number, optionIndex: number) => {
    if (!submitted) {
      setUserAnswers({
        ...userAnswers,
        [questionIndex]: optionIndex
      });
    }
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
    
    toast({
      title: "Assessment Complete!",
      description: `You scored ${score}%. Great job!`,
    });
  };

  const generateAIQuiz = async () => {
    toast({
      title: "Generating Quiz",
      description: "Creating AI-powered questions for you...",
    });

    try {
      const response = await fetch('http://localhost:8000/ai/generate-quiz', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: currentModule.title,
          num_questions: 5,
          difficulty: 'beginner',
          question_types: ["mcq", "true_false"]
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
    }
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
                  Content
                </button>
                <button 
                  className={`mr-8 py-4 px-1 font-medium text-sm ${activeTab === 'assessment' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
                  onClick={() => setActiveTab('assessment')}
                >
                  <i data-feather="check-square" className="w-4 h-4 mr-2 inline"></i>
                  Assessment
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
                  {currentModule.content?.video_url && (
                    <div className="mb-8">
                      <h3 className="text-lg font-semibold text-gray-800 mb-3">Video Lecture</h3>
                      <div className="relative pb-[56.25%] h-0 overflow-hidden rounded-lg">
                        <iframe
                          className="absolute top-0 left-0 w-full h-full"
                          src={currentModule.content.video_url}
                          title="Video Lecture"
                          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                          allowFullScreen
                        ></iframe>
                      </div>
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

                  {!currentModule.content?.video_url && !currentModule.content?.sections && (
                    <div className="text-center py-12">
                      <i data-feather="book-open" className="w-16 h-16 text-gray-400 mx-auto mb-4"></i>
                      <h4 className="text-lg font-medium text-gray-800 mb-2">Content Coming Soon</h4>
                      <p className="text-gray-600">Learning materials will be available here.</p>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'assessment' && (
                <div>
                  <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold text-gray-800">Assessment</h2>
                    {assessments.length === 0 && (
                      <button 
                        onClick={generateAIQuiz}
                        className="bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-lg transition duration-200 flex items-center"
                      >
                        <i data-feather="zap" className="w-4 h-4 mr-2"></i>
                        Generate AI Quiz
                      </button>
                    )}
                  </div>

                  {assessments.length > 0 ? (
                    <div className="space-y-6">
                      {assessments.map((assessment, qIndex) => (
                        <div key={qIndex} className="bg-white border border-gray-200 rounded-lg p-6">
                          <h4 className="font-semibold text-gray-800 mb-4">
                            Question {qIndex + 1}: {assessment.questions?.[0] || 'Question'}
                          </h4>
                          <div className="space-y-2">
                            {assessment.options?.map((option: string, oIndex: number) => {
                              const isSelected = userAnswers[qIndex] === oIndex;
                              const isCorrect = assessment.correct_answer === oIndex;
                              let optionClass = 'border-gray-200 hover:border-blue-300';
                              
                              if (submitted) {
                                if (isCorrect) {
                                  optionClass = 'bg-green-500 text-white border-green-500';
                                } else if (isSelected && !isCorrect) {
                                  optionClass = 'bg-red-500 text-white border-red-500';
                                }
                              } else if (isSelected) {
                                optionClass = 'bg-blue-500 text-white border-blue-500';
                              }

                              return (
                                <button
                                  key={oIndex}
                                  onClick={() => handleAnswerSelect(qIndex, oIndex)}
                                  className={`w-full text-left p-4 border rounded-lg transition duration-200 ${optionClass}`}
                                  disabled={submitted}
                                >
                                  {option}
                                </button>
                              );
                            })}
                          </div>
                          {submitted && assessment.explanation && (
                            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                              <p className="text-sm text-gray-700">
                                <strong>Explanation:</strong> {assessment.explanation}
                              </p>
                            </div>
                          )}
                        </div>
                      ))}
                      
                      {!submitted && (
                        <button 
                          onClick={submitAssessment}
                          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition duration-200"
                        >
                          Submit Assessment
                        </button>
                      )}
                    </div>
                  ) : (
                    <div className="text-center py-12">
                      <i data-feather="clipboard" className="w-16 h-16 text-gray-400 mx-auto mb-4"></i>
                      <h4 className="text-lg font-medium text-gray-800 mb-2">No Assessment Available</h4>
                      <p className="text-gray-600 mb-4">Generate an AI-powered quiz to test your knowledge.</p>
                    </div>
                  )}
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
                    className={`w-12 h-12 rounded-full transition-all ${
                      confidenceRating === rating 
                        ? 'bg-blue-600 text-white scale-125' 
                        : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                    }`}
                  >
                    {rating}
                  </button>
                ))}
              </div>
              
              {confidenceRating && (
                <button 
                  onClick={submitConfidence}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition duration-200"
                >
                  Save Rating
                </button>
              )}
            </div>

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
            <div className="bg-white rounded-xl shadow-md p-6">
              <button 
                onClick={() => navigate('/learning')}
                className="w-full bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-4 rounded-lg transition duration-200 flex items-center justify-center"
              >
                <i data-feather="arrow-left" className="w-4 h-4 mr-2"></i>
                Back to Path
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Pathways;