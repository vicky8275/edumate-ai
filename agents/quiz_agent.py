# quiz_agent.py
import os
import streamlit as st
from datetime import datetime
import ollama # Changed from google.generativeai
import requests # Needed for Ollama error handling
import json
import random

class QuizAgent:
    def __init__(self):
        """Initialize the Quiz Agent with Ollama."""
        # No API key check here as it uses local Ollama server
        self.model_name = "phi3" # Specify Ollama model name
    
    def create_quiz_prompt(self, topic: str, num_questions: int, difficulty: str, question_types: list) -> str:
        """Create a detailed prompt for generating quiz questions."""
        
        question_type_str = " and ".join(question_types)
        
        prompt = f"""
        You are an expert quiz creator and educator. Generate a comprehensive quiz based on the following specifications:

        **Topic:** {topic}
        **Number of Questions:** {num_questions}
        **Difficulty Level:** {difficulty}
        **Question Types:** {question_type_str}

        **Quiz Requirements:**
        1. Create exactly {num_questions} questions about {topic}.
        2. Mix the question types as specified: {question_type_str}.
        3. Ensure questions match the {difficulty} difficulty level.
        4. Provide clear, unambiguous questions.
        5. For multiple choice questions, provide 4 options (A, B, C, D).
        6. For true/false questions, make statements clear and definitive.
        7. **Crucially: Include detailed explanations for all correct answers.** These explanations should clarify the concept and reasoning, even for incorrect options if applicable.

        **Difficulty Guidelines:**
        - Easy: Basic concepts, definitions, simple recall.
        - Intermediate: Application of concepts, analysis, moderate complexity.
        - Hard: Complex analysis, synthesis, advanced application, critical thinking.

        **Response Format (STRICTLY FOLLOW THIS EXACT FORMAT):**
        Question [number]: [Question text]
        Type: [Multiple Choice/True-False/Fill-in-the-Blank - choose from specified types]
        A) [Option A] (for multiple choice only)
        B) [Option B] (for multiple choice only)
        C) [Option C] (for multiple choice only)
        D) [Option D] (for multiple choice only)
        Correct Answer: [Letter (A, B, C, D) or True/False text or specific answer text]
        Explanation: [Detailed explanation of why this is correct and clarifying concepts]

        ---
        Question 2: ...
        ---

        Generate the quiz now:
        """
        
        return prompt
    
    def generate_quiz_questions(self, prompt: str) -> str:
        """Generate quiz questions using Ollama API."""
        try:
            # Use ollama.generate for local LLM
            response = ollama.generate(model=self.model_name, prompt=prompt, options={"temperature": 0.7, "num_predict": 4000}) # Increased num_predict
            
            if not response['response']:
                raise Exception("Empty response from Ollama")
            
            return response['response'].strip()
        
        except requests.exceptions.ConnectionError:
            raise Exception("Ollama server not running. Please ensure Ollama is running and the 'phi3' model is pulled.")
        except Exception as e:
            raise Exception(f"Error generating quiz: {str(e)}")
    
    def parse_quiz_response(self, response: str) -> list:
        """Parse the AI response into structured quiz data."""
        questions = []
        current_question = {}
        
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('Question'):
                if current_question:
                    questions.append(current_question)
                current_question = {
                    'question': line.split(':', 1)[1].strip() if ':' in line else line,
                    'type': '',
                    'options': [],
                    'correct_answer': '',
                    'explanation': ''
                }
            elif line.startswith('Type:'):
                current_question['type'] = line.split(':', 1)[1].strip()
            elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                current_question['options'].append(line)
            elif line.startswith('Correct Answer:'):
                current_question['correct_answer'] = line.split(':', 1)[1].strip()
            elif line.startswith('Explanation:'):
                current_question['explanation'] = line.split(':', 1)[1].strip()
            elif current_question and 'explanation' in current_question and not current_question['explanation'].endswith(('Explanation:')) and '---' not in line:
                # Continue explanation if it spans multiple lines, avoid re-adding 'Explanation:'
                current_question['explanation'] += ' ' + line
        
        # Add the last question
        if current_question:
            questions.append(current_question)
        
        return questions
    
    def create_quiz(self, topic: str, num_questions: int, difficulty: str, question_types: list) -> list:
        """Main method to create quiz questions."""
        try:
            # Step 1: Validate inputs
            if not topic.strip():
                raise Exception("Please enter a valid topic for the quiz")
            
            if num_questions < 1 or num_questions > 50:
                raise Exception("Number of questions must be between 1 and 50")
            
            # Step 2: Create quiz prompt
            st.info("🎯 Preparing quiz questions...")
            prompt = self.create_quiz_prompt(topic, num_questions, difficulty, question_types)
            
            # Step 3: Generate quiz using Ollama
            st.info("❓ Generating quiz questions...")
            quiz_response = self.generate_quiz_questions(prompt)
            
            # Step 4: Parse response into structured data
            st.info("📝 Processing quiz format...")
            questions = self.parse_quiz_response(quiz_response)
            
            # Basic validation to ensure questions were parsed
            if not questions or len(questions) < num_questions / 2: # Accept slightly fewer than requested
                print(f"WARNING: Generated {len(questions)} questions, expected {num_questions}. Raw response:\n{quiz_response}")
                if len(questions) == 0:
                    raise Exception("Failed to generate valid quiz questions. Please try again with a simpler topic or fewer questions.")
            
            return questions
        
        except Exception as e:
            raise Exception(f"Quiz creation failed: {str(e)}")
    
    def calculate_score(self, questions: list, user_answers: dict) -> dict:
        """Calculate quiz score and generate performance report."""
        total_questions = len(questions)
        correct_answers = 0
        detailed_results = []
        
        for i, question in enumerate(questions):
            question_num = i + 1
            # Standardize user input and correct answer for comparison
            user_answer_processed = str(user_answers.get(f"q_{question_num}", "")).strip().lower()
            correct_answer_processed = str(question['correct_answer']).strip().lower()

            is_correct = user_answer_processed == correct_answer_processed
            
            if is_correct:
                correct_answers += 1
            
            detailed_results.append({
                'question_num': question_num,
                'question': question['question'],
                'user_answer': user_answers.get(f"q_{question_num}", ""), # Keep original user answer
                'correct_answer': question['correct_answer'], # Keep original correct answer
                'is_correct': is_correct,
                'explanation': question['explanation']
            })
        
        score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        # Determine grade
        if score_percentage >= 90:
            grade = "A+"
        elif score_percentage >= 80:
            grade = "A"
        elif score_percentage >= 70:
            grade = "B"
        elif score_percentage >= 60:
            grade = "C"
        elif score_percentage >= 50:
            grade = "D"
        else:
            grade = "F"
        
        return {
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'score_percentage': score_percentage,
            'grade': grade,
            'detailed_results': detailed_results
        }
    
    def save_quiz_performance(self, topic: str, score_data: dict):
        """Save quiz performance to session state for history tracking."""
        if 'quiz_history' not in st.session_state:
            st.session_state.quiz_history = []
        
        performance_record = {
            'topic': topic,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'score_percentage': score_data['score_percentage'],
            'grade': score_data['grade'],
            'total_questions': score_data['total_questions'],
            'correct_answers': score_data['correct_answers']
        }
        
        st.session_state.quiz_history.append(performance_record)
    
    def get_quiz_history(self) -> list:
        """Retrieve quiz performance history."""
        return st.session_state.get('quiz_history', [])
    
    def format_quiz_results(self, topic: str, score_data: dict) -> str:
        """Format quiz results for display or download."""
        current_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        formatted = f"""
### 🎯 Quiz Results

**Topic:** {topic}
**Date:** {current_date}
**Score:** {score_data['correct_answers']}/{score_data['total_questions']} ({score_data['score_percentage']:.1f}%)
**Grade:** {score_data['grade']}

---

### 📊 Detailed Results:

"""
        
        for result in score_data['detailed_results']:
            status_emoji = "✅" if result['is_correct'] else "❌"
            formatted += f"""
**Question {result['question_num']}:** {result['question']}
{status_emoji} **Your Answer:** {result['user_answer']}
**Correct Answer:** {result['correct_answer']}
**Explanation:** {result['explanation']}

---
"""
        
        formatted += "\n*Generated by EduMate AI Assistant*"
        return formatted.strip()
