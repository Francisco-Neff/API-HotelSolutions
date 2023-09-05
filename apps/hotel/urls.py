from django.urls import path, include

from rest_framework import routers

from .views import HotelRegisterView, HotelMediaRegisterView, RoomRegisterView, RoomMediaRegisterView, RoomExtraRegisterView, HotelPublicViewer, HotelPrivateViewer, RoomPublicViewer

router = routers.DefaultRouter()
router.register('register/hotel', HotelRegisterView, basename='register_hotel')
router.register('register/hotelmedia', HotelMediaRegisterView, basename='register_hotel_media')
router.register('register/room', RoomRegisterView, basename='register_room')
router.register('register/roommedia', RoomMediaRegisterView, basename='register_room_media')
router.register('register/roomextra', RoomExtraRegisterView, basename='register_room_media')
router.register('viewer/hotel', HotelPublicViewer, basename='viewer_hotel')
router.register('viewer/private/hotel', HotelPrivateViewer, basename='viewer_private_hotel')
router.register('viewer/room', RoomPublicViewer, basename='viewer_room')

router.register

urlpatterns = router.urls