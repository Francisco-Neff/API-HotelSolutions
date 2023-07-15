from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from rest_framework import serializers

from apps.account.models import Account

class AccountUserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer para registrar nuevas cuentas de tipo base en el modelo Account.
    """
    id = serializers.CharField(
        label=_("id"),
        read_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True,
        required=False
    )
    class Meta:
        model = Account
        exclude = ['is_staff','is_superuser','groups','user_permissions']
    
    def create(self,validated_data):
        account = Account.objects.create_user(**validated_data)
        return account

class AccountRetrieveSerializer(serializers.ModelSerializer):
    """
    Serializer para el visualizado de usuarios.
    """
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True,
        required=False
    )
    new_password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'new_password'},
        trim_whitespace=False,
        write_only=True,
        required=False
    )

    class Meta:
        model = Account
        exclude = ['is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions']
    
    def update(self, account, validated_data):
        if 'password' in validated_data.keys() or 'new_password' in validated_data.keys():
            self.validate_passwords(self, account, attrs=validated_data)
               
        user = Account.objects.update(account=account, **validated_data)
        return user
    
    def validate_passwords(self, account, attrs):
        if not 'password' in attrs.keys():
            raise ValidationError(message=_('Debe enviar la contraseña actual del usuario en el campo "password".'))
        if not 'new_password' in attrs.keys():
            raise ValidationError(message=_('Debe enviar la nueva contraseña del usuario en el campo "new_password".'))
        if not account.check_password(attrs['password']):
            raise ValidationError(message=_("La contraseña actual 'password' es incorrecta."))
        return True