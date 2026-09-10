from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    CallOutcomeView,
    CallStateView,
    CallViewSet,
    TranscriptAppendView,
)

router = DefaultRouter()
router.register("calls", CallViewSet, basename="call")

urlpatterns = [
    *router.urls,
    path(
        "internal/calls/<uuid:call_id>/transcript-append",
        TranscriptAppendView.as_view(),
    ),
    path("internal/calls/<uuid:call_id>/state", CallStateView.as_view()),
    path("internal/calls/<uuid:call_id>/outcome", CallOutcomeView.as_view()),
]