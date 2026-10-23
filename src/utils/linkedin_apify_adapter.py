"""Map LinkedIn Apify rows onto ProjectPrism's existing social-extractor names.

Offline-only helpers. Tests import this module and do not call Apify.
"""

from __future__ import annotations

from typing import Any, Dict
from urllib.parse import urlparse

LINKEDIN_ACTOR_ID = "johnvc/linkedin-posts-api"


def linkedin_run_input(url: str) -> Dict[str, Any]:
    """Send a post URL as postUrls, otherwise discover from the profile URL."""

    path = urlparse(url).path.lower()
    if "/posts/" in path or "/feed/update/" in path or "/activity-" in path:
        return {"postUrls": [url]}
    return {"profileUrls": [url]}


def alias_linkedin_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Copy johnvc names onto the keys _run_actor_and_format already reads."""

    aliased = dict(item)
    if "likesCount" not in aliased and aliased.get("numLikes") is not None:
        aliased["likesCount"] = aliased["numLikes"]
    if "commentsCount" not in aliased and aliased.get("numComments") is not None:
        aliased["commentsCount"] = aliased["numComments"]
    if "author" not in aliased and aliased.get("authorName"):
        aliased["author"] = aliased["authorName"]
    if "ownerFullName" not in aliased and aliased.get("authorName"):
        aliased["ownerFullName"] = aliased["authorName"]
    return aliased
