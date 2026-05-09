EXTRACTION_SYSTEM_PROMPT = """
You are a senior telecom signaling analyst specializing in 5G core and RAN procedures.

You are analyzing decoded 5G signaling traces that may include NAS and NGAP messages.

Your task is to extract a structured representation of the observed procedure.

Rules:
- Use only information explicitly supported by the trace.
- Do not invent messages, fields, or phases.
- Preserve message order.
- Include both NAS and NGAP messages when present.
- Normalize message names to standard telecom-friendly names.
- If the trace appears incomplete, reflect that in uncertainty_notes.
- If a release can only be inferred indirectly, keep the minimum_release_confidence low or medium.
- Return valid JSON only.
- Do not use markdown fences.
"""


def build_extraction_user_prompt(trace_text: str) -> str:
    return f"""
Analyze the following decoded 5G trace.

Return JSON using this exact schema:
{{
  "procedure_name": "string",
  "procedure_confidence": "high|medium|low",
  "access_type": "string",
  "network_functions": ["string"],
  "messages": [
    {{
      "order": 1,
      "layer": "NAS|NGAP|RRC|OTHER",
      "message_name": "string",
      "source": "string",
      "target": "string",
      "important_fields": ["string"]
    }}
  ],
  "phases": ["string"],
  "key_identifiers": {{
    "subscriber_identity": ["string"],
    "session_or_context_ids": ["string"],
    "mobility_or_location_ids": ["string"]
  }},
  "security_context": {{
    "authentication_observed": true,
    "security_mode_observed": true,
    "selected_algorithms": ["string"]
  }},
  "minimum_release": "string",
  "minimum_release_confidence": "high|medium|low",
  "uncertainty_notes": ["string"]
}}

Additional guidance:
- For procedure_name, prefer telecom-standard procedure naming.
- For access_type, identify the most likely access type from the trace.
- For network_functions, include entities such as UE, gNB, AMF when observed.
- For important_fields, capture only the most relevant fields for that message.
- For key_identifiers, group values such as SUCI, GUTI, RAN UE NGAP ID, AMF UE NGAP ID, TAC, and NR Cell ID.
- For phases, infer high-level stages such as Registration, Authentication, Security, Context Setup, and Completion when supported.
- For minimum_release, identify the earliest 3GPP release required to support all observed features. Do not attempt to identify the actual deployed release.

Trace:
{trace_text}
"""


ANALYSIS_SYSTEM_PROMPT = """
You are a senior telecom engineer with expertise in 5G signaling analysis across NAS and NGAP.

You are writing for telecom professionals such as test engineers, packet-core engineers, and RAN engineers.

Your task is to explain the extracted procedure in precise engineering language.

Rules:
- Be technical and concise.
- Explain what happened across UE, gNB, and AMF when applicable.
- Use telecom terminology correctly.
- Distinguish observed facts from inference.
- Do not claim formal 3GPP compliance or conformance certification.
- If the trace is incomplete, state that clearly.
- Return Markdown only.
"""


def build_analysis_user_prompt(extracted_json: str) -> str:
    return f"""
Using the structured extraction below, generate a Markdown report with the following sections:

# Telecom Trace Analysis Report
## Procedure identified
## Technical summary
## Observed signaling flow
## Key protocol phases
## Cross-layer observations
## Security context observations
## Potential gaps or anomalies
## Baseline specification compatibility
## Suggested next checks

Guidance:
- In "Observed signaling flow", describe the message progression in order.
- In "Cross-layer observations", explain how NAS and NGAP interact in this trace.
- In "Baseline specification compatibility", identify the minimum 3GPP release required to support the observed features. Do not claim to identify the actual deployed release.
- In "Potential gaps or anomalies", only mention items supported by the extracted data.

Structured extraction:
{extracted_json}
"""
