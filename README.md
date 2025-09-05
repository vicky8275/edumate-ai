# EduMate AI

EduMate AI is a comprehensive academic productivity platform powered by AI. It features:

- **Unified Dashboard**: Access all tools from a single sidebar navigation.
- **User Authentication**: Secure local login and signup.
- **Student Dashboard**: Personalized tasks, urgent reminders, and productivity tools.
- **AI Tools**:
  - **Quiz Master**: Generate and take quizzes on any topic.
  - **Document Summarizer**: Summarize uploaded PDFs or DOCX files.
  - **Flashcard Generator**: Create flashcards from documents or manual text.
  - **Study Planner**: Generate personalized study plans.
  - **Progress Tracker**: Visualize your academic progress and achievements.
- **Admin Panel**: Manage subjects and topics.
- **Knowledge Base**: RAG-powered context from local files and syllabus.

## How to Run

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Start the app:
   ```sh
   streamlit run main.py
   ```

## Project Structure
- `main.py` - Main entry point and navigation
- `_pages/` - All page logic (not visible as Streamlit multipage)
- `agents/` - AI agent logic (Quiz, Summarizer, Flashcard, Planner, Tracker)
- `data_manager.py` - Local SQLite data management
- `vector_rag.py` - Vector search and RAG logic
- `productivity_tools.py` - Pomodoro timer and productivity tips
- `knowledge_base/` - Local knowledge files
- `data/` - SQLite DB and syllabus

## Features
- Modern UI with dark mode
- Downloadable results (quizzes, summaries, flashcards, study plans)
- All navigation via sidebar for a clean user experience

## Requirements
- Python 3.8+
- See `requirements.txt` for all dependencies

---

For any issues or contributions, please open an issue or pull request on GitHub.
