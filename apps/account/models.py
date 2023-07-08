from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models


# Create your models here.
class UserManager(BaseUserManager):
    def _create_user(self, email, name, last_name, password, is_staff, is_superuser, **extra_fields):
        user = self.model(
            email = email,
            name = name,
            last_name = last_name,
            is_staff = is_staff,
            is_superuser = is_superuser,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(self, email, name, last_name, password=None, **extra_fields):
        return self._create_user(email, name, last_name, password, False, False, **extra_fields)
    
    def create_staff(self, email, name, last_name, password=None, **extra_fields):
        return self._create_user(email, name, last_name, password, True, False, **extra_fields)

    def create_superuser(self, email, name, last_name, password=None, **extra_fields):
        return self._create_user(email, name, last_name, password, True, True, **extra_fields)

class Account(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(verbose_name=_('Email'),max_length=250, unique=True)
    name = models.CharField(verbose_name=_('Nombre'), max_length=150, unique=False)
    last_name = models.CharField(verbose_name=_('Apellidos'), max_length=250, unique=False)
    is_staff = models.BooleanField(default = False)
    is_active = models.BooleanField(blank=True, default = False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name','last_name']

    class Meta:
        verbose_name = _('Account')
        verbose_name_plural = _('Accounts')
    
    def __str__(self):
        return self.email

    def get_full_name(self):
        return f'{self.name} {self.last_name}'
