import openai
import os
import base64
from openai import AsyncOpenAI
from dotenv import load_dotenv
from anthropic import AsyncAnthropic

load_dotenv()

class OpenAI():
    def __init__(self):
        load_dotenv()
        self.client = AsyncOpenAI()
        self.model = "gpt-4o"

    def prepare_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    async def get_response(self, system_message, user_message, image_path=None):
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        if image_path:
            messages[1] = {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_message},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{self.prepare_image(image_path)}",
                        }
                    }
                ]
            }
        
        response = await self.client.beta.chat.completions.parse(
            model=self.model,
            messages=messages,
            temperature=0,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content

class Anthropic:
    def __init__(self):
        load_dotenv()
        self.client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-3-5-sonnet-20241022"

    async def get_response(self, system_message, user_message, image_path=None):
        messages = []
        content = user_message

        if image_path:
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")
                content = [
                    {"type": "text", "text": user_message},
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": base64_image
                        }
                    }
                ]

        response = await self.client.messages.create(
            model=self.model,
            system=system_message,
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ],
            temperature=0,
            max_tokens=1024
        )
        return response.content[0].text