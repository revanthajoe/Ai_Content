"""
Amazon DynamoDB Client – Storage for DNA profiles, evolution lineage, and content history.
"""

from __future__ import annotations
import json
import os
from typing import Optional
from datetime import datetime, timezone


class DynamoClient:
    """
    Wrapper for Amazon DynamoDB operations.
    Stores evolution trees, DNA profiles, and fitness history.
    Falls back to in-memory storage when DynamoDB is not available.
    """

    TABLE_NAME = os.getenv("DYNAMO_TABLE", "ContentDNA")

    def __init__(self):
        self._client = None
        self._available = False
        self._memory_store: dict[str, dict] = {}
        self._init_client()

    def _init_client(self):
        """Initialize DynamoDB client if credentials are available."""
        try:
            import boto3
            self._client = boto3.resource(
                "dynamodb",
                region_name=os.getenv("AWS_REGION", "us-east-1"),
            )
            self._table = self._client.Table(self.TABLE_NAME)
            self._available = True
        except Exception:
            self._available = False

    @property
    def available(self) -> bool:
        return self._available

    # ── Store Operations ──────────────────────────────────────────────────────

    def store_evolution(self, evolution_id: str, data: dict) -> bool:
        """Store an evolution tree result."""
        item = {
            "PK": f"EVOLUTION#{evolution_id}",
            "SK": "TREE",
            "data": json.dumps(data, default=str),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "type": "evolution_tree",
        }
        return self._put_item(item)

    def store_dna(self, content_id: str, dna: dict) -> bool:
        """Store a DNA profile."""
        item = {
            "PK": f"DNA#{content_id}",
            "SK": "PROFILE",
            "data": json.dumps(dna, default=str),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "type": "dna_profile",
        }
        return self._put_item(item)

    def store_fitness(self, content_id: str, generation: int, fitness: dict) -> bool:
        """Store fitness scores for a generation."""
        item = {
            "PK": f"FITNESS#{content_id}",
            "SK": f"GEN#{generation:04d}",
            "data": json.dumps(fitness, default=str),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "type": "fitness_score",
        }
        return self._put_item(item)

    # ── Retrieve Operations ───────────────────────────────────────────────────

    def get_evolution(self, evolution_id: str) -> Optional[dict]:
        """Retrieve an evolution tree."""
        return self._get_item(f"EVOLUTION#{evolution_id}", "TREE")

    def get_dna(self, content_id: str) -> Optional[dict]:
        """Retrieve a DNA profile."""
        return self._get_item(f"DNA#{content_id}", "PROFILE")

    def get_fitness_history(self, content_id: str) -> list[dict]:
        """Retrieve all fitness scores for a content piece."""
        if self._available and self._client:
            try:
                response = self._table.query(
                    KeyConditionExpression="PK = :pk AND begins_with(SK, :sk)",
                    ExpressionAttributeValues={
                        ":pk": f"FITNESS#{content_id}",
                        ":sk": "GEN#",
                    },
                )
                return [
                    json.loads(item["data"]) for item in response.get("Items", [])
                ]
            except Exception:
                pass

        # Fallback: memory store
        results = []
        prefix = f"FITNESS#{content_id}"
        for key, item in self._memory_store.items():
            if key.startswith(prefix):
                results.append(json.loads(item["data"]))
        return results

    # ── Internal Helpers ──────────────────────────────────────────────────────

    def _put_item(self, item: dict) -> bool:
        """Put an item to DynamoDB or memory store."""
        if self._available and self._client:
            try:
                self._table.put_item(Item=item)
                return True
            except Exception as e:
                print(f"DynamoDB put failed: {e}")

        # Fallback: memory store
        key = f"{item['PK']}|{item['SK']}"
        self._memory_store[key] = item
        return True

    def _get_item(self, pk: str, sk: str) -> Optional[dict]:
        """Get an item from DynamoDB or memory store."""
        if self._available and self._client:
            try:
                response = self._table.get_item(Key={"PK": pk, "SK": sk})
                item = response.get("Item")
                if item:
                    return json.loads(item["data"])
            except Exception:
                pass

        # Fallback: memory store
        key = f"{pk}|{sk}"
        item = self._memory_store.get(key)
        if item:
            return json.loads(item["data"])
        return None
