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