from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from apps.account.models import Account
from apps.hotel.models import Hotel, HotelMedia, Room, RoomMedia, RoomExtra

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




class HotelMediaRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering new records in the HotelMedia model.
    """
    id_hotel = serializers.SlugRelatedField(queryset=Hotel.objects.all(), slug_field='id')


    class Meta:
        model = HotelMedia
        fields = ['id', 'id_hotel', 'img']
    
    def update(self, model_object, validated_data):
        return self.Meta.model.update_model(self, model_object=model_object, **validated_data)

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation['id_hotel'] = {'id': instance.id_hotel.id, 'name': instance.id_hotel.name, 'address': instance.id_hotel.address, 'description': instance.id_hotel.description}
        return representation




class RoomDeleteItemSerializer(serializers.Serializer):
    """
    Serializer to delete items in your records uses the id_rooms fields.
    """
    id_room = serializers.CharField()




class RoomRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering new records in the Room model.
    """
    id_hotel = serializers.SlugRelatedField(queryset=Hotel.objects.all(), slug_field='id')
    updated_by = serializers.SlugRelatedField(queryset=Account.objects.all(), slug_field='id')


    class Meta:
        model = Room
        fields = ['id', 'id_hotel', 'name', 'description', 'number', 'room_status', 'price', 'room_capacity', 'num_bed', 'updated_by']
    
    def update(self, model_object, validated_data):
        return self.Meta.model.update_model(self, model_object=model_object, **validated_data)
    
    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation['id_hotel'] = {'id': instance.id_hotel.id, 'name': instance.id_hotel.name, 'address': instance.id_hotel.address, 'description': instance.id_hotel.description}
        representation['updated_by'] = {'id': instance.updated_by.id, 'email':instance.updated_by.email, 'full_name':instance.updated_by.full_name}
        representation['created_at'] = instance.created_at
        representation['updated_at'] = instance.updated_at
        return representation




class RoomMediaRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering new records in the RoomMedia model.
    """
    id_rooms = serializers.SlugRelatedField(queryset=Room.objects.all(), slug_field='id', many=True)


    class Meta:
        model = RoomMedia
        fields = ['id', 'id_rooms', 'img']
    
    def create(self, validated_data):
        return self.Meta.model.create_model(self, **validated_data)
    
    def update(self, model_object, validated_data):
        return self.Meta.model.update_model(self, model_object=model_object, **validated_data)
    
    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation['id_rooms'] = [{'id_room': element.id, 'id_hotel': element.id_hotel.id} for element in instance.id_rooms.all() ]
        return representation




class RoomExtraRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering new records in the RoomExtra model.
    """
    id_rooms = serializers.SlugRelatedField(queryset=Room.objects.all(), slug_field='id', many=True)


    class Meta:
        model = RoomExtra
        fields = ['id', 'id_rooms', 'has_internet', 'has_tv']
    
    def create(self, validated_data):
        return self.Meta.model.create_or_update_model(self, **validated_data)
    
    def update(self, model_object, validated_data):
        return self.Meta.model.create_or_update_model(self, **validated_data)
    
    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation['id_rooms'] = [{'id_room': element.id, 'id_hotel': element.id_hotel.id} for element in instance.id_rooms.all() ]
        return representation