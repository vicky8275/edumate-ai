# data_manager.py
import streamlit as st
import os
import json
import sqlite3
from datetime import datetime

# --- SQLite3 Setup for Local Data ---
DB_DIRECTORY = "data"
LOCAL_DB_PATH = os.path.join(DB_DIRECTORY, "edumate_offline.db") 
# UPDATED: Path to your default syllabus file, now in the data directory
SYLLABUS_FILE_PATH = os.path.join(DB_DIRECTORY, "syllabus.json") 

def init_sqlite_db():
    """
    Initializes the SQLite database for local data storage, including user credentials.
    Ensures the database directory exists.
    """
    # Create the directory if it doesn't exist
    if not os.path.exists(DB_DIRECTORY):
        os.makedirs(DB_DIRECTORY)
        print(f"DEBUG: Created database directory: {DB_DIRECTORY}")

    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT, -- In a real app, store hashed passwords! For demo, plaintext.
            created_at TEXT
        )
    """)

    # Create tasks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT, -- This will be the username from the users table
            task TEXT,
            due_date TEXT,
            completed INTEGER,
            created_at TEXT,
            subject_name TEXT, -- New field to link to subject
            topic_name TEXT, -- New field to link to topic within a subject
            FOREIGN KEY (user_id) REFERENCES users(username)
        )
    """)
    # Create subjects table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT, -- This will be the username from the users table
            name TEXT,
            topics TEXT, -- Stored as JSON string
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(username)
        )
    """)
    conn.commit()
    conn.close()
    print("DEBUG: Local SQLite DB initialized with users, tasks, and subjects tables.")

# Initialize SQLite DB on startup
init_sqlite_db()

# --- Syllabus Loading Function ---
def load_default_syllabus():
    """Loads the default syllabus from syllabus.json."""
    if os.path.exists(SYLLABUS_FILE_PATH):
        try:
            with open(SYLLABUS_FILE_PATH, 'r', encoding='utf-8') as f:
                syllabus_data = json.load(f)
            print(f"DEBUG: Default syllabus loaded from {SYLLABUS_FILE_PATH}")
            return syllabus_data
        except Exception as e:
            print(f"ERROR: Failed to load default syllabus from {SYLLABUS_FILE_PATH}: {e}")
            return []
    else:
        print(f"WARNING: Default syllabus file not found at {SYLLABUS_FILE_PATH}")
        return []

# --- Helper function to seed default subjects ---
def seed_default_subjects_for_user(user_id):
    """Adds default subjects from syllabus.json to a user's profile if they have none."""
    existing_subjects = get_all_subjects(user_id) # Fetch existing subjects for the user
    
    if not existing_subjects: # ***CRITICAL CHANGE: Only add if the user has NO subjects yet***
        print(f"DEBUG: User {user_id} has no existing subjects. Attempting to seed default subjects.")
        default_subjects = load_default_syllabus()
        if default_subjects:
            added_count = 0
            for subject in default_subjects:
                topics_list = subject.get('topics', [])
                add_result = add_subject(user_id, subject['name'], topics_list)
                if add_result["success"]:
                    added_count += 1
                else:
                    print(f"ERROR: Failed to add default subject '{subject['name']}': {add_result['error']}")
            
            if added_count > 0:
                print(f"DEBUG: Successfully seeded {added_count} default subjects for new user: {user_id}")
            else:
                print(f"DEBUG: No default subjects found in {SYLLABUS_FILE_PATH} to seed for user: {user_id}")
        else:
            print(f"DEBUG: No default syllabus data found in {SYLLABUS_FILE_PATH} to seed for user: {user_id}")
    else:
        print(f"DEBUG: User {user_id} already has {len(existing_subjects)} subjects. Skipping default syllabus seeding.")


# --- Local User Authentication Functions ---

def signup_user_local(username, password):
    """Signs up a new local user and stores credentials in SQLite."""
    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()
    try:
        created_at = datetime.now().isoformat()
        cursor.execute("INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)",
                       (username, password, created_at))
        conn.commit()
        print(f"DEBUG: Local user '{username}' signed up successfully.")
        seed_default_subjects_for_user(username) # Call seeding function after successful signup
        return {"success": True, "user_id": username}
    except sqlite3.IntegrityError:
        print(f"ERROR: Username '{username}' already exists.")
        return {"success": False, "error": "Username already exists. Please choose a different one."}
    except Exception as e:
        print(f"ERROR: Failed to sign up user '{username}': {e}")
        return {"success": False, "error": str(e)}
    finally:
        conn.close()

def login_user_local(username, password):
    """Logs in a local user by checking credentials against SQLite."""
    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT username FROM users WHERE username = ? AND password = ?", (username, password))
        user_record = cursor.fetchone()
        if user_record:
            print(f"DEBUG: Local user '{username}' logged in successfully.")
            seed_default_subjects_for_user(username) # Call seeding function after login
            return {"success": True, "user_id": user_record[0]}
        else:
            print(f"DEBUG: Invalid credentials for user '{username}'.")
            return {"success": False, "error": "Invalid username or password."}
    except Exception as e:
        print(f"ERROR: Failed to log in user '{username}': {e}")
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


# --- Functions for Tasks (SQLite Only) ---

def add_task(user_id, task_description, due_date_str, subject_name=None, topic_name=None):
    """Adds a new task for a specific user. Uses SQLite."""
    try:
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        created_at = datetime.now().isoformat()
        cursor.execute("INSERT INTO tasks (user_id, task, due_date, completed, created_at, subject_name, topic_name) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (user_id, task_description, due_date_str, 0, created_at, subject_name, topic_name))
        conn.commit()
        task_id = cursor.lastrowid
        conn.close()
        print(f"DEBUG: SQLite Task added with ID: {task_id} for user: {user_id}")
        return {"success": True, "id": task_id}
    except Exception as e:
        print(f"ERROR: Failed to add SQLite task for user {user_id}: {e}")
        return {"success": False, "error": str(e)}


def get_tasks(user_id):
    """Retrieves all tasks for a specific user. Uses SQLite."""
    tasks = []
    try:
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, task, due_date, completed, created_at, subject_name, topic_name FROM tasks WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            tasks.append({
                "id": row[0],
                "task": row[1],
                "due_date": row[2],
                "completed": bool(row[3]),
                "created_at": datetime.fromisoformat(row[4]) if row[4] else datetime.min,
                "subject_name": row[5], # New field
                "topic_name": row[6] # New field
            })
        tasks.sort(key=lambda x: x.get("created_at", datetime.min), reverse=False)
        print(f"DEBUG: Retrieved {len(tasks)} SQLite tasks for user: {user_id}.")
    except Exception as e:
        print(f"ERROR: Failed to get SQLite tasks for user {user_id}: {e}")
        tasks = []
    return tasks


def mark_task_completed(user_id, task_id):
    """Marks a task as completed. Uses SQLite."""
    try:
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET completed = ? WHERE id = ? AND user_id = ?", (1, task_id, user_id))
        conn.commit()
        conn.close()
        print(f"DEBUG: SQLite Task {task_id} marked completed for user: {user_id}.")
        return {"success": True}
    except Exception as e:
        print(f"ERROR: Failed to mark SQLite task {task_id} completed for user {user_id}: {e}")
        return {"success": False, "error": str(e)}


def delete_task(user_id, task_id):
    """Deletes a task. Uses SQLite."""
    try:
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
        conn.commit()
        conn.close()
        print(f"DEBUG: SQLite Task {task_id} deleted for user: {user_id}.")
        return {"success": True}
    except Exception as e:
        print(f"ERROR: Failed to delete SQLite task {task_id} for user {user_id}: {e}")
        return {"success": False, "error": str(e)}


# --- Functions for Subjects (SQLite Only) ---

def add_subject(user_id, subject_name, topics_list):
    """Adds a new subject. Uses SQLite."""
    topics_str = json.dumps(topics_list) # Store list as JSON string
    try:
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        created_at = datetime.now().isoformat()
        cursor.execute("INSERT INTO subjects (user_id, name, topics, created_at) VALUES (?, ?, ?, ?)",
                       (user_id, subject_name, topics_str, created_at))
        conn.commit()
        subject_id = cursor.lastrowid
        conn.close()
        print(f"DEBUG: SQLite Subject '{subject_name}' added with ID: {subject_id} for user: {user_id}")
        return {"success": True, "id": subject_id}
    except Exception as e:
        print(f"ERROR: Failed to add SQLite subject '{subject_name}' for user {user_id}: {e}")
        return {"success": False, "error": str(e)}


def get_all_subjects(user_id):
    """Retrieves all subjects. Uses SQLite."""
    subjects = []
    try:
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, topics, created_at FROM subjects WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            subjects.append({
                "id": row[0],
                "name": row[1],
                "topics": json.loads(row[2]) if row[2] else [], # Parse topics from JSON string
                "created_at": datetime.fromisoformat(row[3]) if row[3] else datetime.min
            })
        subjects.sort(key=lambda x: x.get("created_at", datetime.min), reverse=False)
        print(f"DEBUG: Retrieved {len(subjects)} SQLite subjects for user: {user_id}.")
    except Exception as e:
        print(f"ERROR: Failed to get SQLite subjects for user {user_id}: {e}")
        subjects = []
    return subjects

def delete_subject(user_id, subject_id):
    """Deletes a subject. Uses SQLite."""
    try:
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subjects WHERE id = ? AND user_id = ?", (subject_id, user_id))
        conn.commit()
        conn.close()
        print(f"DEBUG: SQLite Subject {subject_id} deleted for user: {user_id}.")
        return {"success": True}
    except Exception as e:
        print(f"ERROR: Failed to delete SQLite subject {subject_id} for user {user_id}: {e}")
        return {"success": False, "error": str(e)}