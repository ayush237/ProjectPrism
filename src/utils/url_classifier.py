import re
from enum import Enum
from urllib.parse import urlparse

class Platform(Enum):
    YOUTUBE = "YOUTUBE"
    INSTAGRAM = "INSTAGRAM"
    TWITTER = "TWITTER"
    LINKEDIN = "LINKEDIN"
    GITHUB = "GITHUB"
    BLOG = "BLOG"

class URLClassifier:
    """
    Utility class to classify URLs into supported platforms for specialized routing.
    """
    
    @staticmethod
    def classify(url: str) -> Platform:
        if not url:
            return Platform.BLOG
            
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # YouTube
            if domain in ["youtube.com", "www.youtube.com", "youtu.be"]:
                return Platform.YOUTUBE
                
            # Instagram
            if domain in ["instagram.com", "www.instagram.com"]:
                return Platform.INSTAGRAM
                
            # Twitter / X
            if domain in ["twitter.com", "www.twitter.com", "x.com", "www.x.com"]:
                return Platform.TWITTER
                
            # LinkedIn
            if domain in ["linkedin.com", "www.linkedin.com"]:
                return Platform.LINKEDIN
                
            # GitHub
            if domain in ["github.com", "www.github.com"]:
                return Platform.GITHUB
                
            # Default fallback for Medium, Hashnode, generic blogs
            return Platform.BLOG
            
        except Exception:
            return Platform.BLOG
