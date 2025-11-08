# -*- encoding: utf-8 -*-
""" Models for the holidays application """

# standard library
import datetime
import json
from urllib.request import Request
from urllib.request import urlopen

# django
from django.db import models
from django.utils.translation import gettext_lazy as _

from .enums import Countries


class Holiday(models.Model):
    date = models.DateField(
        help_text=_("The date of the holiday"),
    )
    name = models.CharField(
        help_text=_("The name of the holiday"), max_length=100, verbose_name=_("name")
    )
    country_code = models.CharField(
        help_text=_("The code of the country this holiday belongs to."),
        max_length=2,
        verbose_name=_("country code"),
        choices=Countries.django_model_choices,
    )

    class Meta:
        ordering = ("date",)
        verbose_name = _('holiday')
        verbose_name_plural = _('holidays')
        unique_together = (("date", "country_code"),)

    def __str__(self):
        return f"{self.country_code}-{self.date}"

    @classmethod
    def update_holidays(cls, country_code, year):
        request = Request(
            f'https://data.magnet.cl/api/v1/holidays/{country_code.lower()}/{year}/'
        )

        response = urlopen(request)
        data = json.loads(response.read())

        updated_ids = []

        for holiday_data in data['objects']:
            date_string = holiday_data['date']
            date = datetime.datetime.strptime(date_string, '%Y-%m-%d').date()
            name = holiday_data['name']

            updated_ids.append(cls.objects.update_or_create(
                date=date,
                country_code=country_code,
                defaults={
                    'name': name,
                },
            )[0].id)

        cls.objects.filter(
            date__year=year,
            country_code=country_code,
        ).exclude(id__in=updated_ids).delete()
