from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.core.exceptions import ValidationError


class AccountManager(BaseUserManager):
    def _create_user(self, email, full_name, password, is_staff, is_superuser, **extra_fields):
        try:
            validate_password(password=password)
        except:
            raise ValidationError(message=_('The password could not be validated'))
        
        account = self.model(
            email = email,
            full_name = full_name,
            is_staff = is_staff,
            is_superuser = is_superuser,
            **extra_fields
        )
        account.set_password(password)
        account.save(using=self.db)
        return account

    def create_user(self, email, full_name, password=None, **extra_fields):
        return self._create_user(email, full_name, password, False, False, **extra_fields)
    
    def create_staff(self, email, full_name, password=None, **extra_fields):
        return self._create_user(email, full_name, password, True, False, **extra_fields)

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        return self._create_user(email, full_name, password, True, True, **extra_fields)

    def update(self, account=None, **extra_fields):
        """
        In this type of update, converting the account into Staff or Superuser is not allowed.
        """
        if account is None:
            raise ValidationError(message=_('No update can be performed if the account to be updated is not received.'))
        
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
        Access to services is granted to the account again.
        """
        if account is None:
            raise ValidationError(message=_('No update can be performed if the account to be updated is not received.'))
    
        account.is_active = True
        account.save()
        return account
    
    def delete_logical(self, account=None):
        """
        Logical deletion of a account, marked with is_active = False to revoke their access.
        The account can be reactivated.
        """
        if account is None:
            raise ValidationError(message=_('No update can be performed if the account to be updated is not received.'))
        
        account.is_active = False
        account.save()
        return account
    
    def delete_physical(self, account=None):
        """
        Physical deletion of a account, with this deletion the account cannot be recovered.
        """
        if account is None:
            raise ValidationError(message=_('No update can be performed if the account to be updated is not received.'))
        try:
            account.delete()
            return True
        except:
            return False
    
    def revoke_is_staff(self, account=None):
        """
        Revoke the is_staff privilege from the account.
        """
        if account is None:
            raise ValidationError(message=_('No update can be performed if the account to be updated is not received.'))
    
        account.is_staff = False
        account.save()
        return account
    
    def revoke_is_superuser(self, account=None):
        """
        Revoke the is_superuser privilege from the account.
        """
        if account is None:
            raise ValidationError(message=_('No update can be performed if the account to be updated is not received.'))
    
        account.is_superuser = False
        account.save()
        return account
    
    def add_is_staff(self, account):
        """
        Add the is_staff privilege to the account.
        """
        if account is None:
            raise ValidationError(message=_('No update can be performed if the account to be updated is not received.'))
    
        account.is_staff = True
        account.save()
        return account
    
    def add_is_superuser(self, account=None):
        """
        Add the is_superuser privilege to the account.
        """
        if account is None:
            raise ValidationError(message=_('No update can be performed if the account to be updated is not received.'))
    
        account.is_superuser = True
        account.save()
        return account


class Account(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(verbose_name=_('Email'),max_length=250, unique=True)
    full_name = models.CharField(verbose_name=_('Full Name'), max_length=350, unique=False)
    is_staff = models.BooleanField(default = False)
    is_active = models.BooleanField(blank=True, default = False)

    objects = AccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name = _('Account')
        verbose_name_plural = _('Accounts')
    
    def __str__(self):
        return self.email