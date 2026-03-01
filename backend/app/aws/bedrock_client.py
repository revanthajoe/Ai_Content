"""
Amazon Bedrock Client – Integration with Claude 3 Sonnet via Amazon Bedrock.
Provides AI-powered mutation generation as an enhancement over rule-based mutations.
"""

from __future__ import annotations
import json
import os
from typing import Optional


class BedrockClient:
    """
    Wrapper for Amazon Bedrock Claude 3 Sonnet.
    Falls back gracefully when AWS credentials are not available.
    """

    MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

    def __init__(self):
        self._client = None
        self._available = False
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
        Generate a content mutation using Claude 3 via Bedrock.
        Returns None if Bedrock is not available.
        """
        if not self._available or not self._client:
            return None

        prompt = self._build_mutation_prompt(content, strategy, platform)

        try:
            response = self._client.invoke_model(
                modelId=self.MODEL_ID,
                contentType="application/json",
                accept="application/json",
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "temperature": 0.8,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                }),
            )
            result = json.loads(response["body"].read())
            return result["content"][0]["text"]
        except Exception as e:
            print(f"Bedrock mutation generation failed: {e}")
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
