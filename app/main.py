from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import io

from app.gemini_client import generate_qa_pairs

app = FastAPI(title="Academic PDF Q&A Service")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/qa", response_model=List[Dict[str, str]])
async def create_qa_pairs(file: UploadFile = File(...)):
    """
    Upload PDF to Gemini and generate Q&A pairs using Gemini's document understanding capabilities.
    
    Returns a list of question-answer pairs.
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Read the uploaded file into memory
        content = await file.read()
        file_obj = io.BytesIO(content)
        file_obj.name = file.filename  # Set the name for the file object
        
        # Generate Q&A pairs using Gemini's document understanding
        qa_pairs = await generate_qa_pairs(file_obj)
        
        return qa_pairs
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Academic PDF Q&A Service is running"}