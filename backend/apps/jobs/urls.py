from django.urls import path

from .registry import HANDLERS
from .views import SignedJobView

urlpatterns = [path(f"jobs/{job_type}", SignedJobView.as_view()) for job_type in HANDLERS]