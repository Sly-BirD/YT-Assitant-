from groq import Groq

def summarize_text(text):
    try:
        # Limit the input text to avoid exceeding token limits
        if len(text) > 4000:
            text = text[:4000]  # Truncate to the first 4000 characters

        client = Groq()
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Summarize the following text in a concise manner:\n{text}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

def translate_to_english(text: str) -> str:
    try:
        if not text or not text.strip():
            return ""

        client = Groq()
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a professional translator. Always respond in natural, fluent English. Keep formatting and lists when possible."},
                {"role": "user", "content": f"Translate the following text to English. If it's already English, improve clarity and grammar while keeping meaning.\n\n{text}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"