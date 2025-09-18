from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, VideoUnavailable, NoTranscriptFound
from youtube_transcript_api._api import TranscriptListFetcher, HTTPAdapter, Retry, Session



def get_video_transcript(video_id):
    print(f"Debug: Starting transcript fetch for video_id: {video_id}")
    
    if not video_id or len(video_id) != 11:
        return "Error: Invalid YouTube video ID format"

    try:
        # Build an HTTP client compatible with the library's expected types
        http_client = Session()
        http_client.mount('https://', HTTPAdapter(max_retries=Retry(total=5, backoff_factor=0.5)))

        # Use lower-level fetcher for maximum compatibility across versions
        # Many versions accept `None` for proxy_config
        fetcher = TranscriptListFetcher(http_client, None)
        transcript_list = fetcher.fetch(video_id)

        transcript_obj = None
        # Prefer manually created English transcript
        try:
            transcript_obj = transcript_list.find_manually_created_transcript(['en', 'en-US', 'en-GB'])
        except NoTranscriptFound:
            # Fall back to any English transcript (may be auto-generated)
            try:
                transcript_obj = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
            except NoTranscriptFound:
                # As a last resort, pick the first available transcript
                try:
                    transcript_obj = next(iter(transcript_list))
                except StopIteration:
                    raise NoTranscriptFound('No transcripts available')

        entries = transcript_obj.fetch()

        if not entries:
            return "Error: No transcript data received"

        # Support both dict-based entries and object entries (e.g., FetchedTranscriptSnippet)
        text_parts = []
        for entry in entries:
            text_value = None
            if isinstance(entry, dict):
                text_value = entry.get('text')
            else:
                text_value = getattr(entry, 'text', None)
            if text_value:
                text_parts.append(text_value)
        if not text_parts:
            return "Error: No text content found in transcript"
        
        full_text = " ".join(text_parts)
        print(f"Debug: Successfully fetched transcript with {len(full_text)} characters")
        return full_text
        
    except TranscriptsDisabled:
        return "Error: Transcripts are disabled for this video"
    except VideoUnavailable:
        return "Error: The video is unavailable"
    except NoTranscriptFound:
        return "Error: No transcript found for this video"
    except Exception as e:
        print(f"Debug: Exception in get_video_transcript: {type(e).__name__}: {str(e)}")
        return f"Error: Failed to fetch transcript - {type(e).__name__}: {str(e)}"