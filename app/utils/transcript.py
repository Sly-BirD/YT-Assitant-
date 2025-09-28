# Utilities for fetching YouTube transcripts.
# Proxy support
# The fetch logic will try proxies (shuffled) and fall back to direct requests.


from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, VideoUnavailable, NoTranscriptFound
from youtube_transcript_api._api import TranscriptListFetcher, HTTPAdapter, Retry, Session
import os
import random
from typing import List, Optional


def _parse_proxies_from_env() -> List[str]:
    """Read proxies from YT_PROXIES or YT_PROXY env var. Return list of proxy URLs.

    Expected formats:
    - single proxy: http://user:pass@host:port or http://host:port
    - multiple proxies (comma separated): http://p1, http://p2
    """
    env = os.environ.get('YT_PROXIES') or os.environ.get('YT_PROXY')
    if not env:
        return []
    # split on commas and strip whitespace
    parts = [p.strip() for p in env.split(',') if p.strip()]
    return parts


def _build_session_with_proxy(proxy: Optional[str] = None) -> Session:
    """Build a requests-like Session and mount adapter. If proxy provided, set session.proxies."""
    http_client = Session()
    http_client.mount('https://', HTTPAdapter(max_retries=Retry(total=5, backoff_factor=0.5)))
    if proxy:
        # The youtube_transcript_api uses requests-like session which supports session.proxies
        http_client.proxies = {
            'http': proxy,
            'https': proxy,
        }
    return http_client



def get_video_transcript(video_id: str, max_attempts: int = 5):
    """Fetch transcript for a YouTube video.

    If the environment variable `YT_PROXIES` or `YT_PROXY` is set (comma-separated list),
    the function will rotate through proxies on failures to avoid IP-based blocking.

    Returns the transcript text on success, or an "Error: ..." string on failure.
    """
    print(f"Debug: Starting transcript fetch for video_id: {video_id}")

    if not video_id or len(video_id) != 11:
        return "Error: Invalid YouTube video ID format"

    proxies = _parse_proxies_from_env()
    # shuffle proxies to spread load
    if proxies:
        random.shuffle(proxies)

    last_error = None
    # try with proxies first (if any), then fallback to direct request
    attempt = 0
    tried_proxies = []
    # Build a sequence of proxy candidates: proxies list followed by None (direct)
    candidates = proxies + [None]

    for candidate in candidates:
        # For each candidate, try up to max_attempts_per_proxy attempts
        for a in range(max_attempts):
            attempt += 1
            try:
                print(f"Debug: Attempt {attempt} using proxy={candidate}")
                http_client = _build_session_with_proxy(candidate)

                # Use lower-level fetcher for maximum compatibility
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
                print(f"Debug: Successfully fetched transcript with {len(full_text)} characters using proxy={candidate}")
                return full_text

            except TranscriptsDisabled:
                return "Error: Transcripts are disabled for this video"
            except VideoUnavailable:
                return "Error: The video is unavailable"
            except NoTranscriptFound:
                return "Error: No transcript found for this video"
            except Exception as e:
                last_error = e
                err_name = type(e).__name__
                print(f"Debug: Attempt {attempt} failed with {err_name}: {str(e)} (proxy={candidate})")
                # If RequestBlocked or similar, try next proxy candidate
                tried_proxies.append(candidate)
                # small backoff before retrying same proxy
                # Note: avoid import of time at top if not needed elsewhere
                try:
                    import time
                    time.sleep(0.5 * (a + 1))
                except Exception:
                    pass
                continue

    # All attempts exhausted
    if last_error:
        print(f"Debug: All attempts failed. Last error: {type(last_error).__name__}: {str(last_error)}")
        return f"Error: Failed to fetch transcript - {type(last_error).__name__}: {str(last_error)}"
    else:
        return "Error: Failed to fetch transcript - unknown error"
