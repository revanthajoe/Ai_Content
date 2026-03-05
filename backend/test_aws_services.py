"""
AWS Services Health Check – Verify Bedrock, DynamoDB, and Titan Embeddings.
Run:  python -m test_aws_services   (from backend/)
"""

import os
import sys
import json

# ─── Colors for terminal output ──────────────────────────────────────────────
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


def banner(title: str):
    print(f"\n{CYAN}{'─'*60}")
    print(f"  {BOLD}{title}{RESET}")
    print(f"{CYAN}{'─'*60}{RESET}")


def ok(msg: str):
    print(f"  {GREEN}✅ {msg}{RESET}")


def fail(msg: str):
    print(f"  {RED}❌ {msg}{RESET}")


def warn(msg: str):
    print(f"  {YELLOW}⚠️  {msg}{RESET}")


def info(msg: str):
    print(f"  {CYAN}ℹ  {msg}{RESET}")


# ═════════════════════════════════════════════════════════════════════════════
# 1. AWS Credentials Check
# ═════════════════════════════════════════════════════════════════════════════
def check_aws_credentials() -> bool:
    banner("1. AWS Credentials & boto3")

    # Check boto3 is installed
    try:
        import boto3
        ok(f"boto3 installed (version {boto3.__version__})")
    except ImportError:
        fail("boto3 is NOT installed. Run: pip install boto3")
        return False

    # Check credentials
    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials is None:
            fail("No AWS credentials found.")
            info("Set AWS_ACCESS_KEY_ID & AWS_SECRET_ACCESS_KEY env vars,")
            info("or configure ~/.aws/credentials, or attach an IAM role.")
            return False

        creds = credentials.get_frozen_credentials()
        masked_key = creds.access_key[:4] + "****" + creds.access_key[-4:] if creds.access_key else "N/A"
        ok(f"Credentials found (Access Key: {masked_key})")

        region = session.region_name or os.getenv("AWS_REGION", "us-east-1")
        ok(f"Region: {region}")
        return True

    except Exception as e:
        fail(f"Credential check error: {e}")
        return False


# ═════════════════════════════════════════════════════════════════════════════
# 2. Amazon Bedrock (Claude 3 Sonnet)
# ═════════════════════════════════════════════════════════════════════════════
def check_bedrock() -> bool:
    banner("2. Amazon Bedrock (Amazon Nova Pro)")

    try:
        from app.aws.bedrock_client import BedrockClient
        client = BedrockClient()

        if not client.available:
            fail("BedrockClient initialized but reports NOT available.")
            info("Check IAM permissions: bedrock:InvokeModel")
            return False

        ok("BedrockClient initialized and available")

        # Send a tiny test request
        info("Sending test mutation request...")
        result = client.generate_mutation(
            content="The sun is bright today.",
            strategy="hook_amplification",
            platform="twitter",
            max_tokens=64,
        )

        if result:
            ok(f"Bedrock responded! (first 80 chars): {result[:80]}...")
            return True
        else:
            fail("Bedrock returned None – invoke_model may have failed.")
            info("Check CloudWatch logs and IAM policy for bedrock-runtime:InvokeModel.")
            return False

    except Exception as e:
        fail(f"Bedrock test failed: {e}")
        return False


# ═════════════════════════════════════════════════════════════════════════════
# 3. Amazon DynamoDB
# ═════════════════════════════════════════════════════════════════════════════
def check_dynamodb() -> bool:
    banner("3. Amazon DynamoDB")

    table_name = os.getenv("DYNAMO_TABLE", "content_dna_evolution")
    info(f"Table name: {table_name}")

    try:
        from app.aws.dynamo_client import DynamoClient
        client = DynamoClient()

        if not client.available:
            fail("DynamoClient initialized but reports NOT available.")
            info("Check IAM permissions: dynamodb:PutItem, GetItem, Query, etc.")
            return False

        ok("DynamoClient initialized and available")

        # Check if table actually exists and is reachable
        import boto3
        dynamo = boto3.client(
            "dynamodb",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )
        try:
            resp = dynamo.describe_table(TableName=table_name)
            status = resp["Table"]["TableStatus"]
            item_count = resp["Table"].get("ItemCount", "unknown")
            ok(f"Table '{table_name}' exists — Status: {status}, Items: ~{item_count}")
        except dynamo.exceptions.ResourceNotFoundException:
            fail(f"Table '{table_name}' does NOT exist in this region.")
            info("Create it with content_id (String) PK + generation (Number) SK.")
            return False

        # Write + Read test
        info("Running write/read round-trip test...")
        test_id = "__healthcheck_test__"
        success = client.store_dna(test_id, {"test": True, "source": "health_check"})
        if success:
            ok("Write (PutItem) succeeded")
        else:
            fail("Write (PutItem) failed")
            return False

        retrieved = client.get_dna(test_id)
        if retrieved:
            ok("Read (GetItem) succeeded")
        else:
            fail("Read (GetItem) failed")
            return False

        # Clean up test item
        try:
            resource = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
            table = resource.Table(table_name)
            table.delete_item(Key={"content_id": test_id, "generation": -1})
            ok("Cleanup: test item deleted")
        except Exception:
            warn("Cleanup: could not delete test item (non-critical)")

        return True

    except Exception as e:
        fail(f"DynamoDB test failed: {e}")
        return False


# ═════════════════════════════════════════════════════════════════════════════
# 4. Amazon Titan Embeddings
# ═════════════════════════════════════════════════════════════════════════════
def check_titan_embeddings() -> bool:
    banner("4. Amazon Titan Embeddings")

    try:
        from app.aws.titan_embeddings import TitanEmbeddingsClient
        client = TitanEmbeddingsClient()

        if not client.available:
            fail("TitanEmbeddingsClient initialized but reports NOT available.")
            info("Check IAM permissions: bedrock:InvokeModel for amazon.titan-embed-text-v1")
            return False

        ok("TitanEmbeddingsClient initialized and available")

        # Test single embedding
        info("Generating test embedding...")
        embedding = client.get_embedding("Hello world, this is a health check.")
        if embedding and isinstance(embedding, list) and len(embedding) > 0:
            ok(f"Embedding generated — dimension: {len(embedding)}")
        else:
            fail("Embedding returned None or empty.")
            return False

        # Test similarity computation
        info("Computing similarity between two sentences...")
        sim = client.compute_similarity(
            "The cat sat on the mat.",
            "A feline rested on the rug.",
        )
        if sim is not None:
            ok(f"Similarity score: {sim:.4f}  (expected ~0.7–0.95 for similar sentences)")
            return True
        else:
            fail("Similarity computation returned None.")
            return False

    except Exception as e:
        fail(f"Titan Embeddings test failed: {e}")
        return False


# ═════════════════════════════════════════════════════════════════════════════
# 5. Integration check — all services together
# ═════════════════════════════════════════════════════════════════════════════
def check_integration(bedrock_ok: bool, dynamo_ok: bool, titan_ok: bool):
    banner("5. Integration Summary")

    services = {
        "AWS Credentials & boto3": True,  # if we got here, creds were OK
        "Bedrock (Amazon Nova Pro)": bedrock_ok,
        "DynamoDB": dynamo_ok,
        "Titan Embeddings": titan_ok,
    }

    all_good = all(services.values())

    for name, status in services.items():
        if status:
            ok(name)
        else:
            fail(name)

    print()
    if all_good:
        print(f"  {GREEN}{BOLD}🎉 ALL AWS SERVICES ARE OPERATIONAL!{RESET}")
    else:
        failing = [n for n, s in services.items() if not s]
        print(f"  {RED}{BOLD}⚠️  SOME SERVICES ARE DOWN: {', '.join(failing)}{RESET}")
        info("The app will still work with fallbacks (in-memory/rule-based),")
        info("but AI-powered features require the failing services.")

    print()


# ═════════════════════════════════════════════════════════════════════════════
# Main
# ═════════════════════════════════════════════════════════════════════════════
def main():
    print(f"\n{BOLD}{'='*60}")
    print(f"  Content DNA OS — AWS Services Health Check")
    print(f"{'='*60}{RESET}")

    # Step 1: Credentials
    if not check_aws_credentials():
        fail("Cannot proceed without valid AWS credentials.")
        print(f"\n{RED}Aborting remaining checks.{RESET}\n")
        sys.exit(1)

    # Step 2-4: Individual services
    bedrock_ok = check_bedrock()
    dynamo_ok = check_dynamodb()
    titan_ok = check_titan_embeddings()

    # Step 5: Summary
    check_integration(bedrock_ok, dynamo_ok, titan_ok)

    # Exit code
    if all([bedrock_ok, dynamo_ok, titan_ok]):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
