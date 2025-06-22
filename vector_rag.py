import chromadb
import os
from data_manager import get_all_subjects # This will now fetch subjects from SQLite

client = chromadb.Client()
collection = client.get_or_create_collection(name="knowledge_base")

# Modified: initialize_vector_db no longer accepts db_instance and app_id
def initialize_vector_db():
    """
    Initializes the ChromaDB vector database with content from SQLite subjects
    and local knowledge base files.
    This function is called once from main.py after app initialization.
    """
    # Only re-initialize if the collection is empty to avoid re-indexing on every Streamlit rerun
    if collection.count() == 0:
        print("DEBUG: Initializing/Re-initializing vector database with content...")
        documents = []
        ids = []

        # --- Index Syllabus topics from SQLite (via data_manager) ---
        try:
            # get_all_subjects is now called without arguments, it fetches from SQLite
            subjects_from_db = get_all_subjects()
            if subjects_from_db:
                for subject in subjects_from_db:
                    topics = subject.get("topics", [])
                    for topic in topics:
                        # Construct a document string for the RAG
                        doc_content = f"Subject: {subject['name']}, Topic: {topic}. Due: {subject.get('due_date', 'N/A')}"
                        documents.append(doc_content)
                        # Create a unique ID for syllabus topics, sanitizing name and topic for ID
                        ids.append(f"syllabus_{subject['name'].replace(' ', '_').replace('.', '')}_{topic.replace(' ', '_').replace('.', '')}")
                print(f"Indexed {len(subjects_from_db)} subjects and their topics from SQLite DB for RAG.")
            else:
                print("No subjects found in SQLite DB to index for RAG. Please ensure default syllabus is loaded.")
        except Exception as e:
            print(f"ERROR: Failed to fetch subjects from SQLite DB for RAG indexing: {e}")
            print("Skipping SQLite syllabus indexing for RAG.")


        # --- Index local knowledge base files (e.g., history.txt, physics.txt) ---
        knowledge_base_dir = "knowledge_base"
        if os.path.exists(knowledge_base_dir):
            for filename in os.listdir(knowledge_base_dir):
                if filename.endswith(".txt"):
                    file_path = os.path.join(knowledge_base_dir, filename)
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                    # Split content into paragraphs for better retrieval chunks
                    paragraphs = content.split("\n\n")
                    for p_idx, paragraph in enumerate(paragraphs):
                        if paragraph.strip(): # Ensure paragraph is not empty
                            documents.append(paragraph.strip())
                            ids.append(f"kb_{filename.replace('.txt', '')}_{p_idx}")
            print(f"Indexed {len([d for d in documents if d.startswith('kb_')])} paragraphs from local knowledge_base TXT files.")
        else:
            print(f"WARNING: 'knowledge_base' directory not found at {os.path.abspath(knowledge_base_dir)}. RAG will be limited to syllabus only.")

        # Ensure there are documents to upsert to avoid ChromaDB errors
        if documents:
            try:
                collection.upsert(documents=documents, ids=ids)
                print(f"Vector database initialized/updated with a total of {len(documents)} documents.")
            except Exception as e:
                print(f"ERROR: Failed to upsert documents to ChromaDB: {e}")
        else:
            print("No documents found to upsert to ChromaDB collection. RAG will be empty.")
    else:
        print(f"DEBUG: ChromaDB already has {collection.count()} documents. Skipping re-initialization on rerun.")


# IMPORTANT: The module-level call to initialize_vector_db() should NOT be here.
# It is called explicitly from main.py after all app setup.


def get_relevant_context(query, num_results=3):
    """
    Retrieves relevant context from the ChromaDB vector store based on the query.
    Prioritizes detailed knowledge base documents over syllabus entries.
    """
    if collection.count() == 0:
        return "No relevant context found (knowledge base is empty or failed to initialize)."

    try:
        # Perform the query against the ChromaDB collection
        results = collection.query(query_texts=[query], n_results=num_results)

        if results["documents"] and results["documents"][0]:
            detailed_docs = []
            syllabus_docs = []
            # Extract significant words from the query to filter results
            query_words = [word for word in query.lower().split() if len(word) > 2]

            for i in range(len(results["documents"][0])):
                doc = results["documents"][0][i]
                doc_id = results["ids"][0][i]
                is_relevant_to_query = False

                if query_words:
                    # Check if any significant query word is in the document
                    for entity in query_words:
                        if entity in doc.lower():
                            is_relevant_to_query = True
                            break
                else: # If query is very short, consider all top docs potentially relevant
                    is_relevant_to_query = True

                if is_relevant_to_query:
                    # Distinguish between syllabus and other knowledge base documents based on ID prefix
                    if doc_id.startswith("syllabus_"):
                        syllabus_docs.append(doc)
                    else: # This covers other kb_*.txt files (history.txt, physics.txt etc.)
                        detailed_docs.append(doc)

            # Prioritize: detailed knowledge base content, then syllabus, then the overall top result
            if detailed_docs:
                # Join up to 2-3 detailed docs for richer context
                return " ".join(detailed_docs[:2])
            elif syllabus_docs:
                # Join up to 2-3 syllabus docs if they are the only relevant ones found
                return " ".join(syllabus_docs[:2])
            
            # Fallback: if no prioritized match, return the very first retrieved document as a last resort
            return results["documents"][0][0]

    except Exception as e:
        print(f"ERROR: Error during context retrieval: {e}")
        return "No relevant context found in the syllabus or knowledge base due to retrieval error."

    return "No relevant context found in the syllabus or knowledge base." # Default fallback message

