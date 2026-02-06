from groq import Groq, GroqError
from app.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)


def generate_response(messages):
    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            temperature=0.2
        )
        return response.choices[0].message.content

    except GroqError as e:
        return (
            "The AI model is temporarily unavailable. "
            "Please try again later."
        )
