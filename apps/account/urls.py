from .views import AccountRetrieveViewSet, AccountUserRegisterView
from django.urls import path

urlpatterns = [
    path('profile/<str:pk>/', AccountRetrieveViewSet.as_view(), name='profile'),
    path('register_user/', AccountUserRegisterView.as_view(), name='register_user')
]