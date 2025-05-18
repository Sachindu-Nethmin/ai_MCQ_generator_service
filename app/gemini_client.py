import google.generativeai as genai
import json
import os
from typing import List, Dict, BinaryIO, Any
import httpx
from dotenv import load_dotenv

load_dotenv()

# Initialize the Gemini API (you'll need to set GOOGLE_API_KEY in environment variables)
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("Missing GOOGLE_API_KEY environment variable")

# Configure the Gemini client
genai.configure(api_key=API_KEY)

async def generate_qa_pairs(pdf_file: BinaryIO) -> List[Dict[str, str]]:
    """
    Generate MCQ from academic PDF using Gemini's document understanding.
    
    Args:
        pdf_file: The uploaded PDF file as a file-like object
        
    Returns:
        List[Dict[str, str]]: A list of question-answer pairs
    """
    try:
        # Read the file content
        pdf_content = pdf_file.read()
        
        # Create prompt for generating Q&A pairs
        prompt = """
        Analyze this academic PDF document and generate a comprehensive list of important 
        MCQ questions and answers based on its content.
        
        Focus on key concepts, methodologies, findings, and conclusions from the document.
        
        Format your response as a JSON array with each object containing 'question' and 'answer' fields, like:
        [
            {"question": "What is the main research question?
                            A)option1
                            B)option2
                            C)option3
                            D)option4", "answer": "B"},
            {"question": "What methodology was used?
                            A)option1
                            B)option2
                            C)option3
                            D)option4", "answer": "C"},
            ...
        ]
        
        Generate at least 10 meaningful MCQ that cover the most important aspects of the document.
        Try generate MCQ for as much as possible.
        Don't use knowledge other than the document.
        Create proper spaces between the questions and answers.
        If possible make answers little bit descriptive.
        """
        
        # Make the API call with the PDF content and prompt
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create content parts for the request
        response = model.generate_content([
            {
                "mime_type": "application/pdf",
                "data": pdf_content
            },
            prompt
        ])
        
        # Process the response
        response_text = response.text
        
        # Extract JSON array from response
        qa_pairs = []
        
        # Find JSON in the response (it might be wrapped in markdown code blocks)
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        else:
            # Try to find any JSON array
            json_start = response_text.find("[")
            json_end = response_text.rfind("]") + 1
            if json_start != -1 and json_end != 0:
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
        
        # Parse the JSON
        try:
            parsed_data = json.loads(json_text)
            
            # Validate the parsed data
            if isinstance(parsed_data, list):
                for item in parsed_data:
                    if isinstance(item, dict) and "question" in item and "answer" in item:
                        qa_pairs.append({"question": item["question"], "answer": item["answer"]})
            
            return qa_pairs
            
        except json.JSONDecodeError:
            # Handle case where JSON parsing fails
            return [{"question": "Error parsing response", 
                    "answer": "The model did not return a valid JSON format. Raw response: " + response_text[:500] + "..."}]
            
    except Exception as e:
        return [{"question": "Error processing document", 
                "answer": f"An error occurred while processing the document: {str(e)}"}]