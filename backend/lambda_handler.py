"""
AWS Lambda Handler for Content DNA OS.
Entry point for Lambda-based deployment.
"""

import json
from app.core.evolution_manager import EvolutionManager
from app.core.models import PlatformType, MutationStrategy

manager = EvolutionManager()


def handler(event, context):
    """AWS Lambda handler for Content DNA OS API."""
    try:
        path = event.get("path", "")
        method = event.get("httpMethod", "GET")
        body = json.loads(event.get("body", "{}")) if event.get("body") else {}

        # Route: POST /api/evolve
        if path == "/api/evolve" and method == "POST":
            return _handle_evolve(body)

        # Route: POST /api/evolve/lab
        if path == "/api/evolve/lab" and method == "POST":
            return _handle_evolve_lab(body)

        # Route: GET /api/strategies
        if path == "/api/strategies" and method == "GET":
            return _handle_strategies()

        # Route: GET /health
        if path in ("/health", "/"):
            return _response(200, {"status": "healthy", "service": "Content DNA OS"})

        return _response(404, {"error": "Not found"})

    except Exception as e:
        return _response(500, {"error": str(e)})


def _handle_evolve(body: dict) -> dict:
    """Handle single evolution request."""
    content = body.get("content", "")
    platform = PlatformType(body.get("platform", "general"))
    strategy = MutationStrategy(body["strategy"]) if body.get("strategy") else None

    result = manager.evolve_single(content, platform, strategy)
    return _response(200, result.model_dump())


def _handle_evolve_lab(body: dict) -> dict:
    """Handle multi-generation evolution request."""
    content = body.get("content", "")
    platform = PlatformType(body.get("platform", "general"))
    generations = body.get("generations", 3)
    strategies = (
        [MutationStrategy(s) for s in body["strategies"]]
        if body.get("strategies")
        else None
    )

    result = manager.evolve_lab(content, platform, generations, strategies)
    return _response(200, result.model_dump())


def _handle_strategies() -> dict:
    """Return available strategies."""
    strategies = [
        {"value": s.value, "name": s.name}
        for s in MutationStrategy
    ]
    return _response(200, strategies)


def _response(status_code: int, body: dict | list) -> dict:
    """Build API Gateway compatible response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
        "body": json.dumps(body, default=str),
    }
