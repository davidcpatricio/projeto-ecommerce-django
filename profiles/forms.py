from django import forms
from django.contrib.auth.models import User

from . import models


class ProfileForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = '__all__'
        exclude = ('site_user',)


class UserForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
    )

    confirm_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
    )

    def __init__(self, site_user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.site_user = site_user

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username',
                  'password', 'confirm_password')

    def clean(self, *args, **kwargs):
        data = self.data
        cleaned = self.cleaned_data
        validation_error_msgs = {}

        username_data = cleaned.get('username')
        email_data = cleaned.get('email')
        password_data = cleaned.get('password')
        confirm_password_data = cleaned.get('confirm_password')

        username_db = User.objects.filter(username=username_data).first()
        email_db = User.objects.filter(email=email_data).first()

        error_msg_username_exists = 'Username already exists.'
        error_msg_email_exists = 'E-mail address already exists.'
        error_msg_password_match = 'Passwords do not match.'
        error_msg_password_short = \
            'Password must contain at least 6 characters.'
        error_msg_required_field = 'Required field.'

        # Logged in users (update)
        if self.site_user:
            if username_db:
                if username_data != username_db.username:
                    validation_error_msgs['username'] = \
                        error_msg_username_exists

            if email_db:
                if email_data != email_db.email:
                    validation_error_msgs['email'] = error_msg_email_exists

            if password_data:
                if password_data != confirm_password_data:
                    validation_error_msgs['password'] = \
                        error_msg_password_match
                    validation_error_msgs['confirm_password'] = \
                        error_msg_password_match

                if len(password_data) < 6:
                    validation_error_msgs['password'] = \
                        error_msg_password_short
        # Not logged in users (register)
        else:
            if username_db:
                validation_error_msgs['username'] = error_msg_username_exists

            if email_db:
                validation_error_msgs['email'] = error_msg_email_exists

            if not password_data:
                validation_error_msgs['password'] = error_msg_required_field

            if not confirm_password_data:
                validation_error_msgs['confirm_password'] = \
                    error_msg_required_field

            if password_data != confirm_password_data:
                validation_error_msgs['password'] = error_msg_password_match
                validation_error_msgs['confirm_password'] = \
                    error_msg_password_match

            if len(password_data) < 6:
                validation_error_msgs['password'] = error_msg_password_short

        if validation_error_msgs:
            raise forms.ValidationError(validation_error_msgs)
