from django.test import SimpleTestCase

from .grounding import validate_context
from .schemas import LeadContextGenerationResult, SourceClaim


def _result(allowed_claims, unknowns=("Budget",), prohibited=("Do not claim budget",)):
    return LeadContextGenerationResult(
        source_facts=["Acme sells widgets"],
        extracted_facts=[],
        generated_guidance={},
        unknowns=list(unknowns),
        prohibited_assumptions=list(prohibited),
        allowed_claims=allowed_claims,
        opening_guidance="",
        qualification_guidance="",
        agent_notes="",
    )


class GroundingTests(SimpleTestCase):
    def test_demotes_claim_with_invalid_source_ref(self):
        kept, demoted, guidance = validate_context(
            _result(
                [
                    SourceClaim(claim="Acme sells widgets", source_ref=0),
                    SourceClaim(claim="Acme is public", source_ref=5),
                ]
            )
        )
        self.assertEqual(kept, ["Acme sells widgets"])
        self.assertEqual(demoted, ["Acme is public"])
        self.assertIn("Acme is public", guidance["caveated_claims"])

    def test_keeps_all_traceable_claims(self):
        kept, demoted, _ = validate_context(
            _result([SourceClaim(claim="Acme sells widgets", source_ref=0)])
        )
        self.assertEqual(kept, ["Acme sells widgets"])
        self.assertEqual(demoted, [])

    def test_unknowns_without_prohibited_assumptions_rejected(self):
        with self.assertRaises(ValueError):
            validate_context(_result([], unknowns=["Budget"], prohibited=[]))