from fastapi import APIRouter, UploadFile, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import os
import openai
import PyPDF2
from ...core.config import settings
# import docx

# Import database session if needed
from ...core.db.database import async_get_db

router = APIRouter(tags=["generate-api"])

# Configuration
UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global variable to store conversation history
conversation_history = []


def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from different file types.
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    try:
        if file_extension == ".pdf":
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                text = "\n".join([page.extract_text() for page in reader.pages])
                return text
        # elif file_extension in [".docx", ".doc"]:
        #     doc = docx.Document(file_path)
        #     return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        elif file_extension == ".txt":
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")


@router.post("/generate-api")
async def generate_api(
    specification: Optional[str] = Form(None),
    follow_up: Optional[str] = Form(None),
    file: Optional[UploadFile] = None,
    db: AsyncSession = Depends(async_get_db),  # Dependency if needed
) -> JSONResponse:
    global conversation_history

    # Handle file upload if present
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        specification = extract_text_from_file(file_path)

    # Validate input
    if not specification and not follow_up:
        raise HTTPException(status_code=400, detail="No API specification or follow-up provided")

    # Prepare OpenAI messages
    messages = [
        {
            "role": "system",
            "content": "You are an expert assistant who analyzes files or text to provide insights. Answer questions based on the contents of the file or prompt provided.",
        }
    ]

    # Add conversation history
    messages.extend(conversation_history)

    # Prepare user message
    if specification:
        current_message = {
            "role": "user",
            "content": f"""
            Generate a detailed API based on the following specification:
            Specification:
            {specification}
            Please provide:
            1. A comprehensive API design
            2. Sample endpoints
            3. Request/Response examples
            4. Any necessary data models or schemas.
            """,
        }
    else:
        current_message = {
            "role": "user",
            "content": f"Follow-up question based on previous content: {follow_up}",
        }

    messages.append(current_message)

    # Call OpenAI API
    openai.api_key = settings.OPENAI_API_KEY
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
        )
        generated_response = response.choices[0].message.content

        # Update conversation history
        conversation_history.append(current_message)
        conversation_history.append({"role": "assistant", "content": generated_response})

        # Limit history to last 10 exchanges
        conversation_history = conversation_history[-10:]

        return JSONResponse(content={"success": True, "response": generated_response})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API Error: {str(e)}")
