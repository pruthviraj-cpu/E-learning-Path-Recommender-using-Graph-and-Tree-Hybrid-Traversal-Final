import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import * as feather from "feather-icons";
import Navbar from "@/components/Navbar";
import { toast } from "@/hooks/use-toast";

interface ModuleContent {
  video_url?: string;
  sections?: Array<{ title: string; content: string }>;
  reading_materials?: Array<{ title: string; link?: string; content?: string }>;
  projects?: Array<{ title: string; description: string; link?: string }>;
}

interface Module {
  id: string;
  title: string;
  description?: string;
  content?: ModuleContent;
  skills?: string[];
  difficulty?: string;
}

const mockModule: Module = {
  id: "1",
  title: "Introduction to AI",
  description: "Learn AI basics",
  content: {
    video_url: "https://www.youtube.com/embed/dQw4w9WgXcQ",
    sections: [
      { title: "What is AI?", content: "Artificial Intelligence is..." },
      { title: "History of AI", content: "AI started in the 1950s..." },
    ],
    reading_materials: [
      { title: "AI Overview PDF", link: "#", content: "PDF content..." },
      { title: "AI in Practice", link: "#", content: "Article content..." },
    ],
    projects: [
      { title: "Build a Chatbot", description: "Simple Python chatbot project" },
      { title: "AI Image Classifier", description: "Use ML to classify images" },
    ],
  },
  skills: ["AI Basics", "ML Fundamentals"],
  difficulty: "Beginner",
};

const Pathways = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("visual");
  const [currentModule, setCurrentModule] = useState<Module | null>(null);

  useEffect(() => {
    // Initialize mock module (replace this with real backend fetch later)
    setCurrentModule(mockModule);
  }, []);

  useEffect(() => {
    feather.replace();
  }, [activeTab]);

  if (!currentModule) return <div>Loading...</div>;

  return (
    <div className="bg-gray-50 font-sans min-h-screen">
      <Navbar />
      <main className="container mx-auto px-4 py-6">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Main Content */}
          <div className="lg:w-3/4 bg-white rounded-xl shadow-md overflow-hidden">
            {/* Tabs */}
            <div className="border-b border-gray-200">
              <nav className="flex -mb-px">
                {["visual", "reading", "project", "quiz"].map((tab) => (
                  <button
                    key={tab}
                    className={`mr-8 py-4 px-1 font-medium text-sm ${
                      activeTab === tab
                        ? "border-b-2 border-blue-600 text-blue-600"
                        : "text-gray-500 hover:text-gray-700"
                    }`}
                    onClick={() => setActiveTab(tab)}
                  >
                    <i
                      data-feather={
                        tab === "visual"
                          ? "play"
                          : tab === "reading"
                          ? "book-open"
                          : tab === "project"
                          ? "briefcase"
                          : "clipboard"
                      }
                      className="w-4 h-4 mr-2 inline"
                    ></i>
                    {tab.charAt(0).toUpperCase() + tab.slice(1)}
                  </button>
                ))}
              </nav>
            </div>

            <div className="p-6">
              {activeTab === "visual" && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-800 mb-4">
                    {currentModule.title} (Visual)
                  </h2>
                  {currentModule.content?.video_url && (
                    <div className="mb-6">
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
                  {currentModule.content?.sections?.map((s, i) => (
                    <div key={i} className="mb-4">
                      <h3 className="font-semibold text-gray-800">{s.title}</h3>
                      <p className="text-gray-600">{s.content}</p>
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

              {activeTab === "quiz" && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-800 mb-4">Quiz</h2>
                  <p className="text-gray-600">Here you can generate or take quizzes. (Mock data for now)</p>
                  {/* Replace this with your existing quiz component */}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Pathways;
