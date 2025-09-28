from openai import OpenAI
import os
from dotenv import load_dotenv



class OpenAIClient:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)


    def get_response(self, prompt):
        response = self.client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=2000
        )

        return response.choices[0].message.content.strip()
    

if __name__ == "__main__":
    client = OpenAIClient()
    response = client.get_response("What is 1+1?")
    print(response)