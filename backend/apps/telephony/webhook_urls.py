from django.urls import path

from .webhooks import StatusCallbackView, VoiceWebhookView

urlpatterns = [
    path("voice/<int:phone_number_id>", VoiceWebhookView.as_view()),
    path("status/<uuid:call_id>", StatusCallbackView.as_view()),
]