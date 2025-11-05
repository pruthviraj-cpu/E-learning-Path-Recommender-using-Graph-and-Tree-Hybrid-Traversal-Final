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

const Dashboard = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState<any>(null);
  const [enrolledPaths, setEnrolledPaths] = useState<Path[]>([]);
  const [availablePaths, setAvailablePaths] = useState<Path[]>([]);

  useEffect(() => {
    const storedUser = localStorage.getItem("userData");
    if (!storedUser) {
      navigate("/login");
      return;
    }

    const user = JSON.parse(storedUser);
    setUserData(user);

    // Fetch enrolled paths
    fetch(`http://localhost:8000/auth/enrolled/${user.id}`)
      .then(res => res.json())
      .then(data => setEnrolledPaths(data))
      .catch(err => console.error("Error fetching enrolled paths:", err));



    // // Fetch all available paths
    // fetch("http://localhost:8000/paths/all")
    //   .then((res) => res.json())
    //   .then((data) => setAvailablePaths(data))
    //   .catch((err) => console.error("Error fetching available paths:", err));

    feather.replace();
  }, [navigate]);

  useEffect(() => {
    feather.replace();
  });

  const continueLearning = () => {
    if (enrolledPaths.length > 0) {
      const activePath = enrolledPaths.find((p) => p.is_active) || enrolledPaths[0];
      localStorage.setItem("currentLearningPath", JSON.stringify(activePath));
      navigate("/pathways");
    } else {
      navigate("/onboarding");
    }
  };

  const continuePath = (pathId: number) => {
    const path = enrolledPaths.find((p) => p.id === pathId);
    if (path) {
      localStorage.setItem("currentLearningPath", JSON.stringify(path));
      navigate("/pathways");
    }
  };

  const viewPath = (pathId: number) => {
    const path = enrolledPaths.find((p) => p.id === pathId);
    if (path) {
      localStorage.setItem("currentLearningPath", JSON.stringify(path));
      navigate("/learning");
    }
  };

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
            Manage your learning journeys and discover new paths.
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
                <p className="text-gray-600 text-sm">Completed Subnodes</p>
                <h3 className="text-2xl font-bold text-gray-800">
                  {enrolledPaths.reduce(
                    (acc, path) =>
                      acc +
                      (path.subnodes?.filter((t) => (t as any).completed)?.length || 0),
                    0
                  )}
                </h3>
              </div>
              <i data-feather="check-circle" className="w-8 h-8 text-green-600"></i>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Learning Streak</p>
                <h3 className="text-2xl font-bold text-gray-800">0 days</h3>
              </div>
              <i data-feather="calendar" className="w-8 h-8 text-orange-600"></i>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Active Paths</p>
                <h3 className="text-2xl font-bold text-gray-800">
                  {enrolledPaths.filter((p) => p.is_active).length}
                </h3>
              </div>
              <i data-feather="trending-up" className="w-8 h-8 text-purple-600"></i>
            </div>
          </div>
        </div>

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
                    onClick={() => navigate("/onboarding")}
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
                      className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition"
                    >
                      <div className="flex justify-between items-start mb-3">
                        <h3 className="font-semibold text-gray-800">{path.title}</h3>
                        <span
                          className={`text-xs px-2 py-1 rounded ${path.is_active ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"
                            }`}
                        >
                          {path.is_active ? "Active" : "Completed"}
                        </span>
                      </div>
                      <p className="text-gray-600 text-sm mb-3">
                        Difficulty: {path.difficulty} • {path.subnodes?.length || 0} subnodes
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
                            View
                          </button>
                        </div>
                        <span className="text-xs text-gray-500">
                          Created {path.created_at ? new Date(path.created_at).toLocaleDateString() : "N/A"}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Available Paths */}
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl shadow-lg p-6 text-white">
              <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
              <div className="space-y-3">
                <button
                  onClick={continueLearning}
                  className="w-full bg-white text-blue-600 hover:bg-gray-100 font-medium py-2.5 px-4 rounded-lg flex items-center justify-center"
                >
                  <i data-feather="play-circle" className="w-5 h-5 mr-2"></i>
                  Continue Learning
                </button>
                <button
                  onClick={() => navigate("/onboarding")}
                  className="w-full bg-white/10 hover:bg-white/20 backdrop-blur-sm font-medium py-2.5 px-4 rounded-lg flex items-center justify-center"
                >
                  <i data-feather="plus-circle" className="w-5 h-5 mr-2"></i>
                  Create New Path
                </button>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-lg font-bold text-gray-800 mb-4">Available Paths</h2>
              <div className="space-y-3">
                {availablePaths.slice(0, 3).map((path) => (
                  <div
                    key={path.id}
                    className="border border-gray-200 rounded-lg p-3 hover:border-blue-300 transition"
                  >
                    <h4 className="font-semibold text-gray-800">{path.title}</h4>
                    <p className="text-gray-600 text-sm mt-1">{path.type}</p>
                    <div className="flex justify-between items-center mt-2">
                      <span className="text-xs text-gray-500">Difficulty: {path.difficulty}</span>
                      <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                        {path.subnodes?.length || 0} subnodes
                      </span>
                    </div>
                    <button
                      onClick={() => navigate("/onboarding")}
                      className="w-full mt-3 bg-green-600 hover:bg-green-700 text-white text-sm font-medium py-2 px-3 rounded"
                    >
                      Enroll Now
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