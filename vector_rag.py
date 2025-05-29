import chromadb
import os
from data_manager import get_all_subjects

client = chromadb.Client()
collection = client.get_or_create_collection(name="knowledge_base")

def initialize_vector_db():
    # Clear existing collection only if it has IDs to avoid ValueError
    existing_ids = collection.get()["ids"]
    if existing_ids:  # Only delete if there are IDs
        collection.delete(ids=existing_ids)
    
    documents = []
    ids = []
    
    # Index syllabus topics from syllabus.json
    subjects = get_all_subjects()
    for idx, subject in enumerate(subjects):
        topics = subject["topics"]
        for topic in topics:
            doc = f"{subject['name']}: {topic}"
            documents.append(doc)
            ids.append(f"syllabus_{subject['name']}_{topic}")
    
    # Index knowledge base files
    knowledge_base_dir = "knowledge_base" # Assuming your .txt files are in a 'knowledge_base' directory
    if os.path.exists(knowledge_base_dir):
        for filename in os.listdir(knowledge_base_dir):
            if filename.endswith(".txt"):
                file_path = os.path.join(knowledge_base_dir, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                # Split content into paragraphs or sentences for better retrieval
                paragraphs = content.split("\n\n") # Splits by double newline
                for p_idx, paragraph in enumerate(paragraphs):
                    if paragraph.strip():
                        documents.append(paragraph)
                        ids.append(f"kb_{filename}_{p_idx}")
    
    # Ensure there are documents to upsert to avoid errors
    if documents:
        collection.upsert(documents=documents, ids=ids)

def get_relevant_context(query):
    # Ensure the database is initialized before querying
    initialize_vector_db() 
    query_lower = query.lower()
    
    # Retrieve top 3 results for better coverage
    results = collection.query(query_texts=[query], n_results=3)
    
    if results["documents"] and results["documents"][0]:
        # Prioritize detailed content from subject-specific files (e.g., maths.txt) over syllabus.txt
        detailed_docs = []
        syllabus_docs = []
        for doc, doc_id in zip(results["documents"][0], results["ids"][0]):
            # Check if the document contains the main entity from the query
            # This is a heuristic to prefer more direct answers
            query_entities = [entity for entity in query_lower.split() if len(entity) > 3] # Consider longer words as key entities
            
            is_relevant_to_query = False
            if query_entities:
                for entity in query_entities:
                    if entity in doc.lower():
                        is_relevant_to_query = True
                        break
            else: # If no long words in query, consider all docs potentially relevant
                is_relevant_to_query = True


            if is_relevant_to_query:
                if doc_id.startswith("kb_syllabus.txt") or doc_id.startswith("syllabus_"):
                    syllabus_docs.append(doc)
                else: # This covers other kb_*.txt files (history.txt, physics.txt etc.)
                    detailed_docs.append(doc)
        
        # Prefer detailed content if available and relevant, especially for "explain" or general queries
        if detailed_docs:
            # Join multiple detailed docs for richer context, limit to 2-3 for manageability
            return " ".join(detailed_docs[:2])
        elif syllabus_docs:
            return " ".join(syllabus_docs[:2]) # Also join syllabus docs if they are the only ones found
        
        # Fallback to the first result if no prioritized match, or if the docs were not considered 'relevant_to_query' by the heuristic
        # If we reach here, it means detailed_docs and syllabus_docs were empty based on our filtering,
        # but results["documents"][0] might still have something that the LLM could use.
        return results["documents"][0][0] # Return the very first retrieved document as a last resort
    
    return "No relevant context found in the syllabus or knowledge base."