from .views import AccountRetrieveViewSet, AccountUserRegisterView, AccountStaffRegisterView, AccountSuperUserRegisterView
from django.urls import path, include

from rest_framework import routers

router = routers.DefaultRouter()
router.register('register/staff', AccountStaffRegisterView, basename='register_staff')

urlpatterns = [
    path('profile/<str:pk>/', AccountRetrieveViewSet.as_view(), name='profile'),
    path('register/user/', AccountUserRegisterView.as_view(), name='register_user'),
    path('register/superuser/', AccountSuperUserRegisterView.as_view(), name='register_superuser')
]

urlpatterns += router.urls