from django.core.management.base import BaseCommand

from apps.accounts.models import Membership, User
from apps.agents.models import Agent
from apps.campaigns.models import Campaign
from apps.core.crypto import encrypt
from apps.leads.models import Lead, LeadContext
from apps.organizations.models import Organization
from apps.telephony.models import PhoneNumber, TwilioAccount


class Command(BaseCommand):
    help = "Create demo org, agent, and sample leads with pre-generated context."

    def handle(self, *args, **options):
        if User.objects.filter(email="demo@example.com").exists():
            self.stdout.write("Demo data already exists.")
            return
        organization = Organization.objects.create(name="Demo Org", slug="demo-org")
        user = User.objects.create_user(
            username="demo@example.com", email="demo@example.com", password="demo12345"
        )
        Membership.objects.create(organization=organization, user=user, role="owner")
        agent = Agent.objects.create(
            organization=organization,
            name="Demo Agent",
            objective_template="Explore AI automation opportunity",
            system_prompt_template=(
                "You are a sales agent calling on behalf of Acme. Be concise, "
                "friendly, and never invent facts not in the lead context."
            ),
            voice_config={"tts_voice": "aura-asteria-en", "language": "en-US"},
            guardrails={"max_call_duration_seconds": 600},
        )
        account = TwilioAccount.objects.create(
            organization=organization,
            twilio_account_sid="ACdemo",
            auth_token_encrypted=encrypt("demo"),
        )
        number = PhoneNumber.objects.create(
            organization=organization,
            twilio_account=account,
            phone_number="+14155550000",
            twilio_sid="PNdemo",
            friendly_name="Demo Number",
        )
        campaign = Campaign.objects.create(
            organization=organization,
            name="Demo Campaign",
            agent=agent,
            caller_number=number,
        )
        samples = [
            ("John Doe", "+14155551234", "Acme Corp", "John asked about pricing."),
            ("Jane Smith", "+14155555678", "Globex", "Interested in AI automation for support tickets."),
        ]
        for name, phone, company, note in samples:
            lead = Lead.objects.create(
                organization=organization,
                campaign=campaign,
                name=name,
                phone_number=phone,
                company=company,
                raw_fields={"name": name, "phone": phone, "company": company, "notes": note},
                status="needs_review",
            )
            LeadContext.objects.create(
                organization=organization,
                lead=lead,
                version=1,
                source_facts=[f"{name} works at {company}.", note],
                extracted_facts=[],
                generated_guidance={"suggestions": ["Mention the expressed interest."]},
                unknowns=["Budget", "Decision-making authority"],
                allowed_claims=[f"{name} previously asked about pricing." if "pricing" in note else f"{name} is interested in AI automation."],
                prohibited_assumptions=["Do not claim a demo was requested.", "Do not invent budget details."],
                opening_guidance=f"Introduce yourself and confirm you are speaking with {name} at {company}.",
                qualification_guidance="Ask about the current automation workflow and timeline.",
                agent_notes="",
            )
        self.stdout.write("Demo ready: demo@example.com / demo12345")