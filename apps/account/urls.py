from .views import AccountRetrieveViewSet, AccountUserRegisterView, AccountStaffRegisterView
from django.urls import path, include

from rest_framework import routers

router = routers.DefaultRouter()
router.register('register_staff', AccountStaffRegisterView, basename='register_staff')

urlpatterns = [

    path('profile/<str:pk>/', AccountRetrieveViewSet.as_view(), name='profile'),
    path('register_user/', AccountUserRegisterView.as_view(), name='register_user')
]

urlpatterns += router.urls