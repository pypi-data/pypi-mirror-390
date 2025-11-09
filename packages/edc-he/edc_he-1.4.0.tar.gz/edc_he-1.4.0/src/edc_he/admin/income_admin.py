from django.contrib import admin
from edc_crf.modeladmin_mixins import CrfModelAdmin

from ..admin_site import edc_he_admin
from ..forms import HealthEconomicsIncomeForm
from ..modeladmin_mixins import HealthEconomicsIncomeModelAdminMixin
from ..models import HealthEconomicsIncome


@admin.register(HealthEconomicsIncome, site=edc_he_admin)
class HealthEconomicsIncomeAdmin(HealthEconomicsIncomeModelAdminMixin, CrfModelAdmin):
    form = HealthEconomicsIncomeForm
