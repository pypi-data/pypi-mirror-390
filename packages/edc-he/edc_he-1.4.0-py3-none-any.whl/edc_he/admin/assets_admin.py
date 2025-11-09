from clinicedc_constants import OPTION_RETIRED
from django.contrib import admin
from edc_crf.modeladmin_mixins import CrfModelAdmin

from ..admin_site import edc_he_admin
from ..choices import EXTERNAL_WALL_MATERIALS_CHOICES
from ..forms import HealthEconomicsAssetsForm
from ..modeladmin_mixins import HealthEconomicsAssetsModelAdminMixin
from ..models import HealthEconomicsAssets


@admin.register(HealthEconomicsAssets, site=edc_he_admin)
class HealthEconomicsAssetsAdmin(
    HealthEconomicsAssetsModelAdminMixin,
    CrfModelAdmin,
):
    form = HealthEconomicsAssetsForm

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "external_wall_material":
            kwargs["choices"] = self.external_wall_material_choices
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    @property
    def external_wall_material_choices(self) -> tuple[tuple[str, str]]:
        return tuple(
            [tpl for tpl in EXTERNAL_WALL_MATERIALS_CHOICES if tpl[0] != OPTION_RETIRED]
        )
