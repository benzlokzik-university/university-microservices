"""
Mocked Perspective API for content moderation in Rating service.
"""

import random
import asyncio
from typing import Dict, Tuple


class MockPerspectiveAPI:
    """Mocked Perspective API that simulates content moderation."""

    async def analyze_comment(self, comment_text: str) -> Tuple[bool, Dict[str, float]]:
        """
        Simulate comment analysis via Perspective API.

        Args:
            comment_text: Comment text to analyze

        Returns:
            Tuple of (is_toxic, scores_dict)
        """
        # Simulate network delay
        await asyncio.sleep(0.3)

        # Simple mock: check for some basic toxic words
        toxic_words = ["bad", "hate", "stupid", "terrible"]
        is_toxic = any(word in comment_text.lower() for word in toxic_words)

        # Generate random scores
        toxicity_score = (
            random.uniform(0.7, 0.95) if is_toxic else random.uniform(0.1, 0.4)
        )
        spam_score = random.uniform(0.1, 0.3)
        profanity_score = (
            random.uniform(0.0, 0.5) if is_toxic else random.uniform(0.0, 0.2)
        )

        scores = {
            "toxicity": toxicity_score,
            "spam": spam_score,
            "profanity": profanity_score,
        }

        # Comment is moderated if toxicity > 0.5
        is_moderated = toxicity_score > 0.5

        print(
            f"[Perspective API] Comment analyzed: toxicity={toxicity_score:.2f}, moderated={is_moderated}"
        )

        return is_moderated, scores


# Global instance
perspective_api = MockPerspectiveAPI()
