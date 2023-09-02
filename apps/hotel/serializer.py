from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from apps.account.models import Account
from apps.hotel.models import Hotel, Room

class HotelRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering new records in the Hotel model.
    """
    updated_by = serializers.SlugRelatedField(queryset=Account.objects.all(), slug_field='id')
    class Meta:
        model = Hotel
        fields = ['id', 'name', 'address', 'description', 'stars', 'updated_by']

    def update(self, model_object, validated_data):
        return self.Meta.model.update_model(self, model_object=model_object, **validated_data)
    
    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation['updated_by'] = {'id': instance.updated_by.id, 'email':instance.updated_by.email, 'full_name':instance.updated_by.full_name}
        representation['created_at'] = instance.created_at
        representation['updated_at'] = instance.updated_at
        return representation