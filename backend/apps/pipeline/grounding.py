def validate_context(result):
    facts = result.source_facts + result.extracted_facts
    kept = []
    demoted = []
    for claim in result.allowed_claims:
        if 0 <= claim.source_ref < len(facts):
            kept.append(claim.claim)
        else:
            demoted.append(claim.claim)
    guidance = result.generated_guidance
    if demoted:
        guidance = {
            **guidance,
            "caveated_claims": guidance.get("caveated_claims", []) + demoted,
        }
    if result.unknowns and not result.prohibited_assumptions:
        raise ValueError("unknowns present without prohibited_assumptions")
    return kept, demoted, guidance