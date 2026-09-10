from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health),
    path("api/v1/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.organizations.urls")),
    path("api/v1/", include("apps.telephony.urls")),
    path("api/v1/", include("apps.agents.urls")),
    path("api/v1/", include("apps.campaigns.urls")),
    path("api/v1/", include("apps.leads.urls")),
    path("api/v1/", include("apps.calls.urls")),
    path("api/v1/", include("apps.jobs.urls")),
    path("api/v1/webhooks/twilio/", include("apps.telephony.webhook_urls")),
]