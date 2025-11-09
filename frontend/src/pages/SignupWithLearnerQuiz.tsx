"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"

const SignupWithLearnerQuiz = () => {
  const navigate = useNavigate()

  // Signup states
  const [name, setName] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [signupError, setSignupError] = useState("")
  const [signupLoading, setSignupLoading] = useState(false)

  // Quiz states
  const [currentScreen, setCurrentScreen] = useState("signup") // "signup" | "quiz" | "results"
  const [quiz, setQuiz] = useState<any>(null)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [quizLoading, setQuizLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [quizError, setQuizError] = useState("")
  const [submitLoading, setSubmitLoading] = useState(false)

  useEffect(() => {
    const storedUser = localStorage.getItem("userData")
    if (storedUser) {
      const userData = JSON.parse(storedUser)
      if (userData && userData.id) {
        navigate("/login")
      }
    }
  }, [navigate])

  useEffect(() => {
    if (currentScreen === "quiz" && !quiz) {
      setQuizLoading(true)
      fetch("http://localhost:8000/learner-quiz/questions")
        .then((res) => res.json())
        .then((data) => {
          setQuiz(data)
          setQuizError("")
          setQuizLoading(false)
        })
        .catch((err) => {
          console.error("Error fetching quiz:", err)
          setQuizError("Failed to load quiz. Please try again.")
          setQuizLoading(false)
        })
    }
  }, [currentScreen, quiz])

  const handleSignupSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSignupError("")

    // Validation
    if (!name.trim()) {
      setSignupError("Name is required")
      return
    }

    if (password.length < 6) {
      setSignupError("Password must be at least 6 characters")
      return
    }

    if (password !== confirmPassword) {
      setSignupError("Passwords do not match")
      return
    }

    setSignupLoading(true)

    try {
      const response = await fetch("http://localhost:8000/auth/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, password }),
      })

      const data = await response.json()

      if (data.success) {
        // Store user data and move to quiz
        localStorage.setItem("userData", JSON.stringify(data.user || {}))
        setCurrentScreen("quiz")
      } else {
        setSignupError(data.message || "Signup failed. Please try again.")
      }
    } catch (err) {
      console.error("Signup error:", err)
      setSignupError("An error occurred. Please try again later.")
    } finally {
      setSignupLoading(false)
    }
  }

  const handleSelectAnswer = (qId: string, option: string) => {
    setAnswers((prev) => ({ ...prev, [qId]: option }))
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

  const handleSubmitQuiz = async () => {
    try {
      const response = await fetch("http://localhost:8000/learner-quiz/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answers: Object.values(answers).map((a) => parseInt(a)) }),
      });

      const data = await response.json();
      setResult(data);

      // ✅ Also send learner type to backend for the signed-up user
      const storedUser = JSON.parse(localStorage.getItem("userData") || "{}");

      await fetch("http://localhost:8000/auth/learner-type", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: storedUser.name,
          password: storedUser.password,
          learner_type: data.learner_type,
        }),
      });

      setCurrentScreen("results");
    } catch (err) {
      console.error("Error submitting quiz:", err);
      setQuizError("Failed to submit quiz. Please try again.");
    }
  };


  const handleContinue = () => {
    navigate("/login")
  }

  const currentQuestion = quiz && quiz.questions ? quiz.questions[currentQuestionIndex] : null
  const isAllAnswered = quiz && Object.keys(answers).length === quiz.questions.length
  const quizProgress = quiz ? ((currentQuestionIndex + 1) / quiz.questions.length) * 100 : 0

  return (
    <div className="bg-gray-50 flex items-center justify-center min-h-screen p-4">
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeOut {
          from { opacity: 1; transform: translateY(0); }
          to { opacity: 0; transform: translateY(-10px); }
        }
        .screen-enter { animation: fadeIn 0.3s ease-out; }
        .screen-exit { animation: fadeOut 0.2s ease-in; }
      `}</style>

      {/* SIGNUP SCREEN */}
      {currentScreen === "signup" && (
        <div className="screen-enter bg-white shadow-md rounded-xl p-8 w-full max-w-md">
          <h2 className="text-2xl font-bold text-gray-800 mb-2 text-center">Create Account</h2>
          <p className="text-center text-gray-600 text-sm mb-6">Join LearnPath and start your learning journey</p>

          <form onSubmit={handleSignupSubmit} className="space-y-4">
            <div>
              <label className="block text-gray-700 mb-1" htmlFor="name">
                Name
              </label>
              <input
                type="text"
                id="name"
                placeholder="Enter your full name"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-gray-700 mb-1" htmlFor="password">
                Password
              </label>
              <input
                type="password"
                id="password"
                placeholder="Create a password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-gray-700 mb-1" htmlFor="confirmPassword">
                Confirm Password
              </label>
              <input
                type="password"
                id="confirmPassword"
                placeholder="Confirm your password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {signupError && <p className="text-red-500 text-sm font-medium">{signupError}</p>}

            <button
              type="submit"
              disabled={signupLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium py-2 rounded-lg transition duration-200"
            >
              {signupLoading ? "Creating Account..." : "Next"}
            </button>
          </form>

          <p className="mt-4 text-center text-gray-600 text-sm">
            Already have an account?{" "}
            <a href="/login" className="text-blue-600 hover:text-blue-700 font-medium">
              Login
            </a>
          </p>
        </div>
      )}

      {/* QUIZ SCREEN */}
      {currentScreen === "quiz" && (
        <div className="screen-enter bg-white shadow-md rounded-xl p-8 w-full max-w-md">
          {quizLoading ? (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="w-12 h-12 border-4 border-gray-200 border-t-blue-600 rounded-full animate-spin mb-4"></div>
              <p className="text-gray-600">Loading quiz questions...</p>
            </div>
          ) : quizError ? (
            <div className="text-center py-8">
              <p className="text-red-500 font-medium mb-4">{quizError}</p>
              <button
                onClick={() => setCurrentScreen("signup")}
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                Back to Signup
              </button>
            </div>
          ) : quiz && currentQuestion ? (
            <>
              {/* Progress Bar */}
              <div className="mb-6">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-semibold text-gray-600">
                    Question {currentQuestionIndex + 1} of {quiz.questions.length}
                  </span>
                  <span className="text-sm font-semibold text-blue-600">{Math.round(quizProgress)}%</span>
                </div>
                <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-600 transition-all duration-300"
                    style={{ width: `${quizProgress}%` }}
                  ></div>
                </div>
              </div>

              {/* Question */}
              <h2 className="text-xl font-bold text-gray-800 mb-6">{currentQuestion.question}</h2>

              {/* Options */}
              <div className="space-y-3 mb-8">
                {(currentQuestion.options || []).map((option: string, idx: number) => (
                  <label
                    key={idx}
                    className="flex items-start p-4 border-2 border-gray-200 rounded-lg cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-all duration-200"
                  >
                    <input
                      type="radio"
                      name={`q${currentQuestionIndex}`}
                      value={String(idx)}
                      checked={answers[String(currentQuestionIndex)] === String(idx)}
                      onChange={() => handleSelectAnswer(String(currentQuestionIndex), String(idx))}
                      className="w-4 h-4 mt-1 text-blue-600 cursor-pointer accent-blue-600"
                    />
                    <span className="ml-3 text-gray-700">{option}</span>
                  </label>
                ))}
              </div>

              {/* Navigation */}
              <div className="flex gap-3">
                <button
                  onClick={handlePreviousQuestion}
                  disabled={currentQuestionIndex === 0}
                  className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 disabled:bg-gray-100 disabled:text-gray-400 transition duration-200"
                >
                  Previous
                </button>

                {currentQuestionIndex === quiz.questions.length - 1 ? (
                  <button
                    onClick={handleSubmitQuiz}
                    disabled={!isAllAnswered || submitLoading}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-blue-400 transition duration-200"
                  >
                    {submitLoading ? "Submitting..." : "Submit Quiz"}
                  </button>
                ) : (
                  <button
                    onClick={handleNextQuestion}
                    disabled={!answers[String(currentQuestionIndex)]}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-blue-400 transition duration-200"
                  >
                    Next
                  </button>
                )}
              </div>
            </>
          ) : null}
        </div>
      )}

      {/* RESULTS SCREEN */}
      {currentScreen === "results" && result && (
        <div className="screen-enter bg-white shadow-md rounded-xl p-8 w-full max-w-md">
          <div className="text-center mb-6">
            <div className="inline-flex items-center justify-center w-12 h-12 bg-green-100 rounded-full mb-4">
              <span className="text-2xl">✓</span>
            </div>
            <h2 className="text-2xl font-bold text-gray-800">Quiz Complete!</h2>
            <p className="text-gray-600 text-sm mt-2">Here's your learner profile</p>
          </div>

          {/* Learner Type Result */}
          <div className="bg-blue-50 rounded-lg p-6 mb-6 border-2 border-blue-200">
            <p className="text-gray-600 text-xs font-semibold mb-2 uppercase">Your Learner Type</p>
            <p className="text-2xl font-bold text-blue-600 capitalize mb-3">
              {result.learner_type?.replace(/_/g, " ") || "Learner"}
            </p>
            <p className="text-gray-700 text-sm">
              This learning style will help us personalize your path and maximize your learning effectiveness.
            </p>
          </div>

          {/* Learning Stats */}
          {result.stats && (
            <div className="space-y-3 mb-8">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-gray-700 font-medium">Visual</span>
                <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500" style={{ width: `${(result.stats.visual || 0) * 100}%` }}></div>
                </div>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-gray-700 font-medium">Auditory</span>
                <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500" style={{ width: `${(result.stats.auditory || 0) * 100}%` }}></div>
                </div>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-gray-700 font-medium">Kinesthetic</span>
                <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500"
                    style={{ width: `${(result.stats.kinesthetic || 0) * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          )}

          {/* Continue Button */}
          <button
            onClick={handleContinue}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg transition duration-200"
          >
            Continue to Dashboard
          </button>
        </div>
      )}
    </div>
  )
}

export default SignupWithLearnerQuiz