from groq import Groq
from utils.summarizer import translate_to_english

def ask_question_about_text(text, question):
    try:
        # Limit the input text to avoid exceeding token limits
        if len(text) > 4000:
            text = text[:4000]  # Truncate to the first 4000 characters

        client = Groq()
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Answer in clear, fluent English."},
                {"role": "user", "content": f"Based on the following text, answer the question concisely. If the text or question is not in English, you may think in that language but respond in English.\n\nText: {text}\n\nQuestion: {question}"}
            ]
        )
        raw_answer = response.choices[0].message.content.strip()

        # Safety net: if the model still replied in another language, translate to English
        translated = translate_to_english(raw_answer)
        # If translator errored, fall back to raw answer
        return translated if translated and not translated.lower().startswith("error:") else raw_answer
    except Exception as e:
        return f"Error: {e}"



# import openai

