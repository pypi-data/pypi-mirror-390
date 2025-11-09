from django.contrib import admin
from edc_crf.modeladmin_mixins import CrfModelAdmin

from ..admin_site import edc_he_admin
from ..forms import HealthEconomicsPropertyForm
from ..modeladmin_mixins import HealthEconomicsPropertyModelAdminMixin
from ..models import HealthEconomicsProperty


@admin.register(HealthEconomicsProperty, site=edc_he_admin)
class HealthEconomicsPropertyAdmin(HealthEconomicsPropertyModelAdminMixin, CrfModelAdmin):
    form = HealthEconomicsPropertyForm
