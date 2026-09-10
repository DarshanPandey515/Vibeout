from pydantic import BaseModel, field_validator


def _to_text(value):
    if isinstance(value, dict):
        return "; ".join(f"{key}: {item}" for key, item in value.items())
    return str(value)


class SourceClaim(BaseModel):
    claim: str
    source_ref: int


class LeadContextGenerationResult(BaseModel):
    source_facts: list[str]
    extracted_facts: list[str]
    generated_guidance: dict
    unknowns: list[str]
    allowed_claims: list[SourceClaim]
    prohibited_assumptions: list[str]
    opening_guidance: str
    qualification_guidance: str
    agent_notes: str

    @field_validator(
        "source_facts",
        "extracted_facts",
        "unknowns",
        "prohibited_assumptions",
        mode="before",
    )
    @classmethod
    def _stringify(cls, value):
        if isinstance(value, str):
            return [value]
        return [_to_text(item) for item in value]

    @field_validator("allowed_claims", mode="before")
    @classmethod
    def _coerce_claims(cls, value):
        claims = []
        for item in value:
            if isinstance(item, str):
                claims.append({"claim": item, "source_ref": -1})
            else:
                claims.append(item)
        return claims

    @field_validator("generated_guidance", mode="before")
    @classmethod
    def _coerce_guidance(cls, value):
        if isinstance(value, str):
            return {"notes": value}
        if isinstance(value, list):
            return {"suggestions": [_to_text(item) for item in value]}
        return value