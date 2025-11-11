import os
import groq
from typing import List, Dict, Any, Optional
import json
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

class QuizGenerator:
    def __init__(self, api_key: str = None):
        # Initialize Groq client
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
        try:
            self.client = groq.Groq(api_key=self.api_key)
            self.model = "llama-3.3-70b-versatile"
            print("✅ Groq client initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Groq client: {e}")
            raise

    def generate_real_time_feedback(self, 
                                 question_data: Dict[str, Any], 
                                 user_answer: int, 
                                 time_taken: int = None,
                                 user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate real-time feedback for a single question answer
        
        Args:
            question_data: The question data from quiz
            user_answer: Index of user's selected answer
            time_taken: Time taken to answer in seconds
            user_context: Additional user context (learning style, previous performance, etc.)
        
        Returns:
            Dictionary containing detailed feedback
        """
        try:
            is_correct = user_answer == question_data.get('correct_answer', -1)
            
            prompt = self._build_feedback_prompt(question_data, user_answer, is_correct, time_taken, user_context)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert educational tutor. Provide constructive, encouraging, 
                        and personalized feedback for quiz answers. Focus on:
                        - Explaining why the answer is correct/incorrect
                        - Providing additional context or examples
                        - Offering learning tips
                        - Being encouraging and supportive
                        - Keeping feedback concise but informative
                        Always return valid JSON format."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            msg_content = getattr(response.choices[0].message, "content", None)
            if not msg_content:
                raise ValueError("Empty response from AI model")
                
            feedback_data = json.loads(msg_content)
            
            # Enhance with basic data
            feedback_data.update({
                "is_correct": is_correct,
                "user_answer_index": user_answer,
                "correct_answer_index": question_data.get('correct_answer', -1),
                "time_taken": time_taken,
                "question_id": question_data.get('id', '')
            })
            
            return feedback_data
            
        except Exception as e:
            print(f"❌ Real-time feedback generation failed: {e}")
            # Return basic feedback as fallback
            return self._generate_basic_feedback(question_data, user_answer, time_taken)
    
    def _build_feedback_prompt(self, 
                             question_data: Dict[str, Any], 
                             user_answer: int, 
                             is_correct: bool,
                             time_taken: int = None,
                             user_context: Dict[str, Any] = None) -> str:
        """Build prompt for real-time feedback generation"""
        
        question_text = question_data.get('questions', [''])[0]
        question_type = question_data.get('type', 'mcq')
        explanation = question_data.get('explanation', '')
        
        # Get answer texts
        options = question_data.get('options', [])
        user_answer_text = options[user_answer] if user_answer < len(options) else "Unknown"
        correct_answer_index = question_data.get('correct_answer', -1)
        correct_answer_text = options[correct_answer_index] if correct_answer_index < len(options) else "Unknown"
        
        # Build context string
        context_info = ""
        if user_context:
            if user_context.get('learning_style'):
                context_info += f"\nLearning Style: {user_context['learning_style']}"
            if user_context.get('previous_performance'):
                context_info += f"\nPrevious Performance: {user_context['previous_performance']}% average"
            if user_context.get('weak_areas'):
                context_info += f"\nAreas to improve: {', '.join(user_context['weak_areas'][:3])}"
        
        time_info = f"Time taken: {time_taken} seconds" if time_taken else "Time data not available"
        
        return f"""
        Generate personalized feedback for this quiz question:
        
        QUESTION: {question_text}
        QUESTION TYPE: {question_type}
        USER'S ANSWER: {user_answer_text} (Index: {user_answer})
        CORRECT ANSWER: {correct_answer_text} (Index: {correct_answer_index})
        IS CORRECT: {is_correct}
        {time_info}
        BUILT-IN EXPLANATION: {explanation}
        {context_info}
        
        Please provide:
        1. A brief analysis of the answer
        2. Clear explanation of the correct concept
        3. A helpful tip or mnemonic
        4. Encouraging message
        
        RESPONSE FORMAT (JSON):
        {{
            "feedback_message": "Main feedback text explaining the answer",
            "detailed_explanation": "More detailed explanation of the concept",
            "learning_tip": "A helpful tip or trick to remember this",
            "encouragement": "Encouraging message based on performance",
            "suggested_resources": ["Resource 1", "Resource 2"],
            "confidence_boost": true/false,  // Whether this should boost user confidence
            "concept_tags": ["tag1", "tag2"]  // Key concepts tested
        }}
        
        Make the feedback personalized and educational. If the answer is wrong, be constructive, not critical.
        If the answer is correct, reinforce the learning and provide additional insights.
        """
    
    def _generate_basic_feedback(self, 
                               question_data: Dict[str, Any], 
                               user_answer: int, 
                               time_taken: int = None) -> Dict[str, Any]:
        """Generate basic feedback when AI fails"""
        
        is_correct = user_answer == question_data.get('correct_answer', -1)
        options = question_data.get('options', [])
        user_answer_text = options[user_answer] if user_answer < len(options) else "Unknown"
        correct_answer_index = question_data.get('correct_answer', -1)
        correct_answer_text = options[correct_answer_index] if correct_answer_index < len(options) else "Unknown"
        
        if is_correct:
            message = f"Correct! Well done. {question_data.get('explanation', '')}"
            encouragement = "Great job! You're mastering this concept."
        else:
            message = f"Not quite. The correct answer is: {correct_answer_text}. {question_data.get('explanation', '')}"
            encouragement = "Don't worry! Learning from mistakes is part of the process."
        
        return {
            "feedback_message": message,
            "detailed_explanation": question_data.get('explanation', 'No explanation available.'),
            "learning_tip": "Review this concept and try similar questions to strengthen your understanding.",
            "encouragement": encouragement,
            "suggested_resources": [],
            "confidence_boost": is_correct,
            "concept_tags": [],
            "is_correct": is_correct,
            "user_answer_index": user_answer,
            "correct_answer_index": correct_answer_index,
            "time_taken": time_taken,
            "question_id": question_data.get('id', '')
        }
    
    def generate_quiz_summary_feedback(self, 
                                    quiz_data: Dict[str, Any], 
                                    user_answers: List[Dict[str, Any]],
                                    user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate comprehensive feedback after quiz completion
        
        Args:
            quiz_data: Complete quiz data
            user_answers: List of user answers with is_correct flags
            user_context: Additional user context
        
        Returns:
            Dictionary containing summary feedback
        """
        try:
            prompt = self._build_summary_prompt(quiz_data, user_answers, user_context)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert educational coach. Provide comprehensive, 
                        personalized feedback after a quiz. Analyze patterns, identify strengths and weaknesses,
                        and provide actionable recommendations. Be encouraging and motivational.
                        Always return valid JSON format."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            msg_content = getattr(response.choices[0].message, "content", None)
            if not msg_content:
                raise ValueError("Empty response from AI model")
                
            summary_data = json.loads(msg_content)
            
            # Calculate basic metrics
            total_questions = len(user_answers)
            correct_answers = sum(1 for answer in user_answers if answer.get('is_correct', False))
            score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
            
            # Add metrics to summary
            summary_data.update({
                "total_questions": total_questions,
                "correct_answers": correct_answers,
                "score": round(score, 2),
                "performance_level": self._get_performance_level(score)
            })
            
            return summary_data
            
        except Exception as e:
            print(f"❌ Quiz summary feedback generation failed: {e}")
            return self._generate_basic_summary(quiz_data, user_answers)
    
    def _build_summary_prompt(self, 
                            quiz_data: Dict[str, Any], 
                            user_answers: List[Dict[str, Any]],
                            user_context: Dict[str, Any] = None) -> str:
        """Build prompt for quiz summary feedback"""
        
        total_questions = len(user_answers)
        correct_answers = sum(1 for answer in user_answers if answer.get('is_correct', False))
        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        # Analyze question types and performance
        question_types = {}
        for i, (question, answer) in enumerate(zip(quiz_data.get('questions', []), user_answers)):
            q_type = question.get('type', 'unknown')
            if q_type not in question_types:
                question_types[q_type] = {'total': 0, 'correct': 0}
            question_types[q_type]['total'] += 1
            if answer.get('is_correct', False):
                question_types[q_type]['correct'] += 1
        
        # Build context
        context_info = ""
        if user_context:
            if user_context.get('learning_goals'):
                context_info += f"\nLearning Goals: {user_context['learning_goals']}"
            if user_context.get('previous_scores'):
                context_info += f"\nPrevious Scores: {user_context['previous_scores']}"
        
        return f"""
        Generate comprehensive quiz summary feedback:
        
        QUIZ INFO:
        Title: {quiz_data.get('quiz_title', 'Unknown Quiz')}
        Topic: {quiz_data.get('topic', 'Unknown Topic')}
        Difficulty: {quiz_data.get('difficulty', 'Unknown')}
        
        PERFORMANCE:
        Score: {score:.1f}% ({correct_answers}/{total_questions} correct)
        
        QUESTION TYPE PERFORMANCE:
        {json.dumps(question_types, indent=2)}
        
        USER CONTEXT:
        {context_info}
        
        Please provide:
        1. Overall performance assessment
        2. Key strengths identified
        3. Main areas needing improvement
        4. Specific recommendations for study
        5. Motivational message
        6. Suggested next steps
        
        RESPONSE FORMAT (JSON):
        {{
            "overall_assessment": "Brief overall performance summary",
            "strengths": ["strength1", "strength2", "strength3"],
            "improvement_areas": ["area1", "area2", "area3"],
            "study_recommendations": [
                {{
                    "area": "Concept name",
                    "action": "Specific study action",
                    "priority": "high/medium/low"
                }}
            ],
            "next_steps": ["step1", "step2", "step3"],
            "motivational_message": "Encouraging final message",
            "performance_insights": "Detailed insights about performance patterns"
        }}
        """
    
    def _generate_basic_summary(self, 
                              quiz_data: Dict[str, Any], 
                              user_answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate basic summary when AI fails"""
        
        total_questions = len(user_answers)
        correct_answers = sum(1 for answer in user_answers if answer.get('is_correct', False))
        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        if score >= 80:
            assessment = "Excellent performance! You have a strong understanding of this topic."
        elif score >= 60:
            assessment = "Good work! You have a solid foundation with some areas to improve."
        else:
            assessment = "Keep practicing! Review the material and try again to improve your understanding."
        
        return {
            "overall_assessment": assessment,
            "strengths": ["Good effort completed the quiz"],
            "improvement_areas": ["Review incorrect answers"],
            "study_recommendations": [
                {
                    "area": "Quiz topics",
                    "action": "Review all questions and explanations",
                    "priority": "high"
                }
            ],
            "next_steps": ["Retake quiz", "Review study materials"],
            "motivational_message": "Every quiz is a learning opportunity. Keep going!",
            "performance_insights": f"Scored {score:.1f}% with {correct_answers} out of {total_questions} correct.",
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "score": round(score, 2),
            "performance_level": self._get_performance_level(score)
        }
    
    def _get_performance_level(self, score: float) -> str:
        """Convert score to performance level"""
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 60:
            return "satisfactory"
        else:
            return "needs_improvement"



    
    def generate_quiz_from_content(self, content: str, num_questions: int = 5, question_types: List[str] = None):
        """
        Generate quiz questions from provided content
        
        Args:
            content: The educational content to generate questions from
            num_questions: Number of questions to generate
            question_types: Types of questions (mcq, true_false, short_answer, fill_blank)
        
        Returns:
            Dictionary containing quiz data
        """
        try:
            if question_types is None:
                question_types = ["mcq"]

            prompt = self._build_quiz_prompt(content, num_questions, question_types)
            print("🧠 Prompt built successfully!")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": """You are an expert educational content creator. 
                        Create engaging and educational quiz questions based on the provided content.
                        Always return valid JSON format without any additional text.
                        Make sure questions are clear, accurate, and test genuine understanding."""
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )

            print("🧾 Raw Groq Response received")

            # Check content existence
            msg_content = getattr(response.choices[0].message, "content", None)
            if not msg_content:
                raise ValueError("Empty response from AI model")

            quiz_data = json.loads(msg_content)
            
            # Validate and enhance quiz data
            quiz_data = self._validate_quiz_data(quiz_data, num_questions)
            
            # Add metadata
            quiz_data["metadata"] = {
                "total_questions": len(quiz_data.get("questions", [])),
                "question_types": question_types,
                "model_used": self.model,
                "source": "content_based"
            }
            
            print(f"✅ Successfully generated {len(quiz_data.get('questions', []))} questions")
            return quiz_data

        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {str(e)}")
        except Exception as e:
            print(f"❌ Quiz generation failed: {e}")
            raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")
    
    def _build_quiz_prompt(self, content: str, num_questions: int, question_types: List[str]) -> str:
        """Build the prompt for quiz generation from content"""
        
        type_instructions = {
            "mcq": "Multiple choice questions with 4 options (A, B, C, D)",
            "true_false": "True/False questions",
            "short_answer": "Short answer questions (1-2 word answers)",
            "fill_blank": "Fill in the blank questions"
        }
        
        selected_instructions = [type_instructions.get(t, t) for t in question_types]
        
        return f"""
        Based on the following educational content, create {num_questions} quiz questions.

        EDUCATIONAL CONTENT:
        {content}

        REQUIREMENTS:
        - Create exactly {num_questions} questions
        - Question types: {', '.join(selected_instructions)}
        - For MCQs: Provide 4 plausible options with one correct answer
        - Include brief explanations for answers
        - Questions should test understanding of key concepts from the content
        - Cover different aspects of the content
        - Make questions clear and unambiguous
        - Ensure questions are directly based on the provided content

        RESPONSE FORMAT (JSON):
        {{
            "quiz_title": "Quiz Based on Educational Content",
            "questions": [
                {{
                    "id": 1,
                    "type": "mcq",
                    "question": "What is the main topic discussed?",
                    "options": {{
                        "A": "Option A text",
                        "B": "Option B text",
                        "C": "Option C text",
                        "D": "Option D text"
                    }},
                    "correct_answer": "A",
                    "explanation": "Brief explanation why this is correct based on the content"
                }},
                {{
                    "id": 2,
                    "type": "true_false",
                    "question": "This statement is true or false based on the content?",
                    "correct_answer": "true",
                    "explanation": "Brief explanation based on the content"
                }},
                {{
                    "id": 3,
                    "type": "fill_blank",
                    "question": "The concept of ______ is important in this context.",
                    "correct_answer": "expected_answer",
                    "explanation": "Brief explanation"
                }}
            ],
            "summary": {{
                "total_questions": {num_questions},
                "difficulty": "mixed",
                "estimated_time": "5-10 minutes"
            }}
        }}

        Return only valid JSON without any additional text.
        """
    
    def generate_quiz_by_topic(self, topic: str, num_questions: int = 5, difficulty: str = "beginner", question_types: List[str] = None) -> Dict[str, Any]:
        """
        Generate quiz questions on any topic without requiring content
        
        Args:
            topic: The topic to generate quiz about
            num_questions: Number of questions to generate
            difficulty: Difficulty level (beginner, intermediate, advanced)
            question_types: Types of questions (mcq, true_false, short_answer, fill_blank)
        
        Returns:
            Dictionary containing quiz data
        """
        try:
            if question_types is None:
                question_types = ["mcq"]
            
            prompt = self._build_topic_quiz_prompt(topic, num_questions, difficulty, question_types)
            
            print(f"🎯 Generating {num_questions} {difficulty} questions about: {topic}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert educational content creator. 
                        Create engaging quiz questions on any topic.
                        Always return valid JSON format without any additional text.
                        Make questions relevant, clear, and educational.
                        Ensure correct answers are accurate and explanations are helpful."""
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response
            msg_content = getattr(response.choices[0].message, "content", None)
            if not msg_content:
                raise ValueError("Empty response from AI model")
                
            quiz_data = json.loads(msg_content)
            
            # Validate and enhance quiz data
            quiz_data = self._validate_quiz_data(quiz_data, num_questions)
            
            # Add metadata
            quiz_data["metadata"] = {
                "topic": topic,
                "difficulty": difficulty,
                "total_questions": len(quiz_data.get("questions", [])),
                "question_types": question_types,
                "model_used": self.model,
                "source": "topic_based"
            }
            
            print(f"✅ Successfully generated {len(quiz_data.get('questions', []))} questions about {topic}")
            return quiz_data
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to parse AI response: {str(e)}")
        except Exception as e:
            print(f"❌ Topic quiz generation failed: {e}")
            raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")
    
    def _build_topic_quiz_prompt(self, topic: str, num_questions: int, difficulty: str, question_types: List[str]) -> str:
        """Build the prompt for topic-based quiz generation"""
        
        type_instructions = {
            "mcq": "Multiple choice questions with 4 options (A, B, C, D)",
            "true_false": "True/False questions",
            "short_answer": "Short answer questions (1-2 word answers)",
            "fill_blank": "Fill in the blank questions"
        }
        
        selected_instructions = [type_instructions.get(t, t) for t in question_types]
        
        difficulty_instructions = {
            "beginner": "basic concepts and fundamentals",
            "intermediate": "application and understanding of concepts", 
            "advanced": "complex concepts and problem-solving"
        }
        
        return f"""
        Create a {difficulty} level quiz about: {topic}
        
        REQUIREMENTS:
        - Create exactly {num_questions} questions
        - Difficulty level: {difficulty} ({difficulty_instructions.get(difficulty, 'mixed')})
        - Question types: {', '.join(selected_instructions)}
        - For MCQs: Provide 4 plausible options with one correct answer
        - Include brief but helpful explanations for answers
        - Questions should test understanding of {difficulty_instructions.get(difficulty, 'key concepts')} in {topic}
        - Make questions clear and unambiguous
        - Ensure questions are appropriate for {difficulty} level
        - Cover different aspects of {topic}
        
        RESPONSE FORMAT (JSON):
        {{
            "quiz_title": "Quiz about {topic}",
            "topic": "{topic}",
            "difficulty": "{difficulty}",
            "questions": [
                {{
                    "id": 1,
                    "type": "mcq",
                    "question": "Question text here?",
                    "options": {{
                        "A": "Option A text",
                        "B": "Option B text", 
                        "C": "Option C text",
                        "D": "Option D text"
                    }},
                    "correct_answer": "A",
                    "explanation": "Brief but helpful explanation why this is correct"
                }},
                {{
                    "id": 2,
                    "type": "true_false", 
                    "question": "This statement is true or false?",
                    "correct_answer": "true",
                    "explanation": "Brief explanation"
                }},
                {{
                    "id": 3,
                    "type": "fill_blank",
                    "question": "Complete the sentence: The main concept in {topic} is ______.",
                    "correct_answer": "expected_answer",
                    "explanation": "Brief explanation"
                }}
            ],
            "summary": {{
                "total_questions": {num_questions},
                "estimated_time": "5-10 minutes",
                "learning_objectives": [
                    "Understand {difficulty_instructions.get(difficulty, 'key concepts')} of {topic}",
                    "Apply knowledge to solve problems",
                    "Demonstrate comprehension of {topic}"
                ]
            }}
        }}
        
        Return only valid JSON without any additional text.
        """
    
    def _validate_quiz_data(self, quiz_data: Dict[str, Any], expected_questions: int) -> Dict[str, Any]:
        """Validate and enhance the quiz data structure"""
        
        # Ensure required fields exist
        if "questions" not in quiz_data:
            quiz_data["questions"] = []
        
        # Validate each question
        valid_questions = []
        for i, question in enumerate(quiz_data["questions"]):
            try:
                # Ensure question has required fields
                if not all(key in question for key in ["id", "type", "question", "correct_answer"]):
                    print(f"⚠️ Question {i} missing required fields, skipping")
                    continue
                
                # Add missing fields with defaults
                question.setdefault("explanation", "No explanation provided.")
                
                # Ensure options exist for MCQ questions
                if question["type"] == "mcq" and "options" not in question:
                    question["options"] = {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}
                
                valid_questions.append(question)
                
            except Exception as e:
                print(f"⚠️ Error validating question {i}: {e}, skipping")
                continue
        
        quiz_data["questions"] = valid_questions
        
        # Add summary if missing
        if "summary" not in quiz_data:
            quiz_data["summary"] = {
                "total_questions": len(valid_questions),
                "estimated_time": "5-10 minutes",
                "difficulty": "mixed"
            }
        
        print(f"✅ Validated {len(valid_questions)} questions (expected: {expected_questions})")
        return quiz_data
    
    def generate_adaptive_quiz(self, user_level: str, previous_performance: Dict[str, Any], topic: str, num_questions: int = 5) -> Dict[str, Any]:
        """
        Generate adaptive quiz based on user's level and previous performance
        
        Args:
            user_level: User's current level (beginner, intermediate, advanced)
            previous_performance: Dictionary containing user's previous quiz results
            topic: The topic for the quiz
            num_questions: Number of questions to generate
        
        Returns:
            Dictionary containing adaptive quiz data
        """
        try:
            # Analyze previous performance to determine appropriate difficulty
            avg_score = previous_performance.get('average_score', 50)
            
            if avg_score >= 80:
                difficulty = "advanced"
            elif avg_score >= 60:
                difficulty = "intermediate"
            else:
                difficulty = "beginner"
            
            print(f"🎯 Generating adaptive quiz: {difficulty} level for user with {avg_score}% average")
            
            # Generate quiz with determined difficulty
            return self.generate_quiz_by_topic(
                topic=topic,
                num_questions=num_questions,
                difficulty=difficulty,
                question_types=["mcq", "true_false"]
            )
            
        except Exception as e:
            print(f"❌ Adaptive quiz generation failed: {e}")
            # Fallback to basic quiz generation
            return self.generate_quiz_by_topic(
                topic=topic,
                num_questions=num_questions,
                difficulty="beginner"
            )


# Initialize quiz generator
try:
    quiz_generator = QuizGenerator()
    print("✅ AI Quiz Generator initialized successfully")
except Exception as e:
    print(f"❌ Warning: Quiz generator initialization failed: {e}")
    quiz_generator = None