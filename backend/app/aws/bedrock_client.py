"""
Amazon Bedrock Client – Integration with Amazon Nova Pro via Amazon Bedrock.
Provides AI-powered mutation generation as an enhancement over rule-based mutations.
Uses Amazon Nova Pro (primary) and Nova Lite (fallback) — no marketplace subscription needed.
"""

from __future__ import annotations
import json
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class BedrockClient:
    """
    Wrapper for Amazon Bedrock foundation models.
    Uses Amazon Nova Pro for high-quality content mutations.
    Falls back to Nova Lite, then gracefully to None when unavailable.
    """

    PRIMARY_MODEL = "us.amazon.nova-pro-v1:0"
    FALLBACK_MODEL = "us.amazon.nova-lite-v1:0"

    def __init__(self):
        self._client = None
        self._available = False
        self._active_model = self.PRIMARY_MODEL
        self._init_client()

    def _init_client(self):
        """Initialize the Bedrock client if AWS credentials are available."""
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

    def generate_mutation(
        self,
        content: str,
        strategy: str,
        platform: str = "general",
        max_tokens: int = 1024,
    ) -> Optional[str]:
        """
        Generate a content mutation using Amazon Nova via Bedrock.
        Tries Nova Pro first, falls back to Nova Lite.
        Returns None if Bedrock is not available.
        """
        if not self._available or not self._client:
            return None

        prompt = self._build_mutation_prompt(content, strategy, platform)

        # Try primary model, then fallback
        for model_id in [self._active_model, self.FALLBACK_MODEL]:
            result = self._invoke_nova(model_id, prompt, max_tokens)
            if result:
                self._active_model = model_id
                return result

        return None

    def _invoke_nova(self, model_id: str, prompt: str, max_tokens: int) -> Optional[str]:
        """Invoke an Amazon Nova model."""
        try:
            response = self._client.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps({
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"text": prompt}],
                        }
                    ],
                    "inferenceConfig": {
                        "maxTokens": max_tokens,
                        "temperature": 0.8,
                        "topP": 0.9,
                    },
                }),
            )
            result = json.loads(response["body"].read())
            text = result["output"]["message"]["content"][0]["text"]
            return text
        except Exception as e:
            logger.error(f"Bedrock {model_id} failed: {e}")
            return None

    @staticmethod
    def _build_mutation_prompt(content: str, strategy: str, platform: str) -> str:
        """Build the prompt for mutation generation."""
        strategy_instructions = {
            "hook_amplification": (
                "Rewrite this content with a dramatically more powerful opening hook. "
                "The first sentence must grab attention immediately. "
                "Use bold, provocative, or curiosity-driven language."
            ),
            "angle_shift": (
                "Rewrite this content from a completely different angle or perspective. "
                "Challenge the original viewpoint. Consider a contrarian take, a different "
                "stakeholder's view, or an unexpected framing."
            ),
            "story_reframe": (
                "Restructure this content as a compelling narrative with a clear "
                "setup → conflict → resolution arc. Make it story-driven."
            ),
            "counterpoint_injection": (
                "Keep the core message but inject a strong counterpoint or devil's advocate "
                "position in the middle. Then resolve the tension with a stronger conclusion."
            ),
            "summary_distillation": (
                "Distill this content to its absolute essential insight. Remove all fluff. "
                "Keep only the most impactful points in a crisp, punchy format."
            ),
            "platform_formatting": (
                f"Reformat this content specifically for {platform}. "
                "Use appropriate line breaks, emoji anchors, short paragraphs, "
                "and platform-native formatting conventions."
            ),
        }

        instruction = strategy_instructions.get(strategy, "Improve this content meaningfully.")

        return f"""You are a content evolution engine. Your job is to structurally transform content, not paraphrase it.

STRATEGY: {strategy}
PLATFORM: {platform}

INSTRUCTION: {instruction}

ORIGINAL CONTENT:
{content}

RULES:
- Do NOT simply rephrase or paraphrase
- Make STRUCTURAL changes to the content
- The output must be meaningfully different from the input
- Maintain the core message but transform the delivery
- Output ONLY the transformed content, no explanations

EVOLVED CONTENT:"""
