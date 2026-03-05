"""
Amazon Bedrock Client – Integration with Amazon Nova Pro via Amazon Bedrock.
Provides AI-powered mutation generation as an enhancement over rule-based mutations.
Uses Amazon Nova Pro (primary) and Nova Lite (fallback) — no marketplace subscription needed.
"""

from __future__ import annotations
import json
import logging
from typing import Optional

from app.aws.config import settings

logger = logging.getLogger(__name__)


class BedrockClient:
    """
    Wrapper for Amazon Bedrock foundation models.
    Uses Amazon Nova Pro for high-quality content mutations.
    Falls back to Nova Lite, then gracefully to None when unavailable.
    """

    PRIMARY_MODEL = settings.bedrock_primary_model
    FALLBACK_MODEL = settings.bedrock_fallback_model

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
                region_name=settings.aws_region,
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
        language: str = "english",
        max_tokens: int = 1024,
    ) -> Optional[str]:
        """
        Generate a content mutation using Amazon Nova via Bedrock.
        Tries Nova Pro first, falls back to Nova Lite.
        Returns None if Bedrock is not available.
        """
        if not self._available or not self._client:
            return None

        prompt = self._build_mutation_prompt(content, strategy, platform, language)

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
    def _build_mutation_prompt(content: str, strategy: str, platform: str, language: str = "english") -> str:
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
            "regional_adaptation": (
                "Adapt this content for Indian audiences. Use culturally relevant references, "
                "idioms, examples, and analogies that resonate with people in India. "
                "Replace Western-centric references with Indian equivalents. "
                "If the content discusses business, use Indian market examples. "
                "If it discusses culture, use references familiar to Indian readers. "
                "Make it feel like it was originally written for an Indian audience."
            ),
        }

        instruction = strategy_instructions.get(strategy, "Improve this content meaningfully.")

        language_instruction = ""
        if language and language != "english":
            language_instruction = (
                f"\n\nLANGUAGE: Write the output in {language}. "
                f"Use natural, fluent {language} — not robotic translation. "
                f"Preserve cultural nuances appropriate for {language}-speaking audiences."
            )

        return f"""You are a content evolution engine. Your job is to structurally transform content, not paraphrase it.

STRATEGY: {strategy}
PLATFORM: {platform}

INSTRUCTION: {instruction}{language_instruction}

ORIGINAL CONTENT:
{content}

RULES:
- Do NOT simply rephrase or paraphrase
- Make STRUCTURAL changes to the content
- The output must be meaningfully different from the input
- Maintain the core message but transform the delivery
- Output ONLY the transformed content, no explanations

EVOLVED CONTENT:"""

    def simulate_audience(self, content: str, platform: str = "general") -> Optional[dict]:
        """Simulate audience reactions across Indian demographic segments."""
        if not self._available or not self._client:
            return None

        prompt = f"""You are an audience simulation engine for the Indian digital content market.

Analyze this content and simulate how different audience segments would react.

CONTENT:
{content}

PLATFORM: {platform}

For EACH of these 5 audience segments, provide:
1. A reaction summary (1-2 sentences)
2. Predicted engagement score (0-100)
3. One sample comment they might leave
4. Whether they'd share it (yes/no)

SEGMENTS:
- Gen Z India (18-24, Instagram/YouTube natives, mix Hindi-English)
- Urban Professionals (25-40, LinkedIn power users, career-focused)
- Rural Digital India (new smartphone users, WhatsApp-first, regional language)
- College Students (competitive exam culture, meme-savvy, aspirational)
- Business Owners (SME/startup founders, ROI-focused, time-poor)

Respond in this exact JSON format:
{{
  "segments": [
    {{
      "name": "Gen Z India",
      "reaction": "...",
      "engagement_score": 75,
      "sample_comment": "...",
      "would_share": true,
      "emoji_reaction": "🔥"
    }}
  ],
  "overall_virality_score": 65,
  "best_platform": "instagram",
  "improvement_tip": "..."
}}

Output ONLY valid JSON, no markdown fences."""

        for model_id in [self._active_model, self.FALLBACK_MODEL]:
            result = self._invoke_nova(model_id, prompt, 1500)
            if result:
                try:
                    import json as _json
                    clean = result.strip()
                    if clean.startswith("```"):
                        clean = clean.split("\n", 1)[1].rsplit("```", 1)[0]
                    return _json.loads(clean)
                except Exception:
                    logger.warning(f"Audience sim JSON parse failed for {model_id}")
        return None
