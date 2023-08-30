from typing import Type
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError

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
            raise ValidationError(message=_('The object can´t be updated.'))
        
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
    number = models.PositiveSmallIntegerField(verbose_name=_('Number'))
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
        constraints = [models.UniqueConstraint(fields=['name', 'number', 'id_hotel'], name="unique_name_number_per_hotel") ]
    
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
            raise ValidationError(message=_('The object can´t be updated.'))
        
        for field, value in extra_fields.items():
            setattr(model_object, field, value)

        model_object.save()
        return model_object
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    


class RoomMedia(models.Model):
    id_rooms = models.ManyToManyField(Room, related_name='room_media_reference', blank=False)
    img = models.ImageField(upload_to='media_room/')


    class Meta:
        verbose_name = _('Room Media')
        verbose_name_plural = _('Rooms Media')




class RoomExtra(models.Model):
    id_rooms = models.ManyToManyField(Room, related_name='room_extra_reference', blank=False)
    has_internet = models.BooleanField(verbose_name=_('Room with internet'), default=False)
    has_tv = models.BooleanField(verbose_name=_('Room with TV'), default=False)


    class Meta:
        verbose_name = _('Room Extra')
        verbose_name_plural = _('Rooms Extra')