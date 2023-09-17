from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.reservation.models import Discount, Reservation, Room, Account

class DiscountRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering new records in the Discount model.
    """
    updated_by = serializers.SlugRelatedField(queryset=Account.objects.all(), slug_field='id')


    class Meta:
        model = Discount
        fields = ['id', 'discount_code', 'discount_rate', 'discount', 'updated_by']
    
    def update(self, model_object, validated_data):
        return self.Meta.model.update_model(self, model_object=model_object, **validated_data)
    
    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation['updated_by'] = {'id': instance.updated_by.id, 'email':instance.updated_by.email, 'full_name':instance.updated_by.full_name}
        representation['created_at'] = instance.created_at
        representation['updated_at'] = instance.updated_at
        return representation
    



class ReservationRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering new records in the Reservation model.
    """
    id_room = serializers.SlugRelatedField(queryset=Room.objects.all(), slug_field='id')
    id_account = serializers.SlugRelatedField(queryset=Account.objects.all(), slug_field='id')
    id_discount = serializers.SlugRelatedField(queryset=Discount.objects.all(), slug_field='id', required=False)
    updated_by = serializers.SlugRelatedField(queryset=Account.objects.all(), slug_field='id')


    class Meta:
        model = Reservation
        fields = ['id', 'id_room', 'id_account', 'id_discount', 'guest', 'price', 'check_in', 'check_out', 'has_canceled', 'updated_by']

    def create(self, validated_data):
        return self.Meta.model.create_model(self, **validated_data)
    
    def update(self, model_object, validated_data):
        return self.Meta.model.update_model(self, model_object=model_object, **validated_data)
    
    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation['updated_by'] = {'id': instance.updated_by.id, 'email':instance.updated_by.email, 'full_name':instance.updated_by.full_name}
        representation['created_at'] = instance.created_at
        representation['updated_at'] = instance.updated_at
        return representation