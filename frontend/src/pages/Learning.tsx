import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import * as feather from "feather-icons";
import Navbar from "@/components/Navbar";

interface Module {
  title: string;
  description?: string;
  difficulty?: string;
  skills?: string[];
  completed?: boolean;
}

interface LearningPath {
  path_id: string;
  recommended_path: string;
  estimated_completion_time: string;
  modules: Module[];
  progress: {
    current_module: number;
    completion_percent: number;
  };
  confidence_score?: number;
  weekly_schedule?: any[];
  personalization_factors?: string[];
}

const Learning = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [learningPath, setLearningPath] = useState<LearningPath | null>(null);

  useEffect(() => {
    loadLearningPath();
  }, []);

  useEffect(() => {
    if (!loading) {
      feather.replace();
    }
  }, [loading]);

  const loadLearningPath = async () => {
    try {
      const storedPath = localStorage.getItem('currentLearningPath');
      
      // if (!storedPath) {
      //   navigate('/');
      //   return;
      // }

      const path = JSON.parse(storedPath);
      setLearningPath(path);
      setLoading(false);
    } catch (err) {
      console.error('Error loading learning path:', err);
      setError('Failed to load your learning path. Please try again.');
      setLoading(false);
    }
  };

  const startModule = (moduleIndex: number) => {
    localStorage.setItem('currentModule', moduleIndex.toString());
    navigate('/pathways');
  };

  const getModuleDuration = (module: Module) => {
    if (module.skills && module.skills.length > 3) return '60-90 min';
    return '30-45 min';
  };

  if (loading) {
    return (
      <div className="bg-gray-50 font-sans min-h-screen">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Loading your learning path...</p>
          </div>
        </main>
      </div>
    );
  }

  if (error || !learningPath) {
    return (
      <div className="bg-gray-50 font-sans min-h-screen">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <i data-feather="alert-triangle" className="w-12 h-12 text-red-500 mx-auto mb-4"></i>
            <h3 className="text-lg font-medium text-red-800 mb-2">Failed to load learning path</h3>
            <p className="text-red-600 mb-4">{error}</p>
            <button 
              onClick={loadLearningPath}
              className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition duration-200"
            >
              Try Again
            </button>
          </div>
        </main>
      </div>
    );
  }

  const completionPercent = learningPath.progress?.completion_percent || 0;

  return (
    <div className="bg-gray-50 font-sans min-h-screen">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12" data-aos="fade-up">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            {learningPath.recommended_path}
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Your customized learning journey
          </p>
        </div>

        {/* Learning Path Overview */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
          {/* Path Details */}
          <div className="lg:col-span-2" data-aos="fade-right">
            <div className="bg-white rounded-xl shadow-md p-8 transition-all hover:-translate-y-1">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-800">Your Learning Path</h2>
                <span className="bg-blue-100 text-blue-800 text-sm font-medium px-3 py-1 rounded-full">
                  {learningPath.confidence_score || 85}% Match
                </span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <i data-feather="clock" className="w-8 h-8 text-blue-600 mx-auto mb-2"></i>
                  <h3 className="font-semibold text-gray-700">Duration</h3>
                  <p className="text-gray-600">{learningPath.estimated_completion_time}</p>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <i data-feather="book" className="w-8 h-8 text-green-600 mx-auto mb-2"></i>
                  <h3 className="font-semibold text-gray-700">Modules</h3>
                  <p className="text-gray-600">{learningPath.modules?.length || 0} modules</p>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <i data-feather="target" className="w-8 h-8 text-purple-600 mx-auto mb-2"></i>
                  <h3 className="font-semibold text-gray-700">Progress</h3>
                  <p className="text-gray-600">{completionPercent}%</p>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="mb-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Overall Progress</span>
                  <span className="text-sm font-medium text-blue-600">{completionPercent}% complete</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className="bg-blue-600 h-3 rounded-full transition-all duration-500"
                    style={{ width: `${completionPercent}%` }}
                  ></div>
                </div>
              </div>

              {/* Personalization Factors */}
              {learningPath.personalization_factors && learningPath.personalization_factors.length > 0 && (
                <div className="border-t pt-6">
                  <h4 className="font-semibold text-gray-800 mb-3">Personalized For You</h4>
                  <div className="flex flex-wrap gap-2">
                    {learningPath.personalization_factors.map((factor, index) => (
                      <span key={index} className="bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full">
                        {factor}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Weekly Schedule */}
          <div data-aos="fade-left">
            <div className="bg-white rounded-xl shadow-md p-6 sticky top-8">
              <h3 className="font-bold text-gray-800 mb-4">Weekly Schedule</h3>
              <div className="space-y-4">
                {learningPath.weekly_schedule && learningPath.weekly_schedule.length > 0 ? (
                  learningPath.weekly_schedule.map((week, index) => (
                    <div key={index} className="border-l-4 border-blue-500 pl-4 py-2">
                      <div className="flex justify-between items-center mb-1">
                        <h4 className="font-semibold text-gray-800">Week {week.week}</h4>
                        <span className="text-xs text-gray-500">{week.estimated_hours}</span>
                      </div>
                      <ul className="text-sm text-gray-600 space-y-1">
                        {week.modules?.map((module: string, idx: number) => (
                          <li key={idx}>• {module}</li>
                        ))}
                      </ul>
                      {week.focus_areas && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {week.focus_areas.map((area: string, idx: number) => (
                            <span key={idx} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                              {area}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 text-center py-4">Weekly schedule not available</p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Modules List */}
        <div data-aos="fade-up">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Learning Modules</h2>
          <div className="space-y-4">
            {learningPath.modules && learningPath.modules.length > 0 ? (
              learningPath.modules.map((module, index) => {
                const isCompleted = index < (learningPath.progress?.current_module || 0);
                const isCurrent = index === (learningPath.progress?.current_module || 0);
                const isUpcoming = index > (learningPath.progress?.current_module || 0);
                
                let moduleClass = 'bg-gradient-to-r from-gray-500 to-gray-600';
                let statusText = 'Upcoming';
                let buttonText = 'Start';
                
                if (isCompleted) {
                  moduleClass = 'bg-gradient-to-r from-green-500 to-green-600';
                  statusText = 'Completed';
                  buttonText = 'Review';
                } else if (isCurrent) {
                  moduleClass = 'bg-gradient-to-r from-blue-500 to-blue-700';
                  statusText = 'Current';
                  buttonText = 'Continue';
                }
                
                return (
                  <div 
                    key={index}
                    className={`flex items-center justify-between p-6 rounded-lg text-white transition-all hover:-translate-y-1 ${moduleClass}`}
                  >
                    <div className="flex items-center space-x-4 flex-1">
                      <div className="w-12 h-12 rounded-full bg-white bg-opacity-20 flex items-center justify-center font-bold text-lg">
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="font-semibold text-lg">{module.title}</h3>
                          <span className="bg-white bg-opacity-20 text-xs px-2 py-1 rounded">{statusText}</span>
                        </div>
                        <p className="text-white text-opacity-80">{module.description || 'No description available'}</p>
                        <div className="flex items-center space-x-4 mt-2">
                          <span className="text-white text-opacity-80 text-sm">
                            <i data-feather="clock" className="w-3 h-3 inline mr-1"></i>
                            {getModuleDuration(module)}
                          </span>
                          <span className="text-white text-opacity-80 text-sm">
                            <i data-feather="bar-chart" className="w-3 h-3 inline mr-1"></i>
                            {module.difficulty || 'All Levels'}
                          </span>
                          {module.skills && module.skills.length > 0 && (
                            <div className="flex flex-wrap gap-1">
                              {module.skills.slice(0, 2).map((skill, idx) => (
                                <span key={idx} className="bg-white bg-opacity-20 text-xs px-2 py-1 rounded">{skill}</span>
                              ))}
                              {module.skills.length > 2 && (
                                <span className="bg-white bg-opacity-20 text-xs px-2 py-1 rounded">+{module.skills.length - 2} more</span>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                    <button 
                      onClick={() => startModule(index)}
                      className="bg-white bg-opacity-20 hover:bg-opacity-30 text-white font-medium py-2 px-4 rounded-lg transition duration-200 flex items-center"
                    >
                      {buttonText} <i data-feather="arrow-right" className="w-4 h-4 ml-1"></i>
                    </button>
                  </div>
                );
              })
            ) : (
              <div className="text-center py-12 bg-white rounded-xl">
                <i data-feather="book" className="w-16 h-16 text-gray-400 mx-auto mb-4"></i>
                <h4 className="text-lg font-medium text-gray-800 mb-2">No Modules Available</h4>
                <p className="text-gray-600">There are no modules in this learning path yet.</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default Learning;