from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken

from .views import SignupView

urlpatterns = [
    path("auth/signup", SignupView.as_view(), name="signup"),
    path("auth/login", ObtainAuthToken.as_view(), name="login"),
]
