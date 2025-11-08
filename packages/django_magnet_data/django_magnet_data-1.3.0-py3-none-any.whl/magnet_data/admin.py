# django
from django.contrib import admin

from .holidays.models import Holiday


class HolidayAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "country_code")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]


admin.site.register(Holiday, HolidayAdmin)
