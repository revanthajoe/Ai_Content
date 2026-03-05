"""
Amazon Titan Embeddings Client – Semantic similarity via Amazon Titan.
Used for enhanced similarity checking beyond SequenceMatcher.
"""

from __future__ import annotations
import json
import math
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TitanEmbeddingsClient:
    """
    Wrapper for Amazon Titan Embeddings.
    Provides vector-based semantic similarity when available.
    Falls back to None when AWS is not configured.
    """

    MODEL_ID = "amazon.titan-embed-text-v1"

    def __init__(self):
        self._client = None
        self._available = False
        self._init_client()

    def _init_client(self):
        """Initialize the Bedrock runtime client."""
        try:
            import boto3
            self._client = boto3.client(
                "bedrock-runtime",
                region_name=os.getenv("AWS_REGION", "us-east-1"),
            )
            self._available = True
        except Exception:
            self._available = False

    @property
    def available(self) -> bool:
        return self._available

    def get_embedding(self, text: str) -> Optional[list[float]]:
        """Get embedding vector for a text string."""
        if not self._available or not self._client:
            return None

        try:
            response = self._client.invoke_model(
                modelId=self.MODEL_ID,
                contentType="application/json",
                accept="application/json",
                body=json.dumps({"inputText": text[:8000]}),  # Titan limit
            )
            result = json.loads(response["body"].read())
            return result.get("embedding")
        except Exception as e:
            logger.error(f"Titan embedding failed: {e}")
            return None

    def compute_similarity(self, text_a: str, text_b: str) -> Optional[float]:
        """Compute cosine similarity between two texts using Titan embeddings."""
        emb_a = self.get_embedding(text_a)
        emb_b = self.get_embedding(text_b)

        if emb_a is None or emb_b is None:
            return None

        return self._cosine_similarity(emb_a, emb_b)

    @staticmethod
    def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec_a) != len(vec_b):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        magnitude_a = math.sqrt(sum(a * a for a in vec_a))
        magnitude_b = math.sqrt(sum(b * b for b in vec_b))

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return dot_product / (magnitude_a * magnitude_b)
