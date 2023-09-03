import os

from django.utils.translation import gettext_lazy as _
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from apps.account.models import Account

# Create your models here.


class Hotel(models.Model):
    name = models.CharField(verbose_name=_('Hotel'), max_length=250, unique=True)
    address = models.CharField(verbose_name=_('Address'), max_length=250, unique=True)
    description = models.TextField(verbose_name=_('Description'), max_length=5000, null=True, unique=False, blank=True)
    stars = models.PositiveSmallIntegerField(verbose_name=_('Stars'), validators=[MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(Account, related_name='update_by_reference', null=True, blank=False, on_delete=models.SET_NULL)


    class Meta:
        verbose_name = _('Hotel')
        verbose_name_plural = _('Hotel')
    
    def __str__(self):
        return f'{self.id}-{self.name}'

    def update_model(self, model_object=None, **extra_fields):
        if model_object is None or not isinstance(model_object, Hotel):
            raise ValidationError(message=_('The object can`t be updated.'))
        
        for field, value in extra_fields.items():
            setattr(model_object, field, value)

        model_object.save()
        return model_object




class HotelMedia(models.Model):
    id_hotel = models.ForeignKey(Hotel, related_name='hotel_media_reference', null=False, unique=False, blank=False, on_delete=models.CASCADE)
    img = models.ImageField(upload_to='media_hotel/')


    class Meta:
        verbose_name = _('Hotel Media')
        verbose_name_plural = _('Hotel Media')
    
    def update_model(self, model_object=None, **extra_fields):
        if model_object is None or not isinstance(model_object, HotelMedia):
            raise ValidationError(message=_('The object can`t be updated.'))
        
        old_img_path = None
        if 'img' in extra_fields.keys():
            old_img_path = model_object.img.path
        
        for field, value in extra_fields.items():
            setattr(model_object, field, value)

        if old_img_path is not None:
            if os.path.exists(old_img_path):
                os.remove(old_img_path)

        model_object.save()
        return model_object
    
    def delete(self, using=None, keep_parents=False):
        self.img.delete()
        super().delete(using=using, keep_parents=keep_parents)




class Room(models.Model):

    class ChoicesStatusRoom(models.TextChoices):
        clean = _('Clean'), _('Clean')
        dirty = _('Dirty'), _('Dirty')
        cleaning = _('Cleaning'), _('Cleaning')
        busy = _('Busy'), _('Busy')
        available = _('Available'), _('Available')
        discontinued = _('Discontinued'), _('Discontinued')

    id_hotel = models.ForeignKey(Hotel, related_name='hotel_reference', on_delete=models.RESTRICT)
    name = models.CharField(verbose_name=_('Room name'), max_length=250, null=True, unique=False, blank=True)
    description = models.TextField(verbose_name=_('Description'), max_length=5000, null=True, unique=False, blank=True)
    number = models.PositiveSmallIntegerField(verbose_name=_('Number'), null=True, blank=True)
    room_status = models.CharField(verbose_name=_('Status of room'), max_length=15, null=False, unique=False, choices=ChoicesStatusRoom.choices, default=ChoicesStatusRoom.available)
    price = models.DecimalField(verbose_name=_('Price per night'), unique=False, max_digits=6, decimal_places=2, default=0)
    room_capacity = models.PositiveSmallIntegerField(verbose_name=_('Guest Capacity'), validators=[MinValueValidator(1), MaxValueValidator(10)], default=1)
    num_bed = models.PositiveSmallIntegerField(verbose_name=_('Number of Beds'), validators=[MinValueValidator(1), MaxValueValidator(12)], default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(Account, related_name='update_by_room_reference', null=True, blank=False, on_delete=models.SET_NULL)
   

    class Meta:
        verbose_name = _('Room')
        verbose_name_plural = _('Rooms')
        constraints = [models.UniqueConstraint(fields=['name', 'number', 'id_hotel'], name="unique_name_number_per_hotel")]
    
    def __str__(self):
        if self.name and self.number:
            return f'{self.id}-C{self.room_capacity}-B{self.num_bed}-{self.name}-{self.number}'
        elif self.name:
            return f'{self.id}-C{self.room_capacity}-B{self.num_bed}-{self.name}'
        elif self.number:
            return f'{self.id}-C{self.room_capacity}-B{self.num_bed}-{self.number}'
        else:
            return f'{self.id}-C{self.room_capacity}-B{self.num_bed}'
    
    def clean_fields(self, exclude=None):
        if self.name is None and self.number is None:
            raise ValidationError(message=_('You must add the "name" field or the "number" field.'))
        return super().clean_fields(exclude)

    def update_model(self, model_object=None, **extra_fields):
        if model_object is None or not isinstance(model_object, Room):
            raise ValidationError(message=_('The object can`t be updated.'))
        
        for field, value in extra_fields.items():
            setattr(model_object, field, value)

        model_object.save()
        return model_object
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def add_rooms(self, model_object=None, id_rooms=None):
        if model_object is None or id_rooms is None:
            raise ValidationError(message=_('The "id_rooms" field and records is necessary.'))
        if not isinstance(id_rooms, list):
            raise ValidationError(message=_('The "id_rooms" field needs to be a list.'))
        try:
            for id_room in id_rooms:
                if not isinstance(id_room, Room):
                    id_room = get_object_or_404(Room, pk=id_room)
                model_object.id_rooms.add(id_room.id)
        except Exception as e:
            raise ValidationError(message=e)

    


class RoomMedia(models.Model):
    id_rooms = models.ManyToManyField(Room, related_name='room_media_reference', blank=False)
    img = models.ImageField(upload_to='media_room/')


    class Meta:
        verbose_name = _('Room Media')
        verbose_name_plural = _('Rooms Media')

    def create_model(self, **extra_fields):
        if not 'id_rooms' in extra_fields.keys():
            raise ValidationError(message=_('Do you need send the "id_rooms" field.'))
        if not isinstance(extra_fields.get('id_rooms'), list):
            raise ValidationError(message=_('The "id_rooms" field needs to be a list.'))
        try:
            id_rooms = extra_fields.pop('id_rooms')
            model_object = RoomMedia(
                **extra_fields
            )
            model_object.save()
            Room.add_rooms(self, model_object=model_object, id_rooms=id_rooms)
            return model_object
        except Exception as e:
            raise ValidationError(message=e)

    def update_model(self, model_object=None, **extra_fields):
        if model_object is None or not isinstance(model_object, RoomMedia):
            raise ValidationError(message=_('The object can`t be updated.'))
        
        old_img_path = None
        if 'img' in extra_fields.keys():
            old_img_path = model_object.img.path
            setattr(model_object, 'img', extra_fields.get('img'))

        if 'id_rooms' in extra_fields.keys():
            Room.add_rooms(self, model_object=model_object, id_rooms=extra_fields.get('id_rooms'))
            
        if old_img_path is not None:
            if os.path.exists(old_img_path):
                os.remove(old_img_path)

        model_object.save()
        return model_object
    
    def delete_item_room(self, id_room):
        if id_room is None or not isinstance(id_room, Room):
            raise ValidationError(message=_('The object can`t be updated.'))
        
        try:
            self.id_rooms.remove(id_room)
        except:
            raise ValidationError(message=_('The object can`t delete room selected.'))
    
    def delete(self, using=None, keep_parents=False):
        self.img.delete()
        super().delete(using=using, keep_parents=keep_parents)




class RoomExtra(models.Model):
    id_rooms = models.ManyToManyField(Room, related_name='room_extra_reference', blank=False)
    has_internet = models.BooleanField(verbose_name=_('Room with internet'), default=False)
    has_tv = models.BooleanField(verbose_name=_('Room with TV'), default=False)  


    class Meta:
        verbose_name = _('Room Extra')
        verbose_name_plural = _('Rooms Extra')

    def create_or_update_model(self, **extra_fields):
        if 'id_rooms' in extra_fields.keys():
            booleans_value = extra_fields.copy()
            booleans_value.pop('id_rooms')
        else:
            booleans_value = extra_fields.copy()

        model_object = RoomExtra.objects.filter(**booleans_value)
        if model_object.exists():
            model_object = RoomExtra.update_model(self, model_object=model_object.first(), **extra_fields)
        else:
            model_object = RoomExtra.create_model(self, **extra_fields)
        return model_object

    def create_model(self, **extra_fields):
        if not 'id_rooms' in extra_fields.keys():
            raise ValidationError(message=_('Do you need send the "id_rooms" field.'))
        if not isinstance(extra_fields.get('id_rooms'), list):
            raise ValidationError(message=_('The "id_rooms" field needs to be a list.'))
        try:
            id_rooms = extra_fields.pop('id_rooms')
            model_object = RoomExtra(
                **extra_fields
            )
            model_object.save()
            Room.add_rooms(self, model_object=model_object, id_rooms=id_rooms)
            return model_object
        except Exception as e:
            raise ValidationError(message=e)

    def update_model(self, model_object=None, **extra_fields):
        if model_object is None or not isinstance(model_object, RoomExtra):
            raise ValidationError(message=_('The object can`t be updated.'))

        if 'id_rooms' in extra_fields.keys():
            Room.add_rooms(self, model_object=model_object, id_rooms=extra_fields.get('id_rooms'))
            
        model_object.save()
        return model_object

    def delete_item_room(self, id_room):
        if id_room is None or not isinstance(id_room, Room):
            raise ValidationError(message=_('The object can`t be updated.'))
        
        try:
            self.id_rooms.remove(id_room)
        except:
            raise ValidationError(message=_('The object can`t delete room selected.'))