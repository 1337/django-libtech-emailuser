# coding=utf-8


"""Modified from https://github.com/RideCo/django-libtech-emailuser."""


# pylint: disable=invalid-name, protected-access
from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.utils import flatten_fieldsets
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from emailuser.forms import EmailUserChangeForm, EmailUserCreationForm
from emailuser.models import EmailUser


csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())


class EmailUserAdmin(admin.ModelAdmin):
    """Admin form for users. A subclass is actually used."""
    # pylint: disable=redefined-builtin
    add_form_template = 'admin/auth/user/add_form.html'
    change_user_password_template = None
    fieldsets = (
        (None, {'fields': ('email',
                           'password')}),
        (_('Personal info'), {'fields': ('first_name',
                                         'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff',
                                       'is_superuser',
                                       'groups',
                                       'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login',
                                           'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}),
    )
    form = EmailUserChangeForm
    add_form = EmailUserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

    def get_fieldsets(self, request, obj=None):
        """Unsure of usage."""
        if not obj:
            return self.add_fieldsets
        return super(EmailUserAdmin, self).get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """Use special form during user creation."""
        defaults = {}
        if obj is None:
            defaults.update({
                'form': self.add_form,
                'fields': flatten_fieldsets(self.add_fieldsets),
            })
        defaults.update(kwargs)
        return super(EmailUserAdmin, self).get_form(request, obj, **defaults)

    def get_urls(self):
        """Believed to retrieve some kind of URL.

        Avoid using this method.
        """
        from django.conf.urls import url
        return [
            url(r'^(\d+)/password/$',
                self.admin_site.admin_view(self.user_change_password)),
            url(r'^(\d+)/change/password/$',
                self.admin_site.admin_view(self.user_change_password)),
        ] + super(EmailUserAdmin, self).get_urls()

    @sensitive_post_parameters_m
    @csrf_protect_m
    @transaction.atomic
    def add_view(self, request, form_url='', extra_context=None):
        """It is an error for a user to have add permission but NOT
        change permission for users. If we allowed such users to add
        users, they could create superusers, which would mean they would
        essentially have the permission to change users.

        To avoid the problem entirely, we disallow users from adding
        users if they do not have change permission.
        """
        if not self.has_change_permission(request):
            if self.has_add_permission(request) and settings.DEBUG:
                # Raise Http404 in debug mode so that the user gets a helpful
                # error message.
                raise Http404(
                    'Your user does not have the "Change user" permission. In '
                    'order to add users, Django requires that your user '
                    'account have both the "Add user" and "Change user" '
                    'permissions set.')
            raise PermissionDenied()
        if extra_context is None:
            extra_context = {}
        username_field = self.model._meta.get_field(self.model.USERNAME_FIELD)
        defaults = {
            'auto_populated_fields': (),
            'username_help_text': username_field.help_text,
        }
        extra_context.update(defaults)
        return super(EmailUserAdmin, self).add_view(request, form_url,
                                                    extra_context)

    @sensitive_post_parameters_m
    def user_change_password(self, request, id, form_url=''):
        """Believed to allow a user to change the password."""
        if not self.has_change_permission(request):
            raise PermissionDenied()
        user = get_object_or_404(self.get_queryset(request), pk=id)
        if request.method == 'POST':
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                msg = ugettext('Password changed successfully.')
                messages.success(request, msg)
                return HttpResponseRedirect('..')
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        admin_form = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': _('Change password: %s') % escape(user.get_username()),
            'adminForm': admin_form,
            'form_url': form_url,
            'form': form,
            'is_popup': '_popup' in request.GET or '_popup' in request.POST,
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
        }
        return TemplateResponse(request,
                                self.change_user_password_template or
                                'admin/auth/user/change_password.html',
                                context)

    def response_add(self, request, obj, post_url_continue=None):
        """
        Determines the HttpResponse for the add_view stage. It mostly defers to
        its superclass implementation but is customized because the User model
        has a slightly different workflow.
        """
        # We should allow further modification of the user just added i.e. the
        # 'Save' button should behave like the 'Save and continue editing'
        # button except in two scenarios:
        # * The user has pressed the 'Save and add another' button
        # * We are adding a user in a popup
        if '_addanother' not in request.POST and '_popup' not in request.POST:
            request.POST['_continue'] = 1
        return super(EmailUserAdmin, self).response_add(request, obj,
                                                        post_url_continue)


admin.site.register(EmailUser, EmailUserAdmin)
