from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django_audit_fields.admin import audit_fieldset_tuple
from edc_crf.admin import crf_status_fieldset_tuple


class HealthEconomicsAssetsModelAdminMixin:
    form = None

    additional_instructions = _(
        "We want to learn about the household and we use these questions "
        "to get an understanding of wealth and opportunities in the community. "
    )

    fieldsets = (
        (None, {"fields": ("subject_visit", "report_datetime")}),
        (
            _("Household assets"),
            {
                "fields": (
                    "residence_ownership",
                    "dwelling_value_known",
                    "dwelling_value",
                    "rooms",
                    "bedrooms",
                    "beds",
                    "roof_material",
                    "roof_material_other",
                    "external_wall_material",
                    "external_wall_material_other",
                    "external_window_material",
                    "external_window_material_other",
                    "floor_material",
                    "floor_material_other",
                    "electricity",
                    "lighting_source",
                    "lighting_source_other",
                    "cooking_fuel",
                    "cooking_fuel_other",
                )
            },
        ),
        (
            _("Drinking water and sanitation"),
            {
                "fields": (
                    "water_source",
                    "water_source_other",
                    "water_obtain_time",
                    "toilet",
                    "toilet_other",
                )
            },
        ),
        (
            _("Household assets (continued)"),
            {
                "description": format_html(
                    "{text1}? <BR>{text2}",
                    text1=_(
                        "Does your household or anyone in your household have the following "
                        "in working order"
                    ),
                    text2=_(
                        "Note: If a household owns one of the assets below but the asset "
                        "is not in working order then it should be marked as 'No'"
                    ),
                ),
                "fields": (
                    "radio",
                    "television",
                    "mobile_phone",
                    "computer",
                    "telephone",
                    "fridge",
                    "generator",
                    "iron",
                    "bicycle",
                    "motorcycle",
                    "dala_dala",
                    "car",
                    "motorboat",
                    "large_livestock",
                    "small_animals",
                    "shop",
                ),
            },
        ),
        crf_status_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {  # noqa: RUF012
        "bicycle": admin.VERTICAL,
        "car": admin.VERTICAL,
        "computer": admin.VERTICAL,
        "cooking_fuel": admin.VERTICAL,
        "crf_status": admin.VERTICAL,
        "dala_dala": admin.VERTICAL,
        "dwelling_value_known": admin.VERTICAL,
        "electricity": admin.VERTICAL,
        "external_wall_material": admin.VERTICAL,
        "external_window_material": admin.VERTICAL,
        "floor_material": admin.VERTICAL,
        "fridge": admin.VERTICAL,
        "generator": admin.VERTICAL,
        "iron": admin.VERTICAL,
        "large_livestock": admin.VERTICAL,
        "lighting_source": admin.VERTICAL,
        "mobile_phone": admin.VERTICAL,
        "motorboat": admin.VERTICAL,
        "motorcycle": admin.VERTICAL,
        "radio": admin.VERTICAL,
        "residence_ownership": admin.VERTICAL,
        "roof_material": admin.VERTICAL,
        "shop": admin.VERTICAL,
        "small_animals": admin.VERTICAL,
        "telephone": admin.VERTICAL,
        "television": admin.VERTICAL,
        "toilet": admin.VERTICAL,
        "water_obtain_time": admin.VERTICAL,
        "water_source": admin.VERTICAL,
    }
