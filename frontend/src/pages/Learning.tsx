import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import * as feather from "feather-icons";
import Navbar from "@/components/Navbar";

interface Module {
  id: string;
  title: string;
  type: string;
  estimated_time: number;
  load: string;
  difficulty: number;
  prerequisites: string[];
  subnodes: string[];
  subtopics: string[];
  resources: any;
  embedding: number[];
  description?: string;
  skills?: string[];
  completed?: boolean;
}

interface LearningPath {
  path_id: number;
  title: string;
  description: string;
  learner_type: string;
  time_availability: string;
  learning_domain: string;
  study_weeks: number;
  path_data: Module[];
  weekly_schedule: any;
  stats: {
    total_hours_used: number;
    total_hours_available: number;
    utilization_percentage: number;
    nodes_completed: number;
    total_nodes: number;
    weeks: number;
    hours_per_week: number;
    expected_completion: number;
    learning_domain: string;
  };
  current_week: number;
  completed_nodes: string[];
  progress_percentage: number;
  created_at: string;
  is_active: boolean;
}

const Learning = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [learningPath, setLearningPath] = useState<LearningPath | null>(null);
  const [userId, setUserId] = useState<number | null>(null);

  useEffect(() => {
    // Get user ID from authentication context or localStorage
    const storedUserId = localStorage.getItem('userId');
    if (storedUserId) {
      setUserId(parseInt(storedUserId));
    } else {
      // If no user ID, redirect to login
      navigate('/login');
    }
  }, [navigate]);

  useEffect(() => {
    if (userId) {
      loadLearningPath();
    }
  }, [userId]);

  useEffect(() => {
    if (!loading) {
      feather.replace();
    }
  }, [loading]);

  const loadLearningPath = async () => {
    try {
      setLoading(true);
      setError('');

      if (!userId) {
        setError('User ID not found');
        setLoading(false);
        return;
      }

      // Fetch current learning path from backend
      const response = await fetch(`http://localhost:8000/generate-path/user/${userId}/current-path`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch learning path: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success && data.has_path) {
        const path = data.path;
        
        // Transform backend data to match frontend interface
        const transformedPath: LearningPath = {
          path_id: path.id,
          title: path.title,
          description: path.description,
          learner_type: path.learner_type,
          time_availability: path.time_availability,
          learning_domain: path.learning_domain,
          study_weeks: path.study_weeks,
          path_data: path.path_data || [],
          weekly_schedule: path.weekly_schedule || {},
          stats: path.stats || {},
          current_week: path.current_week || 1,
          completed_nodes: path.completed_nodes || [],
          progress_percentage: path.progress_percentage || 0,
          created_at: path.created_at,
          is_active: path.is_active
        };

        setLearningPath(transformedPath);
        
        // Also store in localStorage for offline access
        localStorage.setItem('currentLearningPath', JSON.stringify(transformedPath));
      } else {
        setError('No active learning path found. Please generate a new path.');
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error loading learning path:', err);
      setError('Failed to load your learning path. Please try again.');
      setLoading(false);
    }
  };

  const startModule = (moduleIndex: number) => {
    if (!learningPath) return;
    
    const module = learningPath.path_data[moduleIndex];
    localStorage.setItem('currentModule', moduleIndex.toString());
    localStorage.setItem('currentModuleData', JSON.stringify(module));
    navigate('/pathways');
  };

  const markModuleComplete = async (moduleId: string) => {
    try {
      if (!userId || !learningPath) return;

      const response = await fetch(
        `http://localhost:8000/generate-path/user/${userId}/path/${learningPath.path_id}/complete-node`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ node_id: moduleId })
        }
      );

      if (response.ok) {
        // Refresh the learning path to get updated progress
        await loadLearningPath();
      } else {
        throw new Error('Failed to mark module as complete');
      }
    } catch (err) {
      console.error('Error marking module complete:', err);
      setError('Failed to update progress. Please try again.');
    }
  };

  const generateNewPath = () => {
    navigate('/path-generator'); // Navigate to path generation page
  };

  const getModuleDuration = (module: Module) => {
    if (module.estimated_time > 10) return '60-90 min';
    if (module.estimated_time > 5) return '30-45 min';
    return '15-30 min';
  };

  const getDifficultyText = (difficulty: number) => {
    switch (difficulty) {
      case 1:
      case 2:
        return 'Beginner';
      case 3:
      case 4:
        return 'Intermediate';
      case 5:
      case 6:
        return 'Advanced';
      default:
        return 'Expert';
    }
  };

  const getSkillsFromModule = (module: Module): string[] => {
    // Extract skills from subtopics or generate based on module content
    if (module.subtopics && module.subtopics.length > 0) {
      return module.subtopics.slice(0, 3);
    }
    
    // Fallback skills based on module title/type
    const skillsMap: { [key: string]: string[] } = {
      'html': ['HTML5', 'Semantic HTML', 'Web Structure'],
      'css': ['CSS3', 'Styling', 'Layout'],
      'javascript': ['JavaScript', 'Programming', 'Web Development'],
      'python': ['Python', 'Programming', 'Data Science'],
      'react': ['React', 'Frontend', 'Components'],
      'node': ['Node.js', 'Backend', 'JavaScript'],
      'machine learning': ['ML', 'AI', 'Data Analysis'],
      'data science': ['Data Analysis', 'Statistics', 'Python']
    };

    const moduleTitle = module.title.toLowerCase();
    for (const [key, skills] of Object.entries(skillsMap)) {
      if (moduleTitle.includes(key)) {
        return skills;
      }
    }

    return ['Learning', 'Skills', 'Development'];
  };

  const transformWeeklySchedule = (schedule: any) => {
    if (!schedule || Object.keys(schedule).length === 0) {
      // Generate a default weekly schedule based on path data
      if (learningPath?.path_data) {
        const weeks: any[] = [];
        const modulesPerWeek = Math.ceil(learningPath.path_data.length / learningPath.study_weeks);
        
        for (let week = 1; week <= learningPath.study_weeks; week++) {
          const startIndex = (week - 1) * modulesPerWeek;
          const weekModules = learningPath.path_data.slice(startIndex, startIndex + modulesPerWeek);
          
          if (weekModules.length > 0) {
            weeks.push({
              week: week,
              estimated_hours: `${weekModules.reduce((sum, mod) => sum + mod.estimated_time, 0)}h`,
              modules: weekModules.map(mod => mod.title),
              focus_areas: weekModules.flatMap(mod => mod.subtopics || []).slice(0, 3)
            });
          }
        }
        return weeks;
      }
      return [];
    }

    // Transform backend schedule to frontend format
    return Object.entries(schedule).map(([weekKey, weekModules]: [string, any]) => ({
      week: parseInt(weekKey.replace('Week ', '')),
      estimated_hours: `${weekModules.reduce((sum: number, mod: any) => sum + mod.estimated_time, 0)}h`,
      modules: weekModules.map((mod: any) => mod.title),
      focus_areas: weekModules.flatMap((mod: any) => mod.subtopics || []).slice(0, 3)
    }));
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
          <div className="max-w-2xl mx-auto">
            <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center mb-6">
              <i data-feather="alert-triangle" className="w-12 h-12 text-red-500 mx-auto mb-4"></i>
              <h3 className="text-lg font-medium text-red-800 mb-2">No Learning Path Found</h3>
              <p className="text-red-600 mb-4">{error}</p>
              <div className="flex gap-4 justify-center">
                <button 
                  onClick={loadLearningPath}
                  className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition duration-200"
                >
                  Try Again
                </button>
                <button 
                  onClick={generateNewPath}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition duration-200"
                >
                  Generate New Path
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    );
  }

  const completionPercent = learningPath.progress_percentage;
  const weeklySchedule = transformWeeklySchedule(learningPath.weekly_schedule);

  return (
    <div className="bg-gray-50 font-sans min-h-screen">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12" data-aos="fade-up">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            {learningPath.title}
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            {learningPath.description}
          </p>
        </div>

        {/* Learning Path Overview */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
          {/* Path Details */}
          <div className="lg:col-span-2" data-aos="fade-right">
            <div className="bg-white rounded-xl shadow-md p-8 transition-all hover:-translate-y-1">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-800">Your Learning Path</h2>
                <div className="flex gap-2">
                  <span className="bg-blue-100 text-blue-800 text-sm font-medium px-3 py-1 rounded-full">
                    {learningPath.learner_type}
                  </span>
                  <span className="bg-green-100 text-green-800 text-sm font-medium px-3 py-1 rounded-full">
                    {learningPath.learning_domain.replace('_', ' ')}
                  </span>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <i data-feather="clock" className="w-8 h-8 text-blue-600 mx-auto mb-2"></i>
                  <h3 className="font-semibold text-gray-700">Duration</h3>
                  <p className="text-gray-600">{learningPath.stats.total_hours_used}h total</p>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <i data-feather="book" className="w-8 h-8 text-green-600 mx-auto mb-2"></i>
                  <h3 className="font-semibold text-gray-700">Modules</h3>
                  <p className="text-gray-600">{learningPath.stats.nodes_completed}/{learningPath.stats.total_nodes}</p>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <i data-feather="target" className="w-8 h-8 text-purple-600 mx-auto mb-2"></i>
                  <h3 className="font-semibold text-gray-700">Progress</h3>
                  <p className="text-gray-600">{completionPercent}%</p>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <i data-feather="calendar" className="w-8 h-8 text-orange-600 mx-auto mb-2"></i>
                  <h3 className="font-semibold text-gray-700">Time</h3>
                  <p className="text-gray-600">{learningPath.time_availability.replace('_', ' ')}</p>
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
              <div className="border-t pt-6">
                <h4 className="font-semibold text-gray-800 mb-3">Personalized For You</h4>
                <div className="flex flex-wrap gap-2">
                  <span className="bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full">
                    {learningPath.learner_type} Level
                  </span>
                  <span className="bg-green-100 text-green-800 text-sm px-3 py-1 rounded-full">
                    {learningPath.time_availability.replace('_', ' ')} Pace
                  </span>
                  <span className="bg-purple-100 text-purple-800 text-sm px-3 py-1 rounded-full">
                    {learningPath.learning_domain.replace('_', ' ')} Focus
                  </span>
                  <span className="bg-orange-100 text-orange-800 text-sm px-3 py-1 rounded-full">
                    {learningPath.study_weeks} Weeks
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Weekly Schedule */}
          <div data-aos="fade-left">
            <div className="bg-white rounded-xl shadow-md p-6 sticky top-8">
              <h3 className="font-bold text-gray-800 mb-4">Weekly Schedule</h3>
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {weeklySchedule.length > 0 ? (
                  weeklySchedule.map((week, index) => (
                    <div 
                      key={index} 
                      className={`border-l-4 pl-4 py-2 ${
                        week.week === learningPath.current_week 
                          ? 'border-blue-500 bg-blue-50' 
                          : 'border-gray-300'
                      }`}
                    >
                      <div className="flex justify-between items-center mb-1">
                        <h4 className="font-semibold text-gray-800">
                          Week {week.week}
                          {week.week === learningPath.current_week && (
                            <span className="ml-2 text-xs bg-blue-500 text-white px-2 py-1 rounded">Current</span>
                          )}
                        </h4>
                        <span className="text-xs text-gray-500">{week.estimated_hours}</span>
                      </div>
                      <ul className="text-sm text-gray-600 space-y-1">
                        {week.modules?.map((module: string, idx: number) => (
                          <li key={idx}>• {module}</li>
                        ))}
                      </ul>
                      {week.focus_areas && week.focus_areas.length > 0 && (
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
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-800">Learning Modules</h2>
            <span className="text-gray-600">
              {learningPath.completed_nodes.length} of {learningPath.path_data.length} completed
            </span>
          </div>
          <div className="space-y-4">
            {learningPath.path_data && learningPath.path_data.length > 0 ? (
              learningPath.path_data.map((module, index) => {
                const isCompleted = learningPath.completed_nodes.includes(module.id);
                const isCurrent = !isCompleted && 
                  (index === 0 || learningPath.completed_nodes.includes(learningPath.path_data[index - 1].id));
                
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
                
                const skills = getSkillsFromModule(module);
                
                return (
                  <div 
                    key={module.id}
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
                        <p className="text-white text-opacity-80">
                          {module.subtopics && module.subtopics.length > 0 
                            ? module.subtopics.slice(0, 2).join(' • ')
                            : 'Start your learning journey'
                          }
                        </p>
                        <div className="flex items-center space-x-4 mt-2">
                          <span className="text-white text-opacity-80 text-sm">
                            <i data-feather="clock" className="w-3 h-3 inline mr-1"></i>
                            {getModuleDuration(module)}
                          </span>
                          <span className="text-white text-opacity-80 text-sm">
                            <i data-feather="bar-chart" className="w-3 h-3 inline mr-1"></i>
                            {getDifficultyText(module.difficulty)}
                          </span>
                          {skills.length > 0 && (
                            <div className="flex flex-wrap gap-1">
                              {skills.slice(0, 2).map((skill, idx) => (
                                <span key={idx} className="bg-white bg-opacity-20 text-xs px-2 py-1 rounded">{skill}</span>
                              ))}
                              {skills.length > 2 && (
                                <span className="bg-white bg-opacity-20 text-xs px-2 py-1 rounded">+{skills.length - 2} more</span>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {isCompleted && (
                        <button 
                          onClick={() => markModuleComplete(module.id)}
                          className="bg-white bg-opacity-20 hover:bg-opacity-30 text-white font-medium py-2 px-3 rounded-lg transition duration-200 text-sm"
                        >
                          <i data-feather="check-circle" className="w-4 h-4"></i>
                        </button>
                      )}
                      <button 
                        onClick={() => startModule(index)}
                        className="bg-white bg-opacity-20 hover:bg-opacity-30 text-white font-medium py-2 px-4 rounded-lg transition duration-200 flex items-center"
                      >
                        {buttonText} <i data-feather="arrow-right" className="w-4 h-4 ml-1"></i>
                      </button>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="text-center py-12 bg-white rounded-xl">
                <i data-feather="book" className="w-16 h-16 text-gray-400 mx-auto mb-4"></i>
                <h4 className="text-lg font-medium text-gray-800 mb-2">No Modules Available</h4>
                <p className="text-gray-600 mb-4">There are no modules in this learning path yet.</p>
                <button 
                  onClick={generateNewPath}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition duration-200"
                >
                  Generate Learning Path
                </button>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default Learning;