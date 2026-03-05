"""
Amazon DynamoDB Client – Storage for DNA profiles, evolution lineage, and content history.
Table: content_dna_evolution (content_id: String PK, generation: Number SK)
"""

from __future__ import annotations
import json
import os
import logging
from typing import Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class DynamoClient:
    """
    Wrapper for Amazon DynamoDB operations.
    Stores evolution trees, DNA profiles, and fitness history.
    Falls back to in-memory storage when DynamoDB is not available.
    """

    TABLE_NAME = os.getenv("DYNAMO_TABLE", "content_dna_evolution")

    def __init__(self):
        self._client = None
        self._table = None
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
            logger.info(f"DynamoClient connected to table: {self.TABLE_NAME}")
        except Exception as e:
            logger.warning(f"DynamoClient init failed: {e}")
            self._available = False

    @property
    def available(self) -> bool:
        return self._available

    # ── Store Operations ──────────────────────────────────────────────────────

    def store_evolution(self, content_id: str, generation: int, data: dict) -> bool:
        """Store an evolution generation result."""
        item = {
            "content_id": content_id,
            "generation": generation,
            "record_type": "evolution",
            "data": json.dumps(data, default=str),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return self._put_item(item)

    def store_dna(self, content_id: str, dna: dict) -> bool:
        """Store a DNA profile (generation = -1 sentinel for DNA records)."""
        item = {
            "content_id": content_id,
            "generation": -1,
            "record_type": "dna_profile",
            "data": json.dumps(dna, default=str),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return self._put_item(item)

    def store_fitness(self, content_id: str, generation: int, fitness: dict) -> bool:
        """Store fitness scores for a generation (offset by 10000 to avoid collision)."""
        item = {
            "content_id": content_id,
            "generation": 10000 + generation,
            "record_type": "fitness_score",
            "data": json.dumps(fitness, default=str),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return self._put_item(item)

    def store_full_evolution(self, content_id: str, evolution_data: dict) -> bool:
        """Store the complete evolution tree as a single record (generation = -2)."""
        item = {
            "content_id": content_id,
            "generation": -2,
            "record_type": "evolution_tree",
            "data": json.dumps(evolution_data, default=str),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return self._put_item(item)

    # ── Retrieve Operations ───────────────────────────────────────────────────

    def get_evolution(self, content_id: str) -> Optional[dict]:
        """Retrieve the full evolution tree."""
        return self._get_item(content_id, -2)

    def get_dna(self, content_id: str) -> Optional[dict]:
        """Retrieve a DNA profile."""
        return self._get_item(content_id, -1)

    def get_generation(self, content_id: str, generation: int) -> Optional[dict]:
        """Retrieve a specific generation's data."""
        return self._get_item(content_id, generation)

    def get_fitness_history(self, content_id: str) -> list[dict]:
        """Retrieve all fitness scores for a content piece."""
        if self._available and self._table:
            try:
                from boto3.dynamodb.conditions import Key
                response = self._table.query(
                    KeyConditionExpression=Key("content_id").eq(content_id)
                    & Key("generation").between(10000, 10100),
                )
                return [
                    json.loads(item["data"]) for item in response.get("Items", [])
                ]
            except Exception as e:
                logger.error(f"DynamoDB query failed: {e}")

        # Fallback: memory store
        results = []
        for key, item in self._memory_store.items():
            if key.startswith(content_id) and item.get("record_type") == "fitness_score":
                results.append(json.loads(item["data"]))
        return results

    def list_evolutions(self, limit: int = 20) -> list[dict]:
        """List recent evolution trees (scan, limited use)."""
        if self._available and self._table:
            try:
                from boto3.dynamodb.conditions import Attr
                response = self._table.scan(
                    FilterExpression=Attr("record_type").eq("evolution_tree"),
                    Limit=limit,
                )
                results = []
                for item in response.get("Items", []):
                    results.append({
                        "content_id": item["content_id"],
                        "created_at": item.get("created_at", ""),
                        "data": json.loads(item["data"]),
                    })
                return results
            except Exception as e:
                logger.error(f"DynamoDB scan failed: {e}")

        # Fallback: memory store
        results = []
        for key, item in self._memory_store.items():
            if item.get("record_type") == "evolution_tree":
                results.append({
                    "content_id": item["content_id"],
                    "created_at": item.get("created_at", ""),
                    "data": json.loads(item["data"]),
                })
        return results[:limit]

    # ── Internal Helpers ──────────────────────────────────────────────────────

    def _put_item(self, item: dict) -> bool:
        """Put an item to DynamoDB or memory store."""
        if self._available and self._table:
            try:
                self._table.put_item(Item=item)
                return True
            except Exception as e:
                logger.error(f"DynamoDB put failed: {e}")

        # Fallback: memory store
        key = f"{item['content_id']}|{item['generation']}"
        self._memory_store[key] = item
        return True

    def _get_item(self, content_id: str, generation: int) -> Optional[dict]:
        """Get an item from DynamoDB or memory store."""
        if self._available and self._table:
            try:
                response = self._table.get_item(
                    Key={"content_id": content_id, "generation": generation}
                )
                item = response.get("Item")
                if item:
                    return json.loads(item["data"])
            except Exception as e:
                logger.error(f"DynamoDB get failed: {e}")

        # Fallback: memory store
        key = f"{content_id}|{generation}"
        item = self._memory_store.get(key)
        if item:
            return json.loads(item["data"])
        return None
