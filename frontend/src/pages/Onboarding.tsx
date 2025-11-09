"use client"

import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"

const OnboardingQuiz = () => {
    const [domain, setDomain] = useState("")
    const [quiz, setQuiz] = useState<any>(null)
    const [answers, setAnswers] = useState<Record<string, string>>({})
    const [submitted, setSubmitted] = useState(false)
    const [result, setResult] = useState<any>(null)
    const [loading, setLoading] = useState(false)
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)

    const [timeAvailability, setTimeAvailability] = useState("")
    const [studyWeeks, setStudyWeeks] = useState("")
    const [pathResult, setPathResult] = useState<any>(null)
    const [generatingPath, setGeneratingPath] = useState(false)

    const navigate = useNavigate()
    const availableDomains = ["Data Science", "Web Development"]

    useEffect(() => {
        if (!domain) return
        setQuiz(null)
        setAnswers({})
        setSubmitted(false)
        setResult(null)
        setLoading(true)
        setCurrentQuestionIndex(0)

        fetch(`http://localhost:8000/onboarding_quiz/get-quiz/${domain}`)
            .then((res) => res.json())
            .then((data) => {
                setQuiz(data)
                setLoading(false)
            })
            .catch((err) => {
                console.error("Error fetching quiz:", err)
                setLoading(false)
            })
    }, [domain])

    const handleSelect = (qId: string, option: string) => {
        setAnswers((prev) => ({ ...prev, [qId]: option }))
    }

    const handleSubmit = () => {
        console.log("Submitting:", JSON.stringify({ domain, answers }, null, 2));
        console.log("Answers object:", answers);
        fetch("http://localhost:8000/onboarding_quiz/submit-quiz", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ domain, answers }),
        })
            .then((res) => res.json())
            .then((data) => {
                console.log("Result:", data);
                setResult(data);
                setSubmitted(true);
            })
            .catch((err) => console.error("Error submitting quiz:", err));
    };

    const handleGeneratePath = () => {
        if (!result || !result.learner_type) {
            console.error("Learner type not available yet!")
            return
        }

        const userData = JSON.parse(localStorage.getItem("userData") || "{}");
        const userId = userData?.id;

        if (!userId) {
            console.error("User not logged in!");
            return;
        }

        const availability = timeAvailability <= "2" ? "part_time" : timeAvailability <= "5" ? "full_time" : "intensive"

        const domainMap: Record<string, string> = {
            "Data Science": "ai_ml",
            "Web Development": "web_dev",
            "cybersecurity": "cybersecurity",
            "cloud computing": "cloud_computing",
            "full_stack": "full_stck",
        }

        setGeneratingPath(true)
        fetch("http://localhost:8000/generate-path/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: userId,
                learner_type: result.learner_type,
                learning_domain: domainMap[domain],
                time_availability: availability,
                study_weeks: Number.parseInt(studyWeeks),
            }),
        })
            .then((res) => res.json())
            .then((data) => {
                setPathResult(data)
                setGeneratingPath(false)
                setTimeout(() => {
                    navigate("/dashboard")
                }, 5000)
            })
            .catch((err) => {
                console.error(err)
                setGeneratingPath(false)
            })
    }

    const handleNextQuestion = () => {
        if (currentQuestionIndex < quiz.questions.length - 1) {
            setCurrentQuestionIndex(currentQuestionIndex + 1)
        }
    }

    const handlePreviousQuestion = () => {
        if (currentQuestionIndex > 0) {
            setCurrentQuestionIndex(currentQuestionIndex - 1)
        }
    }

    const isAllAnswered = quiz && Object.keys(answers).length === quiz.questions.length
    const currentQuestion = quiz && quiz.questions[currentQuestionIndex]

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-4 md:p-8">
            <style>{`
                @keyframes fadeInUp {
                    from {
                        opacity: 0;
                        transform: translateY(20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }

                @keyframes fadeOutUp {
                    from {
                        opacity: 1;
                        transform: translateY(0);
                    }
                    to {
                        opacity: 0;
                        transform: translateY(-20px);
                    }
                }

                @keyframes spin {
                    to {
                        transform: rotate(360deg);
                    }
                }

                @keyframes pulse-dot {
                    0%, 100% { opacity: 0.3; }
                    50% { opacity: 1; }
                }

                @keyframes slideInCard {
                    from {
                        opacity: 0;
                        transform: translateY(30px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }

                .question-enter {
                    animation: fadeInUp 0.5s ease-out;
                }

                .question-exit {
                    animation: fadeOutUp 0.3s ease-in;
                }

                .spinner {
                    animation: spin 2s linear infinite;
                }

                .dot {
                    animation: pulse-dot 1.4s ease-in-out infinite;
                }

                .dot:nth-child(2) {
                    animation-delay: 0.2s;
                }

                .dot:nth-child(3) {
                    animation-delay: 0.4s;
                }

                .card-enter {
                    animation: slideInCard 0.6s ease-out;
                }
            `}</style>

            <div className="max-w-2xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                            L
                        </div>
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                            LearnPath Quiz
                        </h1>
                    </div>
                    <p className="text-gray-600 ml-13">Find your perfect learning path</p>
                </div>

                {/* Domain Selection */}
                {!domain && (
                    <div className="card-enter bg-white rounded-2xl shadow-lg p-8">
                        <h2 className="text-2xl font-bold text-gray-800 mb-6">Welcome!</h2>
                        <p className="text-gray-600 mb-6">Select your learning domain to get started</p>

                        <div className="space-y-3">
                            {availableDomains.map((d) => (
                                <button
                                    key={d}
                                    onClick={() => setDomain(d)}
                                    className="w-full p-4 text-left border-2 border-gray-200 rounded-xl hover:border-blue-500 hover:bg-blue-50 transition-all duration-300 group"
                                >
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <h3 className="font-semibold text-gray-800 group-hover:text-blue-600 capitalize transition">
                                                {d}
                                            </h3>
                                            <p className="text-sm text-gray-600">Start your journey in {d}</p>
                                        </div>
                                        <div className="text-xl group-hover:translate-x-1 transition-transform">→</div>
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* Loading State */}
                {domain && loading && (
                    <div className="card-enter bg-white rounded-2xl shadow-lg p-8 flex flex-col items-center justify-center min-h-96">
                        <div className="w-16 h-16 mb-6 relative">
                            <div
                                className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full spinner"
                                style={{ opacity: 0.2 }}
                            ></div>
                            <div className="absolute inset-2 bg-white rounded-full flex items-center justify-center">
                                <div className="w-10 h-10 border-4 border-transparent border-t-blue-600 border-r-purple-600 rounded-full spinner"></div>
                            </div>
                        </div>
                        <h3 className="text-xl font-semibold text-gray-800 mt-4">Your quiz is loading</h3>
                        <div className="flex gap-1 mt-2">
                            <span className="w-2 h-2 bg-blue-600 rounded-full dot"></span>
                            <span className="w-2 h-2 bg-blue-600 rounded-full dot"></span>
                            <span className="w-2 h-2 bg-blue-600 rounded-full dot"></span>
                        </div>
                    </div>
                )}

                {/* Quiz - Single Question Display */}
                {quiz && !submitted && currentQuestion && (
                    <div className="card-enter bg-white rounded-2xl shadow-lg p-8">
                        {/* Progress Bar */}
                        <div className="mb-8">
                            <div className="flex justify-between items-center mb-3">
                                <span className="text-sm font-semibold text-gray-600">
                                    Question {currentQuestionIndex + 1} of {quiz.questions.length}
                                </span>
                                <span className="text-sm font-semibold text-blue-600">
                                    {Math.round(((currentQuestionIndex + 1) / quiz.questions.length) * 100)}%
                                </span>
                            </div>
                            <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-blue-600 to-purple-600 transition-all duration-500 ease-out rounded-full"
                                    style={{ width: `${((currentQuestionIndex + 1) / quiz.questions.length) * 100}%` }}
                                ></div>
                            </div>
                        </div>

                        {/* Question */}
                        <div className="mb-8">
                            <h2 className="text-2xl font-bold text-gray-800 mb-8">{currentQuestion.text}</h2>

                            {/* Options */}
                            <div className="space-y-3">
                                {Object.entries(currentQuestion.options).map(([key, value]) => (
                                    <label
                                        key={key}
                                        className="flex items-start p-4 border-2 border-gray-200 rounded-xl cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-all duration-300 group"
                                    >
                                        <input
                                            type="radio"
                                            name={`q${currentQuestion.id}`}
                                            value={key}
                                            checked={answers[currentQuestion.id] === key}
                                            onChange={() => handleSelect(String(currentQuestion.id), key)}
                                            className="w-5 h-5 mt-1 text-blue-600 cursor-pointer accent-blue-600"
                                        />
                                        <span className="ml-4 text-gray-700 group-hover:text-gray-900 transition">
                                            <span className="font-semibold text-blue-600">{key}.</span> {value as string}
                                        </span>
                                    </label>
                                ))}
                            </div>
                        </div>

                        {/* Navigation Buttons */}
                        <div className="flex gap-4 justify-between items-center">
                            <button
                                onClick={handlePreviousQuestion}
                                disabled={currentQuestionIndex === 0}
                                className={`px-6 py-3 rounded-lg font-semibold transition-all duration-300 ${currentQuestionIndex === 0
                                    ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                                    : "bg-gray-200 text-gray-700 hover:bg-gray-300 active:scale-95"
                                    }`}
                            >
                                ← Previous
                            </button>

                            <div className="flex gap-2">
                                {quiz.questions.map((_, idx) => (
                                    <div
                                        key={idx}
                                        className={`w-3 h-3 rounded-full transition-all duration-300 ${idx === currentQuestionIndex
                                            ? "bg-blue-600 w-8"
                                            : answers[quiz.questions[idx].id]
                                                ? "bg-green-500"
                                                : "bg-gray-300"
                                            }`}
                                    ></div>
                                ))}
                            </div>

                            {currentQuestionIndex === quiz.questions.length - 1 ? (
                                <button
                                    onClick={handleSubmit}
                                    disabled={!isAllAnswered}
                                    className={`px-8 py-3 rounded-lg font-semibold transition-all duration-300 ${isAllAnswered
                                        ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:shadow-lg active:scale-95"
                                        : "bg-gray-100 text-gray-400 cursor-not-allowed"
                                        }`}
                                >
                                    Submit Quiz
                                </button>
                            ) : (
                                <button
                                    onClick={handleNextQuestion}
                                    disabled={!answers[currentQuestion.id]}
                                    className={`px-8 py-3 rounded-lg font-semibold transition-all duration-300 ${answers[currentQuestion.id]
                                        ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:shadow-lg active:scale-95"
                                        : "bg-gray-100 text-gray-400 cursor-not-allowed"
                                        }`}
                                >
                                    Next →
                                </button>
                            )}
                        </div>
                    </div>
                )}

                {/* Results & Path Generation */}
                {submitted && result && !pathResult && (
                    <div className="card-enter bg-white rounded-2xl shadow-lg p-8">
                        {/* Quiz Result */}
                        <div className="mb-8 pb-8 border-b-2 border-gray-100">
                            <div className="flex items-center gap-3 mb-6">
                                <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center text-white text-xl">
                                    ✓
                                </div>
                                <div>
                                    <h2 className="text-2xl font-bold text-gray-800">Quiz Complete!</h2>
                                    <p className="text-gray-600 text-sm">Great job answering all questions</p>
                                </div>
                            </div>

                            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 mb-6">
                                <p className="text-gray-700 text-sm mb-2">Your Learner Type</p>
                                <p className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent capitalize">
                                    {result.learner_type.replace(/_/g, " ")}
                                </p>
                                <p className="text-gray-600 text-sm mt-2">This learning style will help us personalize your path</p>
                            </div>
                        </div>

                        {/* Path Generation Form */}
                        <div>
                            <h3 className="text-xl font-bold text-gray-800 mb-6">Generate Your Learning Path</h3>

                            <div className="space-y-5 mb-8">
                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-2">Daily Study Hours</label>
                                    <div className="flex items-center gap-4">
                                        <input
                                            type="number"
                                            min="1"
                                            max="12"
                                            value={timeAvailability}
                                            onChange={(e) => setTimeAvailability(e.target.value)}
                                            className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none transition"
                                            placeholder="e.g., 2"
                                        />
                                        <span className="text-gray-600 text-sm">hours/day</span>
                                    </div>
                                    <p className="text-xs text-gray-600 mt-1">How many hours can you dedicate daily?</p>
                                </div>

                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-2">Study Duration</label>
                                    <div className="flex items-center gap-4">
                                        <input
                                            type="number"
                                            min="1"
                                            max="52"
                                            value={studyWeeks}
                                            onChange={(e) => setStudyWeeks(e.target.value)}
                                            className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none transition"
                                            placeholder="e.g., 12"
                                        />
                                        <span className="text-gray-600 text-sm">weeks</span>
                                    </div>
                                    <p className="text-xs text-gray-600 mt-1">How long do you want your learning path?</p>
                                </div>
                            </div>

                            <button
                                onClick={handleGeneratePath}
                                disabled={!timeAvailability || !studyWeeks || generatingPath}
                                className={`w-full py-4 rounded-lg font-semibold text-lg transition-all duration-300 ${timeAvailability && studyWeeks && !generatingPath
                                    ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:shadow-lg active:scale-95"
                                    : "bg-gray-100 text-gray-400 cursor-not-allowed"
                                    }`}
                            >
                                {generatingPath ? "Generating Your Path..." : "Generate Learning Path"}
                            </button>
                        </div>
                    </div>
                )}

                {/* Path Result */}
                {pathResult && (
                    <div className="card-enter space-y-6">
                        {/* Success Message */}
                        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl border-2 border-green-200 p-8">
                            <div className="flex items-center gap-4 mb-4">
                                <div className="w-14 h-14 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center text-white text-2xl">
                                    🎉
                                </div>
                                <div>
                                    <h3 className="text-2xl font-bold text-green-800">Path Generated!</h3>
                                    <p className="text-green-700">Your personalized learning path is ready</p>
                                </div>
                            </div>
                        </div>

                        {/* Path Details Cards */}
                        {pathResult.data && (
                            <div className="bg-white rounded-2xl shadow-lg p-8">
                                <h3 className="text-2xl font-bold text-gray-800 mb-6">Your Learning Path</h3>

                                {/* Main Path Card */}
                                <div className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl p-6 text-white mb-6">
                                    <div className="flex items-start justify-between mb-4">
                                        <div>
                                            <p className="text-blue-100 text-sm font-semibold mb-1">LEARNING PATH</p>
                                            <h4 className="text-2xl font-bold">{pathResult.data.title || `${domain} Path`}</h4>
                                        </div>
                                        <div className="text-3xl">📚</div>
                                    </div>
                                    <p className="text-blue-100">{pathResult.data.description || "Your personalized learning journey"}</p>
                                </div>

                                {/* Path Metrics Grid */}
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                                    <div className="bg-gray-50 rounded-lg p-4">
                                        <p className="text-gray-600 text-xs font-semibold mb-2">LEARNER TYPE</p>
                                        <p className="text-lg font-bold text-gray-800 capitalize">
                                            {result?.learner_type?.replace(/_/g, " ") || "Standard"}
                                        </p>
                                    </div>
                                    <div className="bg-gray-50 rounded-lg p-4">
                                        <p className="text-gray-600 text-xs font-semibold mb-2">DURATION</p>
                                        <p className="text-lg font-bold text-gray-800">{studyWeeks} weeks</p>
                                    </div>
                                    <div className="bg-gray-50 rounded-lg p-4">
                                        <p className="text-gray-600 text-xs font-semibold mb-2">DAILY TIME</p>
                                        <p className="text-lg font-bold text-gray-800">{timeAvailability}h/day</p>
                                    </div>
                                    <div className="bg-gray-50 rounded-lg p-4">
                                        <p className="text-gray-600 text-xs font-semibold mb-2">STATUS</p>
                                        <p className="text-lg font-bold text-green-600">Active</p>
                                    </div>
                                </div>

                                {/* Additional Info */}
                                <div className="bg-blue-50 rounded-lg p-4 border-l-4 border-blue-600">
                                    <p className="text-blue-900 text-sm">
                                        <strong>Next Steps:</strong> You'll be redirected to your dashboard shortly to start learning!
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    )
}

export default OnboardingQuiz