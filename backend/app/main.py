"""
Content DNA OS – FastAPI Application
Main entry point for the backend API.
Also serves as Lambda handler via Mangum.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Content DNA OS",
    description="Evolutionary AI Operating System for Digital Content",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow frontend dev server and API Gateway origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {
        "name": "Content DNA OS",
        "version": "1.0.0",
        "status": "alive",
        "description": "Evolutionary AI Operating System for Digital Content",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/health/aws")
def health_aws():
    """Check connectivity to all AWS services used by this app."""
    from .aws.bedrock_client import BedrockClient
    from .aws.dynamo_client import DynamoClient
    from .aws.titan_embeddings import TitanEmbeddingsClient

    bedrock = BedrockClient()
    dynamo = DynamoClient()
    titan = TitanEmbeddingsClient()

    # Quick live probe for Bedrock
    bedrock_live = False
    if bedrock.available:
        try:
            result = bedrock.generate_mutation("test", "hook_amplification", max_tokens=16)
            bedrock_live = result is not None
        except Exception:
            pass

    # Quick live probe for Titan
    titan_live = False
    if titan.available:
        try:
            emb = titan.get_embedding("health check")
            titan_live = emb is not None and len(emb) > 0
        except Exception:
            pass

    # Quick live probe for DynamoDB
    dynamo_live = False
    if dynamo.available:
        try:
            import boto3, os
            client = boto3.client("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
            resp = client.describe_table(TableName=dynamo.TABLE_NAME)
            dynamo_live = resp["Table"]["TableStatus"] == "ACTIVE"
        except Exception:
            pass

    all_ok = bedrock_live and dynamo_live and titan_live

    return {
        "status": "healthy" if all_ok else "degraded",
        "services": {
            "bedrock_nova": {"initialized": bedrock.available, "live": bedrock_live},
            "dynamodb": {"initialized": dynamo.available, "live": dynamo_live, "table": dynamo.TABLE_NAME},
            "titan_embeddings": {"initialized": titan.available, "live": titan_live},
        },
        "integration": {
            "mutation_engine": "bedrock" if bedrock_live else "rule-based fallback",
            "similarity_guard": "titan_embeddings" if titan_live else "sequence_matcher fallback",
            "persistence": "dynamodb" if dynamo_live else "in-memory fallback",
        },
    }
