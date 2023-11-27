import re

from django.contrib.auth.models import User
from django.db import models
from django.forms import ValidationError

from utils.validate_nif import validate_nif


class Profile(models.Model):
    site_user = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name='User'
    )
    date_of_birth = models.DateField()
    nif = models.CharField(max_length=9)
    address = models.CharField(max_length=100)
    number = models.CharField(max_length=10, blank=True)
    complement = models.CharField(max_length=30, blank=True)
    neighborhood = models.CharField(max_length=50, blank=True)
    postal_code = models.CharField(max_length=8)
    city = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.site_user}'

    def clean(self):
        error_messages = {}

        if not validate_nif(self.nif):
            error_messages['nif'] = 'Enter a valid NIF.'

        if re.search(r'^\\d{4}[- ]{0,1}\\d{3}$', self.postal_code) or \
                len(self.postal_code) != 8:
            error_messages['postal_code'] = 'Invalid postal code.'

        if error_messages:
            raise ValidationError(error_messages)
