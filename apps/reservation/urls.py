from rest_framework import routers

from .views import DiscountRegisterView, ReservationRegisterView

router = routers.DefaultRouter()
router.register('register/discount', DiscountRegisterView, basename='register_discount')
router.register('register/reservation', ReservationRegisterView, basename='register_reservation')

router.register

urlpatterns = router.urls