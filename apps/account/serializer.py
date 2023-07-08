from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from apps.account.models import Account

class AccountRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        exclude = ['password', 'is_staff', 'is_superuser', 'is_active']