# pages/agents_tools_page.py
import streamlit as st
from agents.quiz_agent import QuizAgent
from agents.summarizer_agent import SummarizerAgent
from agents.flashcard_agent import FlashcardAgent
from agents.planner_agent import PlannerAgent
from agents.tracker_agent import TrackerAgent
from data_manager import get_all_subjects, get_tasks
from datetime import datetime
from collections import defaultdict


def render_agents_tools_page(user_id):
    """
    Renders a unified page for various AI-powered academic tools.
    """
    st.title("🛠️ EduMate AI Tools")
    st.write("Explore powerful AI agents to enhance your learning experience!")

    # Dropdown to select the tool
    tool_options = {
        "❓ Quiz Master": "quiz",
        "📝 Document Summarizer": "summarizer",
        "🧠 Flashcard Generator": "flashcard",
        "📅 Study Planner": "planner",
        "📊 Progress Tracker": "tracker",
    }
    
    # Initialize session state for selected tool if not present
    if 'selected_ai_tool' not in st.session_state:
        st.session_state.selected_ai_tool = "quiz" # Default to quiz

    # Streamlit Selectbox to choose the tool
    selected_tool_display = st.selectbox(
        "Choose an AI Tool:",
        list(tool_options.keys()),
        key="ai_tool_selector",
        index=list(tool_options.values()).index(st.session_state.selected_ai_tool) # Set initial selection
    )
    
    # Update session state when a new tool is selected
    st.session_state.selected_ai_tool = tool_options[selected_tool_display]
    
    st.markdown("---") # Separator below the selector

    # --- Render selected tool's UI ---
    if st.session_state.selected_ai_tool == "quiz":
        render_quiz_tool(user_id)
    elif st.session_state.selected_ai_tool == "summarizer":
        render_summarizer_tool()
    elif st.session_state.selected_ai_tool == "flashcard":
        render_flashcard_tool()
    elif st.session_state.selected_ai_tool == "planner":
        render_planner_tool(user_id) # Planner needs user_id for context
    elif st.session_state.selected_ai_tool == "tracker":
        render_tracker_tool(user_id)


# --- Individual Tool Rendering Functions (Adapted and cleaned for unified page) ---

def render_quiz_tool(user_id):
    # Removed st.header, st.write (as they are above in render_agents_tools_page)
    # st.header("❓ Quiz Master")
    st.markdown("#### ❓ Quiz Master") # Smaller header for section within tool page
    st.write("Generate custom quizzes on any topic from your syllabus or general knowledge! You'll get explanations for every answer. ✨")

    quiz_agent = QuizAgent()

    # Initialize quiz_questions and current_score in session state (specific to quiz tool)
    if 'quiz_questions_tool' not in st.session_state: # Changed key to avoid conflicts
        st.session_state.quiz_questions_tool = []
    if 'current_score_data_tool' not in st.session_state: # Changed key
        st.session_state.current_score_data_tool = None
    if 'quiz_topic_tool' not in st.session_state: # Changed key
        st.session_state.quiz_topic_tool = ""
    
    # Check if a quiz is active
    quiz_active = len(st.session_state.quiz_questions_tool) > 0

    # --- Quiz Generation Section ---
    if not quiz_active:
        st.markdown("---")
        st.subheader("Generate a New Quiz")

        # Subject Selection (Moved OUTSIDE the form for reactivity within this tool)
        available_subjects_list = get_all_subjects(user_id)
        available_subjects_map = {s['name']: s for s in available_subjects_list}
        subject_names = ["(General Knowledge)"] + sorted(list(available_subjects_map.keys()))
        
        # Use session state for reactive subject selection
        if 'quiz_selected_subject_name_global_for_tool' not in st.session_state: # Unique key
            st.session_state.quiz_selected_subject_name_global_for_tool = "(General Knowledge)"

        st.session_state.quiz_selected_subject_name_global_for_tool = st.selectbox(
            "Select Subject/Area for Quiz",
            subject_names,
            key="quiz_subject_select_global_for_tool" # Global key to ensure reactivity
        )

        # Form for Quiz Parameters and Topic Selection
        with st.form("quiz_generation_form_tool", clear_on_submit=False): # Unique form key
            available_topics = ["(Any Topic in Subject)"]
            if st.session_state.quiz_selected_subject_name_global_for_tool != "(General Knowledge)":
                selected_subject_obj = available_subjects_map.get(st.session_state.quiz_selected_subject_name_global_for_tool)
                if selected_subject_obj and selected_subject_obj['topics']:
                    available_topics.extend(selected_subject_obj['topics'])
                available_topics = sorted(list(set(available_topics)))

            quiz_topic_input = st.selectbox(
                "Specify Topic (e.g., 'Thermodynamics' or leave as '(Any Topic in Subject)')",
                available_topics,
                key="quiz_topic_input_select_tool" # Unique key
            )

            num_questions = st.slider("Number of Questions", 1, 10, 5, key="num_questions_tool")
            difficulty = st.selectbox("Difficulty Level", ["Easy", "Intermediate", "Hard"], key="difficulty_tool")
            question_types = st.multiselect("Question Types", 
                                            ["Multiple Choice", "True-False"],
                                            default=["Multiple Choice"], key="question_types_tool")
            
            generate_quiz_button = st.form_submit_button("Generate Quiz")

            if generate_quiz_button:
                if not question_types:
                    st.error("Please select at least one question type.")
                else:
                    final_quiz_topic = quiz_topic_input
                    if st.session_state.quiz_selected_subject_name_global_for_tool != "(General Knowledge)" and quiz_topic_input == "(Any Topic in Subject)":
                        final_quiz_topic = st.session_state.quiz_selected_subject_name_global_for_tool
                    elif st.session_state.quiz_selected_subject_name_global_for_tool == "(General Knowledge)" and quiz_topic_input != "(Any Topic in Subject)":
                         final_quiz_topic = quiz_topic_input
                    elif st.session_state.quiz_selected_subject_name_global_for_tool == "(General Knowledge)" and quiz_topic_input == "(Any Topic in Subject)":
                        final_quiz_topic = "General Knowledge"

                    st.session_state.quiz_topic_tool = final_quiz_topic

                    with st.spinner("Generating your quiz... This might take a moment!"):
                        try:
                            questions = quiz_agent.create_quiz(
                                topic=final_quiz_topic,
                                num_questions=num_questions,
                                difficulty=difficulty,
                                question_types=question_types
                            )
                            st.session_state.quiz_questions_tool = questions
                            st.session_state.current_score_data_tool = None
                            st.success("Quiz generated successfully! Start answering below.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error generating quiz: {e}")
                            st.session_state.quiz_questions_tool = []

    # --- Quiz Taking Section ---
    if quiz_active:
        st.markdown("---")
        st.subheader(f"Quiz on: {st.session_state.quiz_topic_tool}")
        st.write("Answer the questions below and then submit to see your score!")

        user_answers = {}
        with st.form("quiz_answers_form_tool"): # Unique form key
            for i, q_data in enumerate(st.session_state.quiz_questions_tool):
                st.markdown(f"#### Question {i+1}: {q_data['question']}")
                
                if q_data['type'].lower() == 'multiple choice' and q_data.get('options'):
                    options = [opt[3:].strip() if opt.startswith(('A)', 'B)', 'C)', 'D)')) else opt.strip() for opt in q_data['options']]
                    if options:
                        user_answers[f"q_{i+1}"] = st.radio(
                            "Your Answer:",
                            options,
                            key=f"q_{i+1}_ans_tool"
                        )
                    else:
                        user_answers[f"q_{i+1}"] = st.text_input("Your Answer:", key=f"q_{i+1}_ans_text_fallback_mc_tool")
                elif q_data['type'].lower() == 'true-false':
                    user_answers[f"q_{i+1}"] = st.radio(
                        "Your Answer:",
                        ["True", "False"],
                        key=f"q_{i+1}_ans_tool"
                    )
                else:
                    user_answers[f"q_{i+1}"] = st.text_input(
                        "Your Answer:",
                        key=f"q_{i+1}_ans_text_tool"
                    )
                st.markdown("---")
            
            submit_quiz_button = st.form_submit_button("Submit Quiz & See Results")

            if submit_quiz_button:
                st.session_state.current_score_data_tool = quiz_agent.calculate_score(
                    st.session_state.quiz_questions_tool, user_answers
                )
                quiz_agent.save_quiz_performance( # This saves to general quiz_history
                    st.session_state.quiz_topic_tool, 
                    st.session_state.current_score_data_tool
                )
                st.success("Quiz submitted! Check your results below.")
                st.rerun()

        # --- Quiz Results Section ---
        if st.session_state.current_score_data_tool:
            st.markdown("---")
            st.subheader("Your Quiz Results!")
            formatted_results = quiz_agent.format_quiz_results(
                st.session_state.quiz_topic_tool, 
                st.session_state.current_score_data_tool
            )
            st.markdown(formatted_results)

            st.download_button(
                label="Download Quiz Results",
                data=formatted_results,
                file_name=f"quiz_results_{st.session_state.quiz_topic_tool}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
            
            if st.button("Generate New Quiz", key="generate_new_quiz_button_results_tool"): # Unique key
                st.session_state.quiz_questions_tool = []
                st.session_state.current_score_data_tool = None
                st.session_state.quiz_topic_tool = ""
                st.rerun()

    # --- Quiz History Section ---
    st.markdown("---")
    st.subheader("Quiz History")
    quiz_history = quiz_agent.get_quiz_history() # Retrieves from st.session_state.quiz_history

    if quiz_history:
        for i, record in enumerate(quiz_history):
            with st.container(border=True):
                st.markdown(f"**Topic:** {record['topic']}")
                st.markdown(f"**Date:** {record['date']}")
                st.markdown(f"**Score:** {record['correct_answers']}/{record['total_questions']} ({record['score_percentage']:.1f}%)")
                st.markdown(f"**Grade:** {record['grade']}")
    else:
        st.info("You haven't taken any quizzes yet. Generate one above to get started! 🚀")


def render_summarizer_tool():
    # st.header("📝 Document Summarizer")
    st.markdown("#### 📝 Document Summarizer") # Smaller header
    st.write("Upload a document (PDF or DOCX) to get a quick summary of its key points!")

    summarizer_agent = SummarizerAgent()

    uploaded_file = st.file_uploader("Upload Document", type=["pdf", "docx"], key="summarizer_uploader")

    if uploaded_file:
        summary_length = st.selectbox(
            "Summary Length:",
            ["Brief (3-5 key points)", "Detailed (7-10 key points)", "Comprehensive (10+ key points)"],
            key="summary_length_select"
        )
        focus_area = st.selectbox(
            "Focus Summary On:",
            ["General Overview", "Main Arguments", "Key Concepts", "Important Facts", "Conclusions"],
            key="focus_area_select"
        )

        if st.button("Generate Summary", key="generate_summary_button"):
            with st.spinner("Generating summary... This might take a moment!"):
                try:
                    summary_text = summarizer_agent.summarize_document(uploaded_file, summary_length, focus_area)
                    st.markdown(summary_text)
                    st.download_button(
                        label="Download Summary",
                        data=summary_text,
                        file_name=f"summary_{uploaded_file.name.split('.')[0]}.md",
                        mime="text/markdown",
                        key="download_summary_button"
                    )
                except Exception as e:
                    st.error(f"Error generating summary: {e}")

def render_flashcard_tool():
    # st.header("🧠 Flashcard Generator")
    st.markdown("#### 🧠 Flashcard Generator") # Smaller header
    st.write("Upload a document (PDF or DOCX) to instantly create flashcards for effective memorization!")

    flashcard_agent = FlashcardAgent()

    uploaded_file = st.file_uploader("Upload Document for Flashcards", type=["pdf", "docx"], key="flashcard_uploader")

    if uploaded_file:
        num_cards = st.slider("Number of Flashcards", 1, 20, 5, key="num_cards_slider")
        difficulty = st.selectbox("Difficulty Level", ["Basic", "Intermediate", "Advanced"], key="flashcard_difficulty_select")
        shuffle = st.checkbox("Shuffle Flashcards", value=True, key="flashcard_shuffle_checkbox")

        if st.button("Generate Flashcards", key="generate_flashcards_button"):
            with st.spinner("Generating flashcards... This might take a moment!"):
                try:
                    flashcards = flashcard_agent.generate_flashcards(uploaded_file, num_cards, difficulty, shuffle)
                    st.session_state.current_flashcards_tool = flashcards # Store for display (unique key)

                    if flashcards:
                        st.subheader("Your New Flashcards!")
                        for i, card in enumerate(st.session_state.current_flashcards_tool):
                            with st.expander(f"Card {i+1}: {card['term'][:50]}..."): # Show first 50 chars of term
                                st.markdown(f"**Term:** {card['term']}")
                                st.markdown(f"**Definition:** {card['definition']}")
                                st.markdown("---")

                        st.download_button(
                            label="Download Flashcards (Printable)",
                            data=flashcard_agent.format_flashcards_for_print(flashcards, uploaded_file.name),
                            file_name=f"flashcards_{uploaded_file.name.split('.')[0]}.txt",
                            mime="text/plain",
                            key="download_flashcards_button"
                        )
                    else:
                        st.info("No flashcards generated. Try adjusting parameters or using a different document.")
                except Exception as e:
                    st.error(f"Error generating flashcards: {e}")

def render_planner_tool(user_id): # Planner needs user_id
    # st.header("📅 Study Planner")
    st.markdown("#### 📅 Study Planner") # Smaller header
    st.write("Get a personalized study plan generated just for you!")

    planner_agent = PlannerAgent()

    with st.form("study_plan_form_tool"): # Unique form key
        topic = st.text_input("Learning Goal/Topic (e.g., 'Linear Algebra', 'Python Basics')", key="planner_topic_input")
        duration = st.selectbox("Study Duration", ["1 Week", "2 Weeks", "1 Month", "3 Months", "6 Months"], key="planner_duration_select")
        daily_time = st.text_input("Daily Available Study Time (e.g., '2 hours', '90 minutes')", key="planner_daily_time_input")
        current_level = st.selectbox("Your Current Level", ["Beginner", "Intermediate", "Advanced"], key="planner_level_select")
        learning_style = st.selectbox("Your Preferred Learning Style", ["Theory-focused", "Hands-on/Project-based", "Mixed approach"], key="planner_style_select")

        submitted = st.form_submit_button("Generate Study Plan")

        if submitted:
            if not topic:
                st.error("Please enter a learning goal/topic.")
            else:
                with st.spinner("Generating your personalized study plan..."):
                    try:
                        study_plan_content = planner_agent.create_study_plan(topic, duration, daily_time, current_level, learning_style)
                        st.session_state.current_study_plan = study_plan_content # Still uses this common key for tracker
                        st.session_state.plan_duration = duration # Still uses this common key for tracker
                        st.markdown(study_plan_content)

                        st.download_button(
                            label="Download Study Plan",
                            data=study_plan_content,
                            file_name=f"study_plan_{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md",
                            mime="text/markdown",
                            key="download_plan_button"
                        )
                    except Exception as e:
                        st.error(f"Error generating study plan: {e}")

    # Optional: Display current study plan if one exists in session state
    if 'current_study_plan' in st.session_state and st.session_state.current_study_plan:
        st.markdown("---")
        st.subheader("Active Study Plan:")
        with st.expander("View Active Plan Details"):
            st.markdown(st.session_state.current_study_plan)


def render_tracker_tool(user_id):
    # st.header("📊 Progress Tracker")
    st.markdown("#### 📊 Progress Tracker") # Smaller header
    st.write("Monitor your overall academic progress, task completion, and quiz performance.")

    tracker_agent = TrackerAgent()

    # Pass user_id to display_tracker_interface as it needs to fetch user-specific data
    # The display_tracker_interface method internally uses st.session_state.quiz_history
    # and st.session_state.current_study_plan which are managed by other tools/main.py
    tracker_agent.display_tracker_interface()
