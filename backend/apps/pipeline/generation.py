import json

from django.conf import settings
from groq import BadRequestError, Groq
from pydantic import ValidationError

from .schemas import LeadContextGenerationResult

SYSTEM_PROMPT = (
    "You are a lead-intelligence pipeline. Transform raw lead source material into a "
    "structured, strictly grounded call context. Output ONLY valid JSON matching this schema:\n"
    '{"source_facts": ["verbatim facts present in the source"], '
    '"extracted_facts": ["structured facts you extracted from the source"], '
    '"generated_guidance": {"suggestions": ["how the agent should use the facts"]}, '
    '"unknowns": ["things NOT known from the source"], '
    '"allowed_claims": [{"claim": "a claim the agent can safely make", '
    '"source_ref": <index into source_facts+extracted_facts>}], '
    '"prohibited_assumptions": ["claims the agent must not invent"], '
    '"opening_guidance": "how to open the conversation", '
    '"qualification_guidance": "qualifying questions", '
    '"agent_notes": "extra notes for the agent"}\n'
    "Rules:\n"
    "- Every allowed_claims.claim must be traceable to its source_ref item. Never invent facts.\n"
    "- Every unknown must have a corresponding prohibited_assumption.\n"
    "- opening_guidance and qualification_guidance are instructions, not claims.\n"
    "- If a field has no content, use an empty string or empty list.\n"
    "- All list items must be plain strings, not objects.\n"
)

RETRY_INSTRUCTION = (
    "Return ONLY a single valid JSON object matching the schema. No prose, no empty response."
)


def _build_prompt(source_text, objective):
    return (
        f"Campaign objective: {objective or 'Not provided'}\n\n"
        f"Raw lead source material:\n{source_text}"
    )


def generate_context(source_text, objective):
    client = Groq(api_key=settings.GROQ_API_KEY)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": _build_prompt(source_text, objective)},
    ]
    last_error = None
    for _ in range(2):
        kwargs = {
            "model": settings.GROQ_LLM_MODEL,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 4096,
            "response_format": {"type": "json_object"},
        }
        if settings.GROQ_REASONING_EFFORT:
            kwargs["reasoning_effort"] = settings.GROQ_REASONING_EFFORT
        try:
            completion = client.chat.completions.create(**kwargs)
            content = completion.choices[0].message.content
            return LeadContextGenerationResult.model_validate(json.loads(content))
        except (BadRequestError, json.JSONDecodeError, ValidationError) as exc:
            last_error = exc
            messages = messages + [{"role": "user", "content": RETRY_INSTRUCTION}]
    raise last_error