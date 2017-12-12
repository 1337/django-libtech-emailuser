# coding=utf-8


"""Modified from https://github.com/RideCo/django-libtech-emailuser."""


from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin)
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _


class EmailUserManager(BaseUserManager):
    """Additional methods for the users table."""
    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a User with the given username, email
        and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        user = EmailUser(
            email=email, is_staff=False, is_active=True,
            is_superuser=False, last_login=now, date_joined=now,
            **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Creates a superuser. See create_user."""
        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class EmailUser(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username, password and email are required. Other fields are optional.
    """

    first_name = models.CharField(_('first name'), max_length=30,
                                  blank=True)
    last_name = models.CharField(_('last name'), max_length=30,
                                 blank=True)
    email = models.EmailField(_('email address'), unique=True)
    is_staff = models.BooleanField(
        _('staff status'), default=False,
        help_text=_('Designates whether the user can log into this '
                    'admin site.'))
    is_active = models.BooleanField(
        _('active'), default=True,
        help_text=_(
            'Designates whether this user should be treated as '
            'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'),
                                       default=timezone.now)

    objects = EmailUserManager()

    USERNAME_FIELD = 'email'

    class Meta(object):
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __unicode__(self):
        """Show the user email."""
        if self.email:
            return self.email
        return u''

    def get_absolute_url(self):
        """Does not work. Do not use."""
        return "/users/%s/" % urlquote(self.username)

    def get_full_name(self):
        """Returns the first_name plus the last_name, with a space in
        between.

        Avoid using this method.
        http://www.kalzumeus.com/2010/06/17/falsehoods-programmers-believe-about-names/
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Returns the short name for the user.

        Avoid using this method.
        """
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        """Sends an email to this User.

        Avoid using this method.
        """
        send_mail(subject, message, from_email, [self.email])


class PasswordReset(models.Model):
    """Appears to store password reset records.

    The model does not appear to be in use.
    """
    user = models.ForeignKey(EmailUser)
    key = models.CharField(max_length=100)
    used = models.BooleanField(default=False)

    def __unicode__(self):
        """Show the object name."""
        return u'(Password reset)'
