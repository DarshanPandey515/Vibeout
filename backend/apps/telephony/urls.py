from rest_framework.routers import DefaultRouter

from .views import PhoneNumberViewSet, TwilioAccountViewSet

router = DefaultRouter()
router.register("telephony/twilio-accounts", TwilioAccountViewSet, basename="twilio-account")
router.register("telephony/phone-numbers", PhoneNumberViewSet, basename="phone-number")

urlpatterns = router.urls