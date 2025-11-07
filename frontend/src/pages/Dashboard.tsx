import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import * as feather from "feather-icons";
import Navbar from "@/components/Navbar";
import VantaBackground from "@/components/Vanta Background";

interface Path {
  id: number;
  title: string;
  type: string;
  difficulty: number;
  is_active?: boolean;
  subnodes?: string[];
  created_at?: string;
  resources?: Record<string, any>;
}

interface LearningPath {
  path_id: number;
  title: string;
  description: string;
  learner_type: string;
  time_availability: string;
  learning_domain: string;
  study_weeks: number;
  path_data: any[];
  weekly_schedule: any;
  stats: any;
  current_week: number;
  completed_nodes: string[];
  progress_percentage: number;
  created_at: string;
  is_active: boolean;
}

const Dashboard = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState<any>(null);
  const [enrolledPaths, setEnrolledPaths] = useState<Path[]>([]);
  const [availablePaths, setAvailablePaths] = useState<Path[]>([]);
  const [currentLearningPath, setCurrentLearningPath] = useState<LearningPath | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedUser = localStorage.getItem("userData");
    if (!storedUser) {
      navigate("/login");
      return;
    }

    const user = JSON.parse(storedUser);
    setUserData(user);

    loadUserData(user.id);
    feather.replace();
  }, [navigate]);

  useEffect(() => {
    feather.replace();
  });

  const loadUserData = async (userId: number) => {
    try {
      setLoading(true);
      
      // Load current learning path (new system)
      const currentPathResponse = await fetch(`http://localhost:8000/generate-path/user/${userId}/current-path`);
      const currentPathData = await currentPathResponse.json();
      
      if (currentPathData.success && currentPathData.has_path) {
        setCurrentLearningPath(currentPathData.path);
      }

      // Load all user paths (new system)
      const allPathsResponse = await fetch(`http://localhost:8000/generate-path/user/${userId}/all-paths`);
      const allPathsData = await allPathsResponse.json();
      
      if (allPathsData.success) {
        // Transform the new path data to match the old interface for compatibility
        const transformedPaths: Path[] = allPathsData.paths.map((path: any) => ({
          id: path.id,
          title: path.title,
          type: "generated_path",
          difficulty: path.difficulty || 5,
          is_active: path.is_active,
          subnodes: path.stats ? [`${path.stats.nodes_completed || 0} of ${path.stats.total_nodes || 0} completed`] : [],
          created_at: path.created_at
        }));
        setEnrolledPaths(transformedPaths);
      }

    } catch (err) {
      console.error("Error loading user data:", err);
    } finally {
      setLoading(false);
    }
  };

  const continueLearning = () => {
    if (currentLearningPath) {
      localStorage.setItem("currentLearningPath", JSON.stringify(currentLearningPath));
      navigate("/learning");
    } else if (enrolledPaths.length > 0) {
      // Fallback to old system if no current path
      const activePath = enrolledPaths.find((p) => p.is_active) || enrolledPaths[0];
      localStorage.setItem("currentLearningPath", JSON.stringify(activePath));
      navigate("/learning");
    } else {
      navigate("/onboarding");
    }
  };

  const continuePath = async (pathId: number) => {
    try {
      // Get the full path details from the new system
      const response = await fetch(`http://localhost:8000/generate-path/user/${userData?.id}/path/${pathId}/details`);
      const data = await response.json();
      
      if (data.success) {
        localStorage.setItem("currentLearningPath", JSON.stringify(data.path));
        navigate("/learning");
      } else {
        // Fallback to basic path info
        const path = enrolledPaths.find((p) => p.id === pathId);
        if (path) {
          localStorage.setItem("currentLearningPath", JSON.stringify(path));
          navigate("/learning");
        }
      }
    } catch (err) {
      console.error("Error loading path details:", err);
      // Fallback to basic path info
      const path = enrolledPaths.find((p) => p.id === pathId);
      if (path) {
        localStorage.setItem("currentLearningPath", JSON.stringify(path));
        navigate("/learning");
      }
    }
  };

  const viewPath = async (pathId: number) => {
    try {
      // Get the full path details from the new system
      const response = await fetch(`http://localhost:8000/generate-path/user/${userData?.id}/path/${pathId}/details`);
      const data = await response.json();
      
      if (data.success) {
        localStorage.setItem("currentLearningPath", JSON.stringify(data.path));
        navigate("/learning");
      } else {
        // Fallback to basic path info
        const path = enrolledPaths.find((p) => p.id === pathId);
        if (path) {
          localStorage.setItem("currentLearningPath", JSON.stringify(path));
          navigate("/learning");
        }
      }
    } catch (err) {
      console.error("Error loading path details:", err);
      // Fallback to basic path info
      const path = enrolledPaths.find((p) => p.id === pathId);
      if (path) {
        localStorage.setItem("currentLearningPath", JSON.stringify(path));
        navigate("/learning");
      }
    }
  };

  const generateNewPath = () => {
    navigate("/onboarding");
  };

  if (loading) {
    return (
      <div className="bg-gray-50 font-sans min-h-screen">
        <VantaBackground />
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Loading your dashboard...</p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 font-sans min-h-screen">
      <VantaBackground />
      <Navbar />

      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            Welcome back, {userData?.name || "User"}! 👋
          </h1>
          <p className="text-gray-600">
            {currentLearningPath 
              ? `Continue your ${currentLearningPath.learning_domain.replace('_', ' ')} journey` 
              : "Manage your learning journeys and discover new paths."
            }
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Enrolled Paths</p>
                <h3 className="text-2xl font-bold text-gray-800">{enrolledPaths.length}</h3>
              </div>
              <i data-feather="book" className="w-8 h-8 text-blue-600"></i>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Completed Modules</p>
                <h3 className="text-2xl font-bold text-gray-800">
                  {currentLearningPath 
                    ? currentLearningPath.completed_nodes.length 
                    : enrolledPaths.reduce((acc, path) => acc + (path.subnodes?.length || 0), 0)
                  }
                </h3>
              </div>
              <i data-feather="check-circle" className="w-8 h-8 text-green-600"></i>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Progress</p>
                <h3 className="text-2xl font-bold text-gray-800">
                  {currentLearningPath ? `${currentLearningPath.progress_percentage}%` : "0%"}
                </h3>
              </div>
              <i data-feather="target" className="w-8 h-8 text-purple-600"></i>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Current Week</p>
                <h3 className="text-2xl font-bold text-gray-800">
                  {currentLearningPath ? `Week ${currentLearningPath.current_week}` : "0"}
                </h3>
              </div>
              <i data-feather="calendar" className="w-8 h-8 text-orange-600"></i>
            </div>
          </div>
        </div>

        {/* Current Learning Path */}
        {currentLearningPath && (
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white mb-8">
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-xl font-bold mb-2">Current Learning Path</h2>
                <h3 className="text-2xl font-bold mb-2">{currentLearningPath.title}</h3>
                <p className="text-blue-100 mb-4">{currentLearningPath.description}</p>
                <div className="flex items-center space-x-6">
                  <div className="flex items-center space-x-2">
                    <i data-feather="bar-chart" className="w-4 h-4"></i>
                    <span className="text-sm">{currentLearningPath.learner_type}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <i data-feather="clock" className="w-4 h-4"></i>
                    <span className="text-sm">{currentLearningPath.time_availability.replace('_', ' ')}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <i data-feather="target" className="w-4 h-4"></i>
                    <span className="text-sm">{currentLearningPath.progress_percentage}% Complete</span>
                  </div>
                </div>
              </div>
              <button
                onClick={continueLearning}
                className="bg-white text-blue-600 hover:bg-gray-100 font-medium py-3 px-6 rounded-lg flex items-center"
              >
                <i data-feather="play-circle" className="w-5 h-5 mr-2"></i>
                Continue Learning
              </button>
            </div>
            
            {/* Progress Bar */}
            <div className="mt-4">
              <div className="flex justify-between text-sm mb-1">
                <span>Your progress</span>
                <span>{currentLearningPath.progress_percentage}%</span>
              </div>
              <div className="w-full bg-blue-400 rounded-full h-2">
                <div 
                  className="bg-white h-2 rounded-full transition-all duration-500"
                  style={{ width: `${currentLearningPath.progress_percentage}%` }}
                ></div>
              </div>
            </div>
          </div>
        )}

        {/* Paths Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-md p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold text-gray-800">My Learning Paths</h2>
                <button
                  onClick={() => navigate("/learning")}
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                >
                  View All
                </button>
              </div>

              {enrolledPaths.length === 0 ? (
                <div className="text-center py-12">
                  <i
                    data-feather="book-open"
                    className="w-16 h-16 text-gray-300 mx-auto mb-4"
                  ></i>
                  <h3 className="text-lg font-semibold text-gray-700 mb-2">No Learning Paths Yet</h3>
                  <p className="text-gray-500 mb-4">Start your learning journey today!</p>
                  <button
                    onClick={generateNewPath}
                    className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg"
                  >
                    Create Your First Path
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  {enrolledPaths.map((path) => (
                    <div
                      key={path.id}
                      className={`border rounded-lg p-4 transition ${
                        path.is_active 
                          ? "border-blue-300 bg-blue-50" 
                          : "border-gray-200 hover:border-blue-300"
                      }`}
                    >
                      <div className="flex justify-between items-start mb-3">
                        <h3 className="font-semibold text-gray-800">{path.title}</h3>
                        <span
                          className={`text-xs px-2 py-1 rounded ${
                            path.is_active 
                              ? "bg-green-100 text-green-800" 
                              : "bg-gray-100 text-gray-800"
                          }`}
                        >
                          {path.is_active ? "Active" : "Completed"}
                        </span>
                      </div>
                      <p className="text-gray-600 text-sm mb-3">
                        Difficulty: {path.difficulty}/10 • {path.subnodes?.length || 0} modules
                      </p>

                      <div className="flex justify-between items-center">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => continuePath(path.id)}
                            className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-1.5 px-3 rounded"
                          >
                            Continue
                          </button>
                          <button
                            onClick={() => viewPath(path.id)}
                            className="border border-gray-300 hover:border-blue-500 text-gray-700 text-sm font-medium py-1.5 px-3 rounded"
                          >
                            View Details
                          </button>
                        </div>
                        <span className="text-xs text-gray-500">
                          {path.created_at ? new Date(path.created_at).toLocaleDateString() : "Recently created"}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Quick Actions & Available Paths */}
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-purple-600 to-purple-700 rounded-xl shadow-lg p-6 text-white">
              <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
              <div className="space-y-3">
                <button
                  onClick={continueLearning}
                  className="w-full bg-white text-purple-600 hover:bg-gray-100 font-medium py-2.5 px-4 rounded-lg flex items-center justify-center"
                >
                  <i data-feather="play-circle" className="w-5 h-5 mr-2"></i>
                  {currentLearningPath ? "Continue Learning" : "Start Learning"}
                </button>
                <button
                  onClick={generateNewPath}
                  className="w-full bg-white/10 hover:bg-white/20 backdrop-blur-sm font-medium py-2.5 px-4 rounded-lg flex items-center justify-center"
                >
                  <i data-feather="plus-circle" className="w-5 h-5 mr-2"></i>
                  Create New Path
                </button>
                <button
                  onClick={() => navigate("/learning")}
                  className="w-full bg-white/10 hover:bg-white/20 backdrop-blur-sm font-medium py-2.5 px-4 rounded-lg flex items-center justify-center"
                >
                  <i data-feather="book-open" className="w-5 h-5 mr-2"></i>
                  View All Paths
                </button>
              </div>
            </div>

            {/* Learning Domains */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-lg font-bold text-gray-800 mb-4">Learning Domains</h2>
              <div className="space-y-3">
                {[
                  { name: "AI & Machine Learning", domain: "ai_ml", color: "bg-red-100 text-red-800" },
                  { name: "Web Development", domain: "web_dev", color: "bg-blue-100 text-blue-800" },
                  { name: "Cybersecurity", domain: "cybersecurity", color: "bg-green-100 text-green-800" },
                  { name: "Cloud Computing", domain: "cloud_computing", color: "bg-purple-100 text-purple-800" }
                ].map((domain) => (
                  <div
                    key={domain.domain}
                    className="border border-gray-200 rounded-lg p-3 hover:border-blue-300 transition"
                  >
                    <div className="flex justify-between items-center">
                      <h4 className="font-semibold text-gray-800">{domain.name}</h4>
                      <span className={`text-xs px-2 py-1 rounded ${domain.color}`}>
                        Available
                      </span>
                    </div>
                    <button
                      onClick={generateNewPath}
                      className="w-full mt-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-medium py-2 px-3 rounded"
                    >
                      Generate Path
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;