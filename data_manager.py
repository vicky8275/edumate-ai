import json
import os

def load_json(file_path, default_value=None):
    if default_value is None:
        default_value = []
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True) # Ensure data directory exists
        with open(file_path, "w") as f:
            json.dump(default_value, f, indent=4)
        return default_value
    try:
        with open(file_path, "r") as f:
            content = f.read().strip()
            if not content:
                return default_value
            return json.loads(content)
    except (json.JSONDecodeError, FileNotFoundError):
        return default_value

def save_json(file_path, data):
    os.makedirs(os.path.dirname(file_path), exist_ok=True) # Ensure data directory exists
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def get_all_subjects():
    return load_json("data/syllabus.json", [])

def add_task(task_name, due_date):
    tasks = load_json("data/tasks.json", [])
    tasks.append({"task": task_name, "due_date": str(due_date), "completed": False})
    save_json("data/tasks.json", tasks)

def get_tasks():
    return load_json("data/tasks.json", [])

def mark_task_completed(task_index):
    tasks = load_json("data/tasks.json", [])
    if 0 <= task_index < len(tasks):
        tasks[task_index]["completed"] = True
        save_json("data/tasks.json", tasks)
        return True
    return False