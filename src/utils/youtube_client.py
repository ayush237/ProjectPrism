import logging
import yt_dlp
from typing import Dict, Optional

try:
    from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
    YOUTUBE_API_AVAILABLE = True
except ImportError as e:
    logging.warning(f"youtube_transcript_api failed to import (likely pyexpat issue). Transcripts will be disabled. Error: {e}")
    YOUTUBE_API_AVAILABLE = False
    TranscriptsDisabled, NoTranscriptFound = Exception, Exception

class YouTubeClient:
    """
    Extracts metadata and transcripts from YouTube video/short URLs.
    """
    
    def extract(self, url: str) -> Optional[str]:
        logging.info(f"Extracting YouTube content for {url}")
        
        # 1. Get Metadata via yt-dlp
        metadata = {}
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        video_id = None
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info:
                    video_id = info.get('id')
                    metadata['Title'] = info.get('title')
                    metadata['View Count'] = info.get('view_count')
                    metadata['Like Count'] = info.get('like_count')
                    metadata['Channel'] = info.get('uploader')
        except Exception as e:
            logging.warning(f"Failed to fetch YouTube metadata: {e}")
            
        if not video_id:
            # Fallback to simple extraction if yt-dlp fails
            import re
            match = re.search(r"(?:v=|\/shorts\/|youtu\.be\/)([\w-]{11})", url)
            if match:
                video_id = match.group(1)
                
        if not video_id:
            logging.error("Could not extract YouTube video ID.")
            return None
            
        # 2. Get Transcript
        transcript_text = ""
        if YOUTUBE_API_AVAILABLE:
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                transcript_text = " ".join([t['text'] for t in transcript_list])
            except (TranscriptsDisabled, NoTranscriptFound) as e:
                logging.warning(f"No transcript available for {url}: {e}")
                transcript_text = "[No transcript available]"
            except Exception as e:
                logging.warning(f"Error fetching transcript: {e}")
                transcript_text = "[Error fetching transcript]"
        else:
            transcript_text = "[Transcripts disabled due to missing python dependency]"
            
        # Format the output
        output = "# YouTube Video Extraction\n\n"
        output += "## Metadata\n"
        for k, v in metadata.items():
            if v:
                output += f"- **{k}:** {v}\n"
                
        output += "\n## Transcript\n"
        output += transcript_text
        
        return output
