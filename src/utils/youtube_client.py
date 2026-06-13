import logging
from utils.logger import get_logger
logger = get_logger(__name__)
import asyncio
import yt_dlp
from typing import Dict, Optional

try:
    from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
    YOUTUBE_API_AVAILABLE = True
except ImportError as e:
    logger.warning(f"youtube_transcript_api failed to import (likely pyexpat issue). Transcripts will be disabled. Error: {e}")
    YOUTUBE_API_AVAILABLE = False
    TranscriptsDisabled, NoTranscriptFound = Exception, Exception

class YouTubeClient:
    """
    Extracts metadata and transcripts from YouTube video/short URLs.
    """
    
    async def extract(self, url: str) -> Optional[str]:
        return await asyncio.to_thread(self._extract_sync, url)

    def _extract_sync(self, url: str) -> Optional[str]:
        logger.info(f"Extracting YouTube content for {url}")
        
        # 1. Get Metadata via yt-dlp
        import re
        is_channel = bool(re.search(r"(/@|/c/|/channel/|/user/)", url))
        
        metadata = {}
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        if is_channel:
            ydl_opts['playlistend'] = 1
            
        video_id = None
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info:
                    if 'entries' in info:
                        entries = list(info['entries'])
                        if entries:
                            first_entry = entries[0]
                            video_id = first_entry.get('id')
                            metadata['Title'] = first_entry.get('title')
                            metadata['Channel'] = info.get('uploader', info.get('title'))
                    else:
                        video_id = info.get('id')
                        metadata['Title'] = info.get('title')
                        metadata['View Count'] = info.get('view_count')
                        metadata['Like Count'] = info.get('like_count')
                        metadata['Channel'] = info.get('uploader')
        except Exception as e:
            logger.warning(f"Failed to fetch YouTube metadata: {e}")
            
        if not video_id:
            # Fallback to simple extraction if yt-dlp fails
            import re
            match = re.search(r"(?:v=|\/shorts\/|youtu\.be\/)([\w-]{11})", url)
            if match:
                video_id = match.group(1)
                
        if not video_id:
            logger.error("Could not extract YouTube video ID.", exc_info=True)
            return None
            
        # 2. Get Transcript
        transcript_text = ""
        if YOUTUBE_API_AVAILABLE:
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                transcript_text = " ".join([t['text'] for t in transcript_list])
            except (TranscriptsDisabled, NoTranscriptFound) as e:
                logger.warning(f"No transcript available for {url}: {e}")
                transcript_text = "[No transcript available]"
            except Exception as e:
                logger.warning(f"Error fetching transcript: {e}")
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
