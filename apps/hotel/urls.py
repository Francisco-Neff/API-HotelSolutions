from django.urls import path, include

from rest_framework import routers

from .views import HotelRegisterView

router = routers.DefaultRouter()
router.register('register/hotel', HotelRegisterView, basename='register_hotel')

urlpatterns = router.urls