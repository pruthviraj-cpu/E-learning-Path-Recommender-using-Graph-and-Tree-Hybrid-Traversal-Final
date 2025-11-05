import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./onboarding-styles.css";

const TYPE_DESCRIPTIONS = {
  visual: "Learns best with diagrams, charts, maps, and visual structure; clear layouts and visual summaries work well.",
  auditory: "Learns best by listening, discussing, and explaining; lectures, podcasts, and Q&A suit this style.",
  reading: "Learns best by reading and writing; detailed notes, articles, and text‑based resources help retention.",
  kinesthetic: "Learns best by doing; hands‑on tasks, labs, demos, and practice projects improve understanding."
};

const OPTION_IMAGES: Record<string, string> = {
  "q1_option1": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz1a.jpg",
  "q1_option2": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz1b.jpg",
  "q1_option3": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz1c.jpg",
  "q2_option1": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz2a.jpg",
  "q2_option2": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz2b.jpg",
  "q2_option3": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz2c.jpg",
  "q3_option1": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz3a.jpg",
  "q3_option2": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz3b.jpg",
  "q3_option3": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz3c.jpg",
  "q4_option1": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz4a.jpg",
  "q4_option2": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz4b.jpg",
  "q4_option3": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz4c.jpg",
  "q5_option1": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz5a.jpg",
  "q5_option2": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz5b.jpg",
  "q5_option3": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz5c.jpg",
  "q6_option1": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz6a.jpg",
  "q6_option2": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz6b.jpg",
  "q6_option3": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz6c.jpg",
  "q7_option1": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz7a.jpg",
  "q7_option2": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz7b.jpg",
  "q7_option3": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz7c.jpg",
  "q8_option1": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz8a.jpg",
  "q8_option2": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz8b.jpg",
  "q8_option3": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz8c.jpg",
  "q9_option1": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz9a.jpg",
  "q9_option2": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz9b.jpg",
  "q9_option3": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz9c.jpg",
  "q10_option1": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz10a.jpg",
  "q10_option2": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz10b.jpg",
  "q10_option3": "https://arden.ac.uk/themes/arden/campaigns/what-type-of-learner-are-you/images/quiz10c.jpg"
};

const quizQuestions = [
  {
    question: "You prefer to:",
    options: [
      { type: "auditory", text: "Listen to things rather than read about them", imageKey: "q1_option1" },
      { type: "visual", text: "Analyse pictures, graphs and charts", imageKey: "q1_option2" },
      { type: "kinesthetic", text: "Handle physical objects and try to understand how they work for yourself", imageKey: "q1_option3" }
    ]
  },
  {
    question: "You remember things by:",
    options: [
      { type: "auditory", text: "Saying them out loud", imageKey: "q2_option1" },
      { type: "visual", text: "Watching a demonstration", imageKey: "q2_option2" },
      { type: "kinesthetic", text: "Experiencing them for yourself (being hands on)", imageKey: "q2_option3" }
    ]
  },
  {
    question: "You find reading:",
    options: [
      { type: "kinesthetic", text: "Takes too long; you get fidgety", imageKey: "q3_option1" },
      { type: "reading", text: "The best and most relaxing thing ever", imageKey: "q3_option2" },
      { type: "kinesthetic", text: "Pretty boring; you'd rather be outside", imageKey: "q3_option3" }
    ]
  },
  {
    question: "You're more likely to remember somebody's:",
    options: [
      { type: "auditory", text: "Name", imageKey: "q4_option1" },
      { type: "visual", text: "Face", imageKey: "q4_option2" },
      { type: "kinesthetic", text: "Hug", imageKey: "q4_option3" }
    ]
  },
  {
    question: "When you see the word 'cat', what do you do?:",
    options: [
      { type: "visual", text: "Picture a cat in your mind", imageKey: "q5_option1" },
      { type: "auditory", text: "Say the word \"cat\" to yourself", imageKey: "q5_option2" },
      { type: "kinesthetic", text: "Think about being with a cat (stroking it or hearing it meow)", imageKey: "q5_option3" }
    ]
  },
  {
    question: "What kind of book would you like to read for fun?:",
    options: [
      { type: "visual", text: "A book with lots of images", imageKey: "q6_option1" },
      { type: "reading", text: "A book with lots of words and details", imageKey: "q6_option2" },
      { type: "kinesthetic", text: "A book with word searches or crossword puzzles", imageKey: "q6_option3" }
    ]
  },
  {
    question: "If you're ever unsure of how to spell a word, what are you most likely to do?:",
    options: [
      { type: "kinesthetic", text: "Write it down to see if it looks right", imageKey: "q7_option1" },
      { type: "auditory", text: "Spell it out to see if it sounds right", imageKey: "q7_option2" },
      { type: "kinesthetic", text: "Trace the letters in the air with your finger", imageKey: "q7_option3" }
    ]
  },
  {
    question: "You're out shopping and you are standing in the queue at the checkout. What are you most likely to do while you are waiting?:",
    options: [
      { type: "visual", text: "Look around at other clothes", imageKey: "q8_option1" },
      { type: "auditory", text: "Talk to the person next to you in the queue", imageKey: "q8_option2" },
      { type: "kinesthetic", text: "Fidget, move about or rock / lean on your feet", imageKey: "q8_option3" }
    ]
  },
  {
    question: "What's the best way for you to study for an exam?:",
    options: [
      { type: "reading", text: "Read the book or your notes and review pictures or charts", imageKey: "q9_option1" },
      { type: "auditory", text: "Get a friend or family member to ask you questions that you can answer out loud", imageKey: "q9_option2" },
      { type: "kinesthetic", text: "Make index cards that you can review", imageKey: "q9_option3" }
    ]
  },
  {
    question: "What do you like to do to relax?:",
    options: [
      { type: "reading", text: "Read", imageKey: "q10_option1" },
      { type: "auditory", text: "Listen to music", imageKey: "q10_option2" },
      { type: "kinesthetic", text: "Exercise (walk, run, play sports, etc.)", imageKey: "q10_option3" }
    ]
  }
];

const Onboarding = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [userName, setUserName] = useState("");
  const [userEmail, setUserEmail] = useState("");
  const [existingUser, setExistingUser] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [quizAnswers, setQuizAnswers] = useState<string[]>([]);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [learnerTypeScores, setLearnerTypeScores] = useState({ visual: 0, auditory: 0, reading: 0, kinesthetic: 0 });
  const [skillLevel, setSkillLevel] = useState("");
  const [primaryGoal, setPrimaryGoal] = useState("");
  const [timeCommitment, setTimeCommitment] = useState("10h/week");
  const [loading, setLoading] = useState(false);

  const checkUserAndContinue = async () => {
    if (!userName.trim()) return;

    try {
      const response = await fetch(`http://localhost:8000/users/users/${userName}`);
      
      if (response.ok) {
        setExistingUser(true);
        setTimeout(() => {
          navigate('/pathways');
        }, 3000);
      } else {
        setStep(1);
        setCurrentQuestion(0);
      }
    } catch (error) {
      console.error('Error checking user:', error);
      setStep(1);
      setCurrentQuestion(0);
    }
  };

  const selectQuizOption = (answerType: string, optionIndex: number) => {
    setSelectedOption(optionIndex);
    const newAnswers = [...quizAnswers];
    newAnswers[currentQuestion] = answerType;
    setQuizAnswers(newAnswers);
  };

  const nextQuestion = () => {
    if (currentQuestion < quizQuestions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setSelectedOption(null);
    } else {
      calculateLearnerType();
      setStep(2);
    }
  };

  const calculateLearnerType = () => {
    const scores = { visual: 0, auditory: 0, reading: 0, kinesthetic: 0 };
    quizAnswers.forEach(answer => {
      if (answer && answer in scores) {
        scores[answer as keyof typeof scores]++;
      }
    });
    setLearnerTypeScores(scores);
  };

  const handleStep2Next = () => {
    if (skillLevel && primaryGoal) {
      setStep(3);
    }
  };

  const handleStep3Next = () => {
    setStep(4);
  };

  const getDominantType = (scores: any) => {
    let best = "visual";
    for (const k of ["visual", "auditory", "reading", "kinesthetic"]) {
      if (scores[k] > scores[best]) best = k;
    }
    const max = scores[best];
    const ties = Object.keys(scores).filter(k => scores[k] === max);
    return { dominant: ties.length === 1 ? best : `mixed:${ties.join("+")}`, ties };
  };

  const getPercentages = (scores: any) => {
    let total = 0;
    for (const k in scores) {
      total += Number(scores[k]);
    }
    if (total === 0) total = 1;
    
    const pct: any = {};
    for (const k in scores) {
      const scoreValue = Number(scores[k]);
      pct[k] = Math.round((scoreValue / total) * 100);
    }
    return pct;
  };

  const capitalize = (s: string) => {
    return s ? s.charAt(0).toUpperCase() + s.slice(1) : '';
  };

  const confirmLearnerType = async () => {
    setLoading(true);
    const { dominant } = getDominantType(learnerTypeScores);
    const dominantType = dominant.startsWith("mixed:") ? "mixed" : dominant;

    const profileData = {
      name: userName,
      email: userEmail || `${userName.toLowerCase().replace(/\s/g, '')}@example.com`,
      preferences: {
        skill_level: skillLevel,
        primary_goal: primaryGoal,
        learner_type: dominantType,
        time_commitment: timeCommitment,
        quiz_answers: quizAnswers
      }
    };

    try {
      const response = await fetch('http://localhost:8000/users/enroll', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profileData)
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('userData', JSON.stringify(data.user));
        sessionStorage.setItem('currentUser', userName);
        sessionStorage.setItem('learnerType', dominantType);
        
        setTimeout(() => {
          navigate('/pathways');
        }, 2000);
      } else {
        alert('Error creating profile. Please try again.');
        setLoading(false);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error connecting to server. Please try again.');
      setLoading(false);
    }
  };

  if (existingUser) {
    return (
      <div className="container">
        <div className="step active">
          <div className="user-exists">
            <h2>Welcome back, {userName}! 👋</h2>
            <p>You've already completed your onboarding. Redirecting you to your dashboard...</p>
            <div className="loading-spinner"></div>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="container">
        <div className="step active">
          <div className="loading active">
            <div className="loading-spinner"></div>
            <h2>Creating your personalized learning path...</h2>
            <p>Analyzing your responses and preferences...</p>
          </div>
        </div>
      </div>
    );
  }

  // Step 0: Name Entry
  if (step === 0) {
    return (
      <div className="container">
        <div className="step active">
          <h1>Welcome to LearnPath! 🚀</h1>
          <p className="subtitle">Let's start by getting to know you</p>
          
          <div className="form-group">
            <label htmlFor="userName">What's your name?</label>
            <input 
              type="text" 
              id="userName" 
              placeholder="Enter your full name" 
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              required
            />
          </div>

          <div className="navigation">
            <div></div>
            <button 
              className="btn" 
              onClick={checkUserAndContinue}
              disabled={!userName.trim()}
            >
              Next <span>→</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Step 1: Quiz
  if (step === 1) {
    const currentQ = quizQuestions[currentQuestion];
    return (
      <div className="container">
        <div className="step active">
          <div className="quiz-container">
            <div className="quiz-intro">
              <h2>
                We are all different, therefore it shouldn't come as a surprise that we also 
                have our own, unique way of learning. Knowing how you retain information 
                best will make you more productive and help you get more enjoyment out of 
                any course.
              </h2>
              <p className="bold-text">Take the quiz below to find out what type of learner you are.</p>
            </div>

            <div className="quiz-content">
              <div className="question-counter">
                Question {currentQuestion + 1} of {quizQuestions.length}
              </div>
              
              <h3 className="question-text">{currentQ.question}</h3>
              
              <div className="options-grid">
                {currentQ.options.map((option, idx) => (
                  <div
                    key={idx}
                    className={`option-card ${selectedOption === idx ? 'selected' : ''}`}
                    onClick={() => selectQuizOption(option.type, idx)}
                  >
                    <img 
                      src={OPTION_IMAGES[option.imageKey]} 
                      alt={option.text}
                      className="option-image"
                    />
                    <p className="option-text">{option.text}</p>
                  </div>
                ))}
              </div>

              <div className="navigation">
                {currentQuestion > 0 && (
                  <button 
                    className="btn btn-secondary"
                    onClick={() => {
                      setCurrentQuestion(currentQuestion - 1);
                      setSelectedOption(null);
                    }}
                  >
                    <span>←</span> Previous
                  </button>
                )}
                <button 
                  className="btn"
                  onClick={nextQuestion}
                  disabled={selectedOption === null}
                >
                  {currentQuestion < quizQuestions.length - 1 ? 'Next' : 'Finish Quiz'} <span>→</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Step 2: Background
  if (step === 2) {
    return (
      <div className="container">
        <div className="step active">
          <h1>Let's Personalize Your Learning Journey 🚀</h1>
          <p className="subtitle">Answer a few questions to get recommendations tailored just for you.</p>
          
          <div className="form-group">
            <label>What's your current skill level?</label>
            <div className="radio-group">
              <div className="radio-option">
                <input 
                  type="radio" 
                  id="beginner" 
                  name="skillLevel" 
                  value="Beginner"
                  checked={skillLevel === "Beginner"}
                  onChange={(e) => setSkillLevel(e.target.value)}
                />
                <label htmlFor="beginner">Beginner</label>
              </div>
              <div className="radio-option">
                <input 
                  type="radio" 
                  id="intermediate" 
                  name="skillLevel" 
                  value="Intermediate"
                  checked={skillLevel === "Intermediate"}
                  onChange={(e) => setSkillLevel(e.target.value)}
                />
                <label htmlFor="intermediate">Intermediate</label>
              </div>
              <div className="radio-option">
                <input 
                  type="radio" 
                  id="advanced" 
                  name="skillLevel" 
                  value="Advanced"
                  checked={skillLevel === "Advanced"}
                  onChange={(e) => setSkillLevel(e.target.value)}
                />
                <label htmlFor="advanced">Advanced</label>
              </div>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="primaryGoal">What's your primary learning goal?</label>
            <select 
              id="primaryGoal" 
              value={primaryGoal}
              onChange={(e) => setPrimaryGoal(e.target.value)}
              required
            >
              <option value="">Select your goal</option>
              <option value="Data Science">Data Science</option>
              <option value="Web Development">Web Development</option>
              <option value="Artificial Intelligence">Artificial Intelligence</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div className="navigation">
            <button className="btn btn-secondary" onClick={() => setStep(1)}>
              <span>←</span> Previous
            </button>
            <button 
              className="btn" 
              onClick={handleStep2Next}
              disabled={!skillLevel || !primaryGoal}
            >
              Next <span>→</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Step 3: Time Commitment
  if (step === 3) {
    return (
      <div className="container">
        <div className="step active">
          <h1>Almost Done! ⏰</h1>
          <p className="subtitle">One more thing to help us tailor your experience</p>
          
          <div className="form-group">
            <label htmlFor="timeCommitment">Weekly time commitment</label>
            <select 
              id="timeCommitment" 
              value={timeCommitment}
              onChange={(e) => setTimeCommitment(e.target.value)}
              required
            >
              <option value="5h/week">5h/week</option>
              <option value="10h/week">10h/week</option>
              <option value="15h/week">15h/week</option>
              <option value="20h/week">20h/week</option>
            </select>
          </div>

          <div className="navigation">
            <button className="btn btn-secondary" onClick={() => setStep(2)}>
              <span>←</span> Previous
            </button>
            <button className="btn" onClick={handleStep3Next}>
              See my learner type <span>✨</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Step 4: Learner Type Summary
  if (step === 4) {
    const { dominant, ties } = getDominantType(learnerTypeScores);
    const isMixed = dominant.startsWith("mixed:");
    const typeKey = isMixed ? ties[0] : dominant;
    const desc = isMixed
      ? `Mixed learner: ${ties.map(t => capitalize(t)).join(" + ")}.`
      : `${capitalize(typeKey)} learner. ${TYPE_DESCRIPTIONS[typeKey as keyof typeof TYPE_DESCRIPTIONS]}`;
    const pct = getPercentages(learnerTypeScores);

    return (
      <div className="container">
        <div className="step active">
          <h1>Your learner type 🎯</h1>
          <p className="subtitle">Here's the result from the 10‑question quiz along with a quick breakdown:</p>
          
          <div className="summary-card">
            <div className="summary-header">
              <span className="learner-badge">{isMixed ? "Mixed" : capitalize(typeKey)}</span>
              <h2>{isMixed ? `Mixed learner (${ties.map(capitalize).join(" + ")})` : `${capitalize(typeKey)} learner`}</h2>
              <p className="summary-desc">{desc}</p>
            </div>
            
            <div className="score-list">
              {["visual", "auditory", "reading", "kinesthetic"].map((k) => (
                <div key={k} className="score-row">
                  <span className="score-label">{capitalize(k)}</span>
                  <div className="score-bar-wrap">
                    <div className="score-bar" style={{ width: `${pct[k]}%` }}></div>
                  </div>
                  <span className="score-value">{pct[k]}%</span>
                </div>
              ))}
            </div>
          </div>

          <div className="navigation">
            <button className="btn" onClick={confirmLearnerType}>
              Finish <span>→</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default Onboarding;