"""Offline fixture tests for the LinkedIn Apify adapter.

These tests do not call Apify.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from utils.linkedin_apify_adapter import (  # noqa: E402
    LINKEDIN_ACTOR_ID,
    alias_linkedin_item,
    linkedin_run_input,
)

JOHNVC_ROW = {
    "text": "Shipping a new retrieval pipeline this week.",
    "authorName": "Alex Founder",
    "numLikes": 40,
    "numComments": 6,
    "postUrl": "https://www.linkedin.com/posts/alex-activity-1",
}


class LinkedInApifyAdapterTests(unittest.TestCase):
    def test_actor_id_is_the_live_linkedin_posts_actor(self) -> None:
        self.assertEqual(LINKEDIN_ACTOR_ID, "johnvc/linkedin-posts-api")
        self.assertNotIn("curious_coder", LINKEDIN_ACTOR_ID)

    def test_profile_url_uses_profile_urls(self) -> None:
        payload = linkedin_run_input("https://www.linkedin.com/in/alex")
        self.assertEqual(payload, {"profileUrls": ["https://www.linkedin.com/in/alex"]})

    def test_post_url_uses_post_urls(self) -> None:
        payload = linkedin_run_input(
            "https://www.linkedin.com/posts/alex-activity-123"
        )
        self.assertEqual(
            payload,
            {"postUrls": ["https://www.linkedin.com/posts/alex-activity-123"]},
        )

    def test_alias_keeps_formatter_field_names(self) -> None:
        aliased = alias_linkedin_item(JOHNVC_ROW)
        self.assertEqual(aliased["likesCount"], 40)
        self.assertEqual(aliased["commentsCount"], 6)
        self.assertEqual(aliased["author"], "Alex Founder")
        self.assertEqual(aliased["ownerFullName"], "Alex Founder")
        self.assertEqual(aliased["text"], "Shipping a new retrieval pipeline this week.")


if __name__ == "__main__":
    unittest.main()
