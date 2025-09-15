# YouTube Assistant App

Fetch YouTube transcripts, get crisp summaries, and ask questions about any video, all in your browser with Streamlit. Non‑English video? No problem. We’ll summarize and (optionally) translate to English for you.

## What it does

- Fetches transcripts from YouTube videos
- Summarizes the content using Groq’s Llama 3.1 models
- Q&A on top of the transcript (answers in English by default)
- Optional “Translate summary to English” toggle

## Project Structure

```
youtube-assistant-app
├── app
│   ├── __init__.py
│   ├── main.py              # Streamlit UI
│   ├── utils
│   │   ├── __init__.py
│   │   ├── transcript.py    # YouTube transcript fetching
│   │   ├── summarizer.py    # Summarize + translate to English
│   │   └── qa.py            # Q&A (answers forced to English)
├── requirements.txt
└── README.md
```

## Setup

1) Clone the repo
```bash
git clone <repository-url>
cd youtube-assistant-app
```

2) Install dependencies
```bash
pip install -r requirements.txt
```

3) Add your Groq API key
- Create a `.env` file (or copy `env_template.txt` to `.env`)
- Add:
```env
GROQ_API_KEY=your_groq_api_key_here
```

## Run it

```bash
streamlit run app/main.py
```


## Tips

- If a video has no official transcript, we’ll try available alternatives.
- Summaries can be auto‑translated to English with the checkbox.
- Q&A always responds in English (and we auto‑translate if the model slips).

## Requirements

- Python 3.x
- Streamlit
- Groq API
- YouTube Transcript API
- python-dotenv (for .env loading)

## License

MIT — do what you like. Have fun! 🙌
