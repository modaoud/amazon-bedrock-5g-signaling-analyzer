import json
import sys
from pathlib import Path

import botocore.exceptions

from prompts import (
    EXTRACTION_SYSTEM_PROMPT,
    ANALYSIS_SYSTEM_PROMPT,
    build_extraction_user_prompt,
    build_analysis_user_prompt,
)
from bedrock_utils import call_bedrock_converse, extract_json

# Update to your preferred Region where the model is available
REGION = "us-east-1"

# Cross-region inference profile ID. Check Amazon Bedrock documentation
# for supported models and current inference profile IDs in your Region.
MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

INPUT_FILE = "input/sample_5g_registration_trace.txt"


def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else INPUT_FILE
    trace_text = Path(input_file).read_text()
    Path("output").mkdir(exist_ok=True)

    stem = Path(input_file).stem
    output_json = f"output/{stem}_extracted.json"
    output_md = f"output/{stem}_analysis.md"

    print(f"Using model: {MODEL_ID}")
    print(f"Reading trace: {input_file}")

    print("Step 1: Extracting structured telecom data...")
    try:
        extracted_text = call_bedrock_converse(
            REGION, MODEL_ID, EXTRACTION_SYSTEM_PROMPT,
            build_extraction_user_prompt(trace_text),
        )
    except botocore.exceptions.ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "AccessDeniedException":
            print("Access denied. Verify IAM permissions for bedrock:InvokeModel.")
        elif error_code == "ThrottlingException":
            print("Request throttled. Wait and retry, or request a quota increase.")
        elif error_code == "ResourceNotFoundException":
            print("Model not found. Verify the model ID and Region.")
        else:
            print(f"Bedrock call failed ({error_code}): {e}")
        sys.exit(1)

    try:
        extracted_obj = extract_json(extracted_text)
    except json.JSONDecodeError as e:
        print(f"Failed to parse extraction JSON: {e}")
        print(f"Raw output:\n{extracted_text[:500]}")
        sys.exit(1)

    extracted_pretty = json.dumps(extracted_obj, indent=2)
    Path(output_json).write_text(extracted_pretty)
    print(f"  -> Saved: {output_json}")

    print("Step 2: Generating analysis report...")
    try:
        analysis_text = call_bedrock_converse(
            REGION, MODEL_ID, ANALYSIS_SYSTEM_PROMPT,
            build_analysis_user_prompt(extracted_pretty),
        )
    except botocore.exceptions.ClientError as e:
        error_code = e.response["Error"]["Code"]
        print(f"Bedrock analysis call failed ({error_code}): {e}")
        sys.exit(1)

    Path(output_md).write_text(analysis_text)
    print(f"  -> Saved: {output_md}")
    print("Done.")


if __name__ == "__main__":
    main()
