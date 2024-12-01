from typing import List
import openai
from ..core.config import settings
import os
import PyPDF2
from fastapi import UploadFile, HTTPException

class OpenAIService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.conversation_history: List[dict] = []
        
    async def extract_text_from_file(self, file: UploadFile) -> str:
        """
        Extract text from different file types.
        """
        file_extension = os.path.splitext(file.filename)[1].lower()
        try:
            if file_extension == ".pdf":
                pdf_reader = PyPDF2.PdfReader(file.file)
                text = "\n".join([page.extract_text() for page in pdf_reader.pages])
                return text
            # elif file_extension in [".docx", ".doc"]:
            #     doc = docx.Document(file_path)
            #     return "\n".join([paragraph.text for paragraph in doc.paragraphs])
            elif file_extension == ".txt":
                content = await file.read()
                return content.decode("utf-8")
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
    
    async def generate_chat_response(self, message: str, follow_up: str | None = None, image_url: str | None = None, file: UploadFile | None = None) -> str:
        messages = [
            {
                "role": "system",
                "content": "You are AI-powered tool that generates RESTful / GraphQL APIs based on text-based input specifications. Can Handle media files. You Automatically generate API documentation when RESTful/ GraphQL APIs are generated."
            }
        ]

        # Add conversation history
        messages.extend(self.conversation_history)
        if image_url:
        # Add current message
            current_message = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": follow_up if follow_up else message
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    }
                ]
            }
        elif file:
            current_message = {
                "role": "user",
                "content": follow_up if follow_up else message + "\n" + self.extract_text_from_file(file)
            }
        else:
            current_message = {
                "role": "user",
                "content": follow_up if follow_up else message
            }
        messages.append(current_message)

        try:
            response = openai.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS
            )
            generated_response = response.choices[0].message.content

            # Update conversation history
            self.conversation_history.append(current_message)
            self.conversation_history.append(
                {"role": "assistant", "content": generated_response}
            )

            # Limit conversation history
            self.conversation_history = self.conversation_history[-10:]

            return generated_response

        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")