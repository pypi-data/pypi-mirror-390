from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MagnetDataConfig(AppConfig):
    name = "magnet_data"
    verbose_name = _("magnet data")
    default_auto_field = 'django.db.models.AutoField'
