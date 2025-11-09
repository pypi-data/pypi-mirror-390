from django.contrib import admin
from edc_list_data.admin import ListModelAdminMixin

from .admin_site import edc_he_admin
from .models import Ethnicities, InsuranceTypes, Nationalities, Religions


@admin.register(InsuranceTypes, site=edc_he_admin)
class InsuranceTypesAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(Nationalities, site=edc_he_admin)
class NationalitiesAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(Ethnicities, site=edc_he_admin)
class EthnicitiesAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(Religions, site=edc_he_admin)
class ReligionsAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass
