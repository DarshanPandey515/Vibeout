from django.test import TestCase

from rest_framework.test import APIClient


class TenantIsolationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        response = self.client.post(
            "/api/v1/auth/signup",
            {"email": "a@example.com", "password": "secret123", "org_name": "Org A"},
            format="json",
        )
        self.user_a, self.org_a = response.data["user_id"], response.data["organization_id"]
        self.token_a = response.data["token"]
        response = self.client.post(
            "/api/v1/auth/signup",
            {"email": "b@example.com", "password": "secret123", "org_name": "Org B"},
            format="json",
        )
        self.user_b, self.org_b = response.data["user_id"], response.data["organization_id"]
        self.token_b = response.data["token"]

    def _auth(self, token, org_id):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        self.client.defaults["HTTP_X_ORGANIZATION_ID"] = str(org_id)

    def test_user_cannot_see_other_org_data(self):
        self._auth(self.token_a, self.org_a)
        self.client.post(
            "/api/v1/agents/",
            {"name": "A Agent", "objective_template": "x", "system_prompt_template": "y"},
            format="json",
        )
        self._auth(self.token_b, self.org_b)
        response = self.client.get("/api/v1/agents/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)

    def test_foreign_org_header_rejected(self):
        self._auth(self.token_b, self.org_a)
        response = self.client.get("/api/v1/agents/")
        self.assertEqual(response.status_code, 403)

    def test_missing_org_header_rejected(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_b}")
        response = self.client.get("/api/v1/agents/")
        self.assertEqual(response.status_code, 403)

    def test_role_gated_endpoint_ok_for_owner(self):
        self._auth(self.token_a, self.org_a)
        response = self.client.get("/api/v1/telephony/twilio-accounts/")
        self.assertEqual(response.status_code, 200)