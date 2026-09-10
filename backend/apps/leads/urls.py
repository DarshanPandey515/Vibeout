from django.urls import path

from .views import (
    CampaignLeadsUploadView,
    CampaignLeadsView,
    LeadContextApproveView,
    LeadContextEditView,
    LeadContextRegenerateView,
    LeadDetailView,
    LeadImportConfirmView,
    LeadImportStatusView,
)

urlpatterns = [
    path("campaigns/<uuid:campaign_id>/leads/upload", CampaignLeadsUploadView.as_view()),
    path("campaigns/<uuid:campaign_id>/leads", CampaignLeadsView.as_view()),
    path("leads/imports/<uuid:import_id>/confirm", LeadImportConfirmView.as_view()),
    path("leads/imports/<uuid:import_id>", LeadImportStatusView.as_view()),
    path("leads/<uuid:lead_id>", LeadDetailView.as_view()),
    path("leads/<uuid:lead_id>/context/regenerate", LeadContextRegenerateView.as_view()),
    path("leads/<uuid:lead_id>/context", LeadContextEditView.as_view()),
    path("leads/<uuid:lead_id>/context/approve", LeadContextApproveView.as_view()),
]