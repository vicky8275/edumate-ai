import requests
from vector_rag import get_relevant_context
from data_manager import get_all_subjects, get_tasks
import os
from dotenv import load_dotenv
import ollama

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

OLLAMA_MODEL = "phi3:3.8b"

def search_resources(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": query
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json()
        items = results.get("items", [])
        if items:
            snippets = [item.get("snippet", "") for item in items[:5]]
            return " ".join(snippets) if snippets else "No information found on the web."
        return "No information found on the web."
    except requests.RequestException as e:
        print(f"Error fetching information from the web: {str(e)}")
        return f"Error fetching information from the web: {str(e)}"

def get_chatbot_response(query, chat_history=None):
    if chat_history is None:
        chat_history = []

    query_lower = query.lower()
    
    subjects = get_all_subjects()
    subject_list = "\n".join([f"- {s['name']}: {', '.join(s['topics'])}" for s in subjects])
    
    all_tasks = get_tasks()
    task_list_for_llm_context = "\n".join([f"- {t['task']} (Due: {t['due_date']}) - {'Completed' if t.get('completed', False) else 'Pending'}" for t in all_tasks])

    full_prompt = f"""
    You are EduMate, a super friendly 🤗 and highly knowledgeable academic assistant for students.
    Your goal is to provide comprehensive, detailed, and factually accurate answers across a wide range of academic subjects and general knowledge.
    Always use a warm, encouraging, and positive tone. Feel free to use relevant emojis 🎉🧠✨ to make the conversation engaging and lively!
    You can retrieve information from your internal knowledge base (syllabus, key concepts) and perform real-time web searches for current or broader topics.
    Always strive to be helpful, clear, and encouraging.
    If a query implies a continuation of a previous topic, use the conversation history to understand the context.
    If your internal knowledge is insufficient for a detailed answer, rely on web search results heavily.

    Available Subjects and their topics (for general reference):
    {subject_list}
    Current Tasks (for general reference, including completion status):
    {task_list_for_llm_context}

    --- Conversation History ---
    """

    clean_history = [m for m in chat_history if m and m.get("content")]
    history_for_prompt = []
    if clean_history:
        if clean_history[-1].get("role") == "user" and clean_history[-1].get("content") == query:
            history_for_prompt = clean_history[:-1]
        else:
            history_for_prompt = clean_history
            
    for message in history_for_prompt:
        if message["role"] == "user":
            full_prompt += f"User: {message['content']}\n"
        elif message["role"] == "assistant":
            full_prompt += f"EduMate: {message['content']}\n"

    # --- Tool Hinting ---
    tool_hint_prompt = f"""
    Based on the following CONVERSATION HISTORY and the CURRENT USER'S QUERY,
    determine the primary intent and the most appropriate tool/data source.
    Respond ONLY with one of the following tool hints, followed by a colon and the suggested tool name. Do not add any other text.
    TOOL_HINT: RAG (for specific academic topics likely in the knowledge base like definitions, core concepts, or syllabus-related questions)
    TOOL_HINT: WEB_SEARCH (for general knowledge, current events, "why is it important" questions, broader context, or if RAG is likely insufficient or topic is not in specific syllabus, or for tools like Pomodoro)
    TOOL_HINT: TASKS (for queries about current tasks or deadlines, specifically for "pending tasks" or "completed tasks" or "all tasks". Examples: "what are my tasks", "show pending tasks", "list completed assignments", "tasks", "my due dates")
    TOOL_HINT: SYLLABUS (for queries about subjects or topics in the academic roadmap. Examples: "what's in my syllabus", "tell me about subjects", "list topics in math")
    TOOL_HINT: GENERAL (for greetings, general conversation, or if no specific tool applies and a simple direct answer is expected)

    Conversation history (most recent last, up to 6 turns for better context):
    """
    for message in [m for m in clean_history[-6:] if m and m.get("content")]:
         if message["role"] == "user":
             tool_hint_prompt += f"User: {message['content']}\n"
         elif message["role"] == "assistant":
             tool_hint_prompt += f"EduMate: {message['content']}\n"
    tool_hint_prompt += f"Current User Query: {query}\n"
    tool_hint_prompt += f"Your suggested tool hint:"
    
    try:
        tool_hint_response_obj = ollama.generate(model=OLLAMA_MODEL, prompt=tool_hint_prompt, options={"temperature": 0.1, "num_predict": 50})
        tool_hint_response = tool_hint_response_obj['response'].strip()
    except requests.exceptions.ConnectionError:
        yield "Oops! 😬 I'm having a little trouble connecting to my brain (Ollama server). Please make sure Ollama is running in your terminal!"
        return
    except Exception as e:
        print(f"ERROR: Ollama tool hint generation failed: {e}")
        tool_hint_response = ""

    suggested_tool = "GENERAL"
    if tool_hint_response.startswith("TOOL_HINT:"):
        suggested_tool = tool_hint_response.replace("TOOL_HINT:", "").strip().upper()

    print(f"DEBUG: Suggested Tool: {suggested_tool}")

    combined_context = ""
    
    if "pomodoro" in query_lower:
        print("DEBUG: Forcing WEB_SEARCH for Pomodoro query.")
        suggested_tool = "WEB_SEARCH"

    if "why is it important" in query_lower or "explain" in query_lower and suggested_tool == "RAG":
        print("DEBUG: Overriding RAG to WEB_SEARCH for 'why is it important' or 'explain' query.")
        suggested_tool = "WEB_SEARCH"

    if suggested_tool == "TASKS":
        tasks = get_tasks()
        pending_tasks = [t for t in tasks if not t.get('completed', False)]
        completed_tasks = [t for t in tasks if t.get('completed', False)]

        response_parts = []
        # Check for specific keywords to determine task type
        if "pending" in query_lower or "due" in query_lower or "incomplete" in query_lower or ("what are my tasks" in query_lower and "completed" not in query_lower):
            if pending_tasks:
                response_parts.append("Here are your pending tasks, ready to be crushed! 💪\n")
                for task in pending_tasks:
                    response_parts.append(f"- {task['task']} (Due: {task['due_date']})\n")
            else:
                response_parts.append("Great news! 🎉 You have no pending tasks! You're on top of things! ✨")
        elif "completed" in query_lower or "done" in query_lower or "finished" in query_lower:
            if completed_tasks:
                response_parts.append("Fantastic job! 🎉 Here are your completed tasks:\n")
                for task in completed_tasks:
                    response_parts.append(f"- {task['task']} (Due: {task['due_date']})\n")
            else:
                response_parts.append("You haven't marked any tasks as completed yet. Time to get started! 🎯")
        else: # If user asks for just "tasks" or "all tasks" or a general task query
            if tasks:
                response_parts.append("Here's a look at all your tasks, both pending and completed! 📝\n")
                for task in tasks:
                    status = "Completed! 🎉" if task.get('completed', False) else "Pending..."
                    response_parts.append(f"- {task['task']} (Due: {task['due_date']}) - {status}\n")
            else:
                response_parts.append("You currently have no tasks added. Let's set some goals! 🎯")
        
        yield "".join(response_parts)
        return # Important: Stop further processing as tool has handled it
    elif suggested_tool == "SYLLABUS":
        if subject_list:
            yield f"Here's your academic roadmap and subjects! Let's conquer these together! 🚀\n{subject_list}"
        else:
            yield "It looks like your academic roadmap is empty for now. Time to add some exciting subjects! 📚"
        return # Important: Stop further processing as tool has handled it
    elif suggested_tool == "GENERAL":
        rag_context = get_relevant_context(query)
        if rag_context and rag_context != "No relevant context found in the syllabus or knowledge base.":
            combined_context += f"Knowledge Base Information: {rag_context}\n\n"
        
        web_result = search_resources(query)
        if "No information found on the web." not in web_result and \
           "Error fetching information from the web" not in web_result and web_result:
            combined_context += f"Web Search Information: {web_result}\n\n"

    # --- Generate Final Response (streaming) ---
    if combined_context.strip():
        full_prompt += f"\n--- Additional Context ---\n{combined_context.strip()}\n"
    elif suggested_tool not in ["TASKS", "SYLLABUS"]:
        full_prompt += "\n--- No specific external context found for this query via RAG or initial WEB_SEARCH. Relying on general knowledge and conversation history.---\n"

    full_prompt += f"\nUser: {query}\nEduMate:"

    if not combined_context.strip() and suggested_tool not in ["TASKS", "SYLLABUS"]:
        general_fallback_prompt = f"""
        You are EduMate, a friendly and helpful academic assistant.
        I couldn't find specific information from my knowledge base or the web for this particular query right now 🙁.
        Please provide a polite, helpful, and concise response based on your general knowledge and the conversation history.
        If you need more clarity, ask the user to rephrase. Remember to be encouraging and use emojis! 😊

        Conversation History:
        """
        for message in history_for_prompt:
            if message["role"] == "user":
                general_fallback_prompt += f"User: {message['content']}\n"
            elif message["role"] == "assistant":
                general_fallback_prompt += f"EduMate: {message['content']}\n"
        general_fallback_prompt += f"Current User Query: {query}\nEduMate:"

        try:
            for chunk in ollama.generate(model=OLLAMA_MODEL, prompt=general_fallback_prompt, options={"temperature": 0.5, "num_predict": 200}, stream=True):
                yield chunk['response']
            return
        except requests.exceptions.ConnectionError:
            yield "Oops! 😬 I'm having a little trouble connecting to my brain (Ollama server) to provide a response. Please make sure Ollama is running."
            return
        except Exception as e:
            print(f"ERROR: Ollama general fallback generation failed: {e}")
            yield "Oh dear! 😔 An error occurred while trying to find an answer. Could you please rephrase or ask something else? I'm here to help! ✨"
            return

    try:
        for chunk in ollama.generate(model=OLLAMA_MODEL, prompt=full_prompt, options={"temperature": 0.7, "num_predict": 1000}, stream=True):
            yield chunk['response']
    except requests.exceptions.ConnectionError:
        print("ERROR: Ollama server not running. Please ensure Ollama is running.")
        yield "Oops! 😬 I'm having a little trouble connecting to my brain (Ollama server) to provide a response. Please make sure Ollama is running."
    except Exception as e:
        print(f"ERROR: Ollama response generation failed: {e}")
        yield "Oh dear! 😔 An error occurred while trying to generate a response. Please try again! I'm here to support you. ✨"