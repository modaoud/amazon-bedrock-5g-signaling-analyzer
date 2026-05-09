import json
import re
import boto3


def call_bedrock_converse(region, model_id, system_prompt, user_prompt):
    client = boto3.client("bedrock-runtime", region_name=region)
    response = client.converse(
        modelId=model_id,
        system=[{"text": system_prompt}],
        messages=[{"role": "user", "content": [{"text": user_prompt}]}],
        inferenceConfig={"temperature": 0.1, "maxTokens": 4096},
    )
    return response["output"]["message"]["content"][0]["text"]


def extract_json(text):
    """Parse JSON from model output, stripping markdown fences or preamble."""
    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", text.strip())
    cleaned = re.sub(r"\n?```\s*$", "", cleaned)
    brace = cleaned.find("{")
    if brace > 0:
        cleaned = cleaned[brace:]
    return json.loads(cleaned)
