# coding=utf-8


"""Modified from https://github.com/RideCo/django-libtech-emailuser."""

from __future__ import unicode_literals

from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import ugettext_lazy as _

from emailuser.models import EmailUser


class EmailUserCreationForm(forms.ModelForm):
    """A form that creates a user, with no privileges, from the given
    email and password.
    """
    error_messages = {
        'duplicate_email': _("A user with that  email already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }
    email = forms.EmailField(label=_("Email"))

    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput)
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=_(
            "Enter the same password as above, for verification."))

    class Meta(object):
        """Inner Meta class."""
        model = EmailUser
        fields = ("email",)

    def clean_password2(self):
        """Unsure of usage."""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    def save(self, commit=True):
        """Sets the password if one is provided."""
        user = super(EmailUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class EmailUserChangeForm(forms.ModelForm):
    """Presumably allows a user's password to be changed.

    Unsure of actual usage.
    """
    email = forms.EmailField(label=_("Email"))

    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            "Raw passwords are not stored, so there is no way to see "
            "this user's password, but you can change the password "
            "using <a href=\"password/\">this form</a>."))

    class Meta(object):
        """Inner Meta class."""
        model = EmailUser
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        super(EmailUserChangeForm, self).__init__(*args, **kwargs)
        perms = self.fields.get('user_permissions', None)
        if perms is not None:
            perms.queryset = perms.queryset.select_related(
                'content_type')

    def clean_password(self):
        """
        Regardless of what the user provides, return the initial value.

        This is done here, rather than on the field, because the
        field does not have access to the initial value.
        """
        return self.initial["password"]


class PasswordResetRequestForm(forms.Form):
    """Presumably allows a user's password to be reset.

    Unsure of actual usage.
    """
    email = forms.CharField(label=_("Email"))

    def clean_email(self):
        """Unsure of usage."""
        email = self.cleaned_data.get("email")
        if not EmailUser.objects.filter(email=email).exists():
            raise forms.ValidationError(
                _("No user with that email exists"))
        return email


class PasswordResetForm(forms.Form):
    """Presumably allows a user's password to be reset.

    Unsure of actual usage.
    """
    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
                                widget=forms.PasswordInput)

    def clean_password2(self):
        """Unsure of usage."""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                _("The two passwords did not match"))
        return password2
