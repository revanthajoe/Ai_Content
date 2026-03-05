"""
Central configuration – loads .env once and provides settings to all modules.
Import: from app.aws.config import settings
"""

from __future__ import annotations
import os
from pathlib import Path


def _load_dotenv():
    """Load .env file from backend/ directory into os.environ."""
    # Look for .env in backend/ (parent of app/)
    env_paths = [
        Path(__file__).resolve().parent.parent.parent / ".env",  # backend/.env
        Path.cwd() / ".env",
    ]
    for env_path in env_paths:
        if env_path.is_file():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, value = line.partition("=")
                    key, value = key.strip(), value.strip()
                    # Only set if not already in environment (env vars take precedence)
                    if key and key not in os.environ:
                        os.environ[key] = value
            return


# Load .env on first import
_load_dotenv()


class _Settings:
    """Read-only settings from environment variables."""

    @property
    def aws_access_key_id(self) -> str:
        return os.getenv("AWS_ACCESS_KEY_ID", "")

    @property
    def aws_secret_access_key(self) -> str:
        return os.getenv("AWS_SECRET_ACCESS_KEY", "")

    @property
    def aws_region(self) -> str:
        return os.getenv("AWS_REGION", "us-east-1")

    @property
    def dynamo_table(self) -> str:
        return os.getenv("DYNAMO_TABLE", "content_dna_evolution")

    @property
    def bedrock_primary_model(self) -> str:
        return os.getenv("BEDROCK_PRIMARY_MODEL", "us.amazon.nova-pro-v1:0")

    @property
    def bedrock_fallback_model(self) -> str:
        return os.getenv("BEDROCK_FALLBACK_MODEL", "us.amazon.nova-lite-v1:0")

    @property
    def titan_model(self) -> str:
        return os.getenv("TITAN_MODEL", "amazon.titan-embed-text-v1")

    @property
    def has_aws_credentials(self) -> bool:
        return bool(self.aws_access_key_id and self.aws_secret_access_key)


settings = _Settings()
