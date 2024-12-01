from typing import List
import openai
from ..core.config import settings

class OpenAIService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.conversation_history: List[dict] = []

    async def generate_chat_response(self, message: str, follow_up: str | None = None, image_url: str | None = None) -> str:
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