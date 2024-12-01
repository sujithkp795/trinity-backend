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
                "content": f"""
                You are an advanced AI specialized in API design and development. Your task is to create a fully functional and detailed API schema based on user-provided natural language input.
                You should differentiate between a request for an API design or casual conversation. If the talk is casual conversation, continue the casual conversation.
                If the conversation is about api generation, you should go with the api generation flow.
                To ensure a complete API design, you will need the following information:
                1. **API Type**: Ask the user about the type of api - REST/GraphQL they want to generate.
                2. **Specification/Overview**: {message}
                3. **Authentication Requirements**: Specify the authentication mechanism (e.g., JWT, OAuth2, etc.) or any roles like Admin, User, etc.
                4. **Endpoints**: List the primary actions you want the API to handle (e.g., creating a post, retrieving user details, etc.). For each action, please include:
                - HTTP Method (GET, POST, PUT, DELETE) or GraphQL query/mutation
                - Request Parameters (body, headers, query parameters)
                - Expected Response (success/failure and response body structure)
                5. **Data Models**: Describe the entities involved (e.g., User, Post, Comment, etc.), their properties, and their relationships (e.g., one-to-many, many-to-many).
                6. **File Handling**: Specify if your API needs to handle file uploads or downloads (e.g., images, documents). Include details on where files should be stored.
                7. **Error Handling**: Define how errors should be returned (e.g., HTTP status codes, error messages).
                8. **Rate Limiting/Throttling**: If applicable, define any rate limiting or throttling rules to protect the API from abuse.
                9. **Versioning**: Do you require versioning for your API? If so, describe the preferred method (e.g., `/v1/`, `/api/v2/`).
                10. **Documentation**: The API documentation should be in markdown format. Ensure all endpoints, request/response models, and examples are well-documented.
                The output should be a **complete API schema**, which includes:
                - A detailed list of endpoints
                - Request/response models
                - Proper documentation with clear examples
                - Authentication and authorization details
                - Error handling strategies
                - File handling specifications (if applicable)
                - Versioning strategy (if applicable)
                If any requirements are not provided, I will prompt you to clarify or provide additional details.
                The Documentation to start building after we get full requirements
                """,
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