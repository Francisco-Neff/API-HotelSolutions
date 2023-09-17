from datetime import datetime

from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models

from apps.account.models import Account
from apps.hotel.models import Room


class Discount(models.Model):
    discount_code = models.CharField(verbose_name=_('Code Discount'), max_length=100, unique=True, blank=False)
    discount_rate = models.DecimalField(verbose_name=_('Discount rate %'), validators=[MaxValueValidator(100)], max_digits=5, decimal_places=2, default=0)
    discount = models.DecimalField(verbose_name=_('Mark down amount'), unique=False, max_digits=9, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(Account, related_name='update_by_discount_reference', null=True, blank=False, on_delete=models.SET_NULL)


    class Meta:
        verbose_name = _('Discount')
        verbose_name_plural = _('Discounts')

    def __str__(self):
        return f'{self.discount_code}'
    
    def clean_fields(self, exclude=None):
        if self.discount_rate <= 0 and self.discount <= 0:
            raise ValidationError(message=_('The "discount_rate" field and "discount" field cannot be less than or equal to 0.'))
        if self.discount_rate > 0 and self.discount > 0:
            raise ValidationError(message=_('The "discount_rate" and "discount" fields cannot be greater than or equal to 0 together.'))
        return super().clean_fields(exclude)
    
    def update_model(self, model_object=None, **extra_fields):
        if model_object is None or not isinstance(model_object, Discount):
            raise ValidationError(message=_('The object can`t be updated.'))

        for field, value in extra_fields.items():
            setattr(model_object, field, value)

        model_object.save()
        return model_object
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)




class Reservation(models.Model):
    id_room = models.ForeignKey(Room, related_name='room_reservation_reference', on_delete=models.RESTRICT)
    id_account = models.ForeignKey(Account, related_name='account_reservation_reference', null=True, blank=False, on_delete=models.SET_NULL)
    id_discount = models.ForeignKey(Discount, related_name='discount_reservation_reference', null=True, blank=True, on_delete=models.SET_NULL)
    guest = models.PositiveSmallIntegerField(verbose_name=_('Number'), blank=False)
    price = models.DecimalField(verbose_name=_('Price'), unique=False, max_digits=9, decimal_places=2, default=0)
    check_in = models.DateTimeField(verbose_name=_('Check In'), unique=False)
    check_out = models.DateTimeField(verbose_name=_('Check Out'), unique=False)
    has_canceled = models.BooleanField(verbose_name=_('Cancellation'), unique=False, default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(Account, related_name='update_by_reservation_reference', null=True, blank=False, on_delete=models.SET_NULL)
   

    class Meta:
        verbose_name = _('Reservation')
        verbose_name_plural = _('Reservations')

    def __str__(self):
        return f'R{self.id_room}-I{self.check_in}-O{self.check_out}'
    
    def clean_fields(self, exclude=None):
        if self.check_in >= self.check_out:
            raise ValidationError(message=_('The date in the "check_out" field cannot be less than or equal to the date in the "check_in" field'))
        return super().clean_fields(exclude)
    
    def create_model(self, **extra_fields):
        model_object = Reservation(**extra_fields)
        model_object.full_clean()
        model_object.price = Reservation.calculated_price(self, check_in=extra_fields.get('check_in'), check_out=extra_fields.get('check_out'), id_room=extra_fields.get('id_room'), id_discount=None if not 'id_discount' in extra_fields.keys() else extra_fields.get('id_discount'))
        
        model_object.save()
        return model_object
    
    def update_model(self, model_object=None, **extra_fields):
        if model_object is None or not isinstance(model_object, Reservation):
            raise ValidationError(message=_('The object can`t be updated.'))
        
        for field, value in extra_fields.items():
            setattr(model_object, field, value)

        model_object.save()
        return model_object
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def calculated_price(self, check_in : datetime, check_out : datetime, id_room=None, id_discount=None):
        if id_room is None or not isinstance(id_room, Room):
            raise ValidationError(message=_('The price cannot be calculated with the input Room object'))
        if id_discount is not None and not isinstance(id_discount, Discount):
            raise ValidationError(message=_('The price cannot be calculated with the input Discount object'))

        days = check_out - check_in
        price = id_room.price * days.days
        if id_discount:
            if id_discount.discount:
                price -= id_discount.discount
                if id_discount.discount > price:
                    price = 0
            elif id_discount.discount_rate:
                price = round(price*(1-(id_discount.discount_rate/100)),2 )
            else:
                raise ValidationError(message=_('The discount could not be applied.'))
        return price

    def canceled_reservation(self, model_object=None):
        if model_object is None or not isinstance(model_object, Reservation):
            raise ValidationError(message=_('The object can`t be updated.'))
        
        model_object.has_canceled = False
        model_object.save()
        return model_object

    



