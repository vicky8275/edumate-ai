# summary_agent.py
import os
import tempfile
import streamlit as st
from typing import Optional
import ollama # Changed from google.generativeai
import requests # Needed for Ollama error handling
from PyPDF2 import PdfReader
from docx import Document
import io

class SummarizerAgent:
    def __init__(self):
        """Initialize the Summarizer Agent with Ollama."""
        # No API key check here as it uses local Ollama server
        self.model_name = "phi3" # Specify Ollama model name
    
    def extract_text_from_pdf(self, file) -> str:
        """Extract text from PDF file."""
        try:
            pdf_reader = PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def extract_text_from_docx(self, file) -> str:
        """Extract text from DOCX file."""
        try:
            doc = Document(file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")
    
    def extract_text_from_file(self, uploaded_file) -> str:
        """Extract text from uploaded file based on file type."""
        file_type = uploaded_file.type
        
        # Check file size (10MB limit)
        if uploaded_file.size > 10 * 1024 * 1024:
            raise Exception("File size exceeds 10MB limit")
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_file_path = tmp_file.name
        
        try:
            if file_type == "application/pdf":
                with open(tmp_file_path, 'rb') as file:
                    text = self.extract_text_from_pdf(file)
            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                text = self.extract_text_from_docx(tmp_file_path)
            else:
                raise Exception(f"Unsupported file type: {file_type}")
            
            if not text.strip():
                raise Exception("No text content found in the document")
            
            return text
        
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
    
    def create_summary_prompt(self, text: str, summary_length: str, focus_area: str) -> str:
        """Create a detailed prompt for Ollama based on user preferences."""
        
        # Map summary length to number of points
        length_mapping = {
            "Brief (3-5 key points)": "3-5",
            "Detailed (7-10 key points)": "7-10",
            "Comprehensive (10+ key points)": "10-15"
        }
        
        num_points = length_mapping.get(summary_length, "5-7")
        
        # Create focus-specific instructions
        focus_instructions = {
            "General Overview": "Provide a balanced overview covering all major topics and themes.",
            "Main Arguments": "Focus on the primary arguments, claims, and supporting evidence presented.",
            "Key Concepts": "Emphasize important concepts, definitions, and theoretical frameworks.",
            "Important Facts": "Highlight crucial facts, statistics, and data points.",
            "Conclusions": "Focus on conclusions, findings, and final recommendations."
        }
        
        focus_instruction = focus_instructions.get(focus_area, focus_instructions["General Overview"])
        
        prompt = f"""
        You are an expert academic summarizer helping a student understand complex documents. 
        
        Please analyze the following document and create a comprehensive summary with these specifications:
        
        **Summary Requirements:**
        - Generate {num_points} key points in bullet format
        - {focus_instruction}
        - Each bullet point should be clear, concise, and informative
        - Use academic language appropriate for students
        - Maintain the original meaning and context
        - Organize points from most important to least important
        
        **Formatting Guidelines:**
        - Use bullet points (`-`) for each key point.
        - Each point should be 1-2 sentences long.
        - Include relevant examples or details where appropriate.
        - Use clear, readable formatting.
        
        **Document to Summarize:**
        {text}
        
        Please provide the summary now:
        """
        
        return prompt
    
    def generate_summary_with_ollama(self, prompt: str) -> str:
        """Generate summary using Ollama API."""
        try:
            # Use ollama.generate for local LLM
            # Note: For very large texts, consider chunking or increasing num_predict significantly.
            # Phi3 might struggle with very long input texts for summarization.
            response = ollama.generate(model=self.model_name, prompt=prompt, options={"temperature": 0.5, "num_predict": 2000})
            
            if not response['response']:
                raise Exception("Empty response from Ollama")
            
            return response['response'].strip()
        
        except requests.exceptions.ConnectionError:
            raise Exception("Ollama server not running. Please ensure Ollama is running and the 'phi3' model is pulled.")
        except Exception as e:
            raise Exception(f"Error generating summary: {str(e)}")
    
    def summarize_document(self, uploaded_file, summary_length: str, focus_area: str) -> str:
        """Main method to summarize uploaded document."""
        try:
            # Step 1: Extract text from document
            st.info("📄 Extracting text from document...")
            text = self.extract_text_from_file(uploaded_file)
            
            # Check if text is too short for meaningful summary (Phi3 might be sensitive)
            if len(text.split()) < 100: # Increased minimum word count for better results
                raise Exception("Document too short to generate meaningful summary (minimum 100 words required)")
            
            # Step 2: Create summary prompt
            st.info("🤖 Preparing summary request...")
            prompt = self.create_summary_prompt(text, summary_length, focus_area)
            
            # Step 3: Generate summary using Ollama
            st.info("✨ Generating intelligent summary...")
            summary = self.generate_summary_with_ollama(prompt)
            
            # Step 4: Format summary
            formatted_summary = self.format_summary(summary, uploaded_file.name)
            
            return formatted_summary
        
        except Exception as e:
            raise Exception(f"Summarization failed: {str(e)}")
    
    def format_summary(self, summary: str, filename: str) -> str:
        """Format the summary with header and metadata."""
        formatted = f"""
### 📋 Document Summary

**Source:** {filename}  
**Generated:** {st.session_state.get('current_time', 'Now')}

### Key Points:

{summary}

---
*Generated by EduMate AI Assistant*
        """
        return formatted.strip()
