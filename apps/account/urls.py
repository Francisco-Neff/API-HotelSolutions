from .views import AccountRetrieveViewSet
from django.urls import path

urlpatterns = [
    path('profile/<str:pk>/', AccountRetrieveViewSet.as_view(), name='profile')
]