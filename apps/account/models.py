from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.core.exceptions import ValidationError


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

    def update(self, account=None, **extra_fields):
        """
        En este tipo de actualización no se permite convertir al usuario en Staff o Superuser.
        """
        if account is None:
            raise ValidationError(message=_('No se puede realizar ninguna actualización si no se recibe el usuario a actualizar.'))
        
        if 'is_staff' in extra_fields.keys():
            extra_fields.pop('is_staff')
        
        if 'is_superuser' in extra_fields.keys():
            extra_fields.pop('is_superuser')
        
        for field, value in extra_fields.items():
            setattr(account, field, value)

        if 'password' in extra_fields.keys():
            account.set_password(extra_fields['password'])

        account.save()
        return account
    
    def activate_user(self, account=None):
        """
        Se vuelve a conceder al usuario el acceso a los servicios.
        """
        if account is None:
            raise ValidationError(message=_('No se puede realizar ninguna actualización si no se recibe el usuario a actualizar.'))
    
        account.is_active = True
        account.save()
        return account
    
    def delete_logical(self, account=None):
        """
        Borrado lógico de un usuario, se marca con is_active = False para revocar su acceso.
        El usuario se puede volver a reactivar.
        """
        if account is None:
            raise ValidationError(message=_('No se puede realizar ninguna actualización si no se recibe el usuario a actualizar.'))
        
        account.is_active = False
        account.save()
        return account
    
    def delete_physical(self, account=None):
        """
        Borrado físico de un usuario, con este borrado no se puede recuperar al usuario.
        """
        if account is None:
            raise ValidationError(message=_('No se puede realizar ninguna actualización si no se recibe el usuario a actualizar.'))
        try:
            account.delete()
            return True
        except:
            return False
    
    def revoke_is_staff(self, account):
        """
        Revoca el privilegio de is_staff al usuario.
        """
        if account is None:
            raise ValidationError(message=_('No se puede realizar ninguna actualización si no se recibe el usuario a actualizar.'))
    
        account.is_staff = False
        account.save()
        return account
    
    def revoke_is_superuser(self, account):
        """
        Revoca el privilegio de is_superuser al usuario.
        """
        if account is None:
            raise ValidationError(message=_('No se puede realizar ninguna actualización si no se recibe el usuario a actualizar.'))
    
        account.is_superuser = False
        account.save()
        return account
    
    def add_is_staff(self, account):
        """
        Añade el privilegio de is_staff al usuario.
        """
        if account is None:
            raise ValidationError(message=_('No se puede realizar ninguna actualización si no se recibe el usuario a actualizar.'))
    
        account.is_staff = True
        account.save()
        return account
    
    def add_is_superuser(self, account):
        """
        Añade el privilegio de is_superuser al usuario.
        """
        if account is None:
            raise ValidationError(message=_('No se puede realizar ninguna actualización si no se recibe el usuario a actualizar.'))
    
        account.is_superuser = True
        account.save()
        return account


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
