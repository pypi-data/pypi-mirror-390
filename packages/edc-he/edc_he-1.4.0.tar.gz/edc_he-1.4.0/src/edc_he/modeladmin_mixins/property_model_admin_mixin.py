from django.contrib import admin
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django_audit_fields.admin import audit_fieldset_tuple
from edc_crf.admin import crf_status_fieldset_tuple


class HealthEconomicsPropertyModelAdminMixin:
    form = None

    additional_instructions = _(
        "We want to learn about the household and we use these questions "
        "to get an understanding of wealth and opportunities in the community. "
    )
    fieldsets = (
        (None, {"fields": ("subject_visit", "report_datetime")}),
        (
            "Property",
            {
                "description": format_html(
                    "{html}",
                    html=mark_safe(  # noqa: S308
                        render_to_string("edc_he/property/description.html"),
                    ),
                ),
                "fields": (
                    "land_owner",
                    "land_value",
                    "land_surface_area",
                    "land_surface_area_units",
                    "land_additional",
                    "land_additional_value",
                ),
            },
        ),
        (
            "Calculated values",
            {
                "description": "To be calculated (or recalculated) when this form is saved",
                "classes": ("collapse",),
                "fields": ("calculated_land_surface_area",),
            },
        ),
        crf_status_fieldset_tuple,
        audit_fieldset_tuple,
    )

    readonly_fields = ("calculated_land_surface_area",)

    radio_fields = {  # noqa: RUF012
        "land_owner": admin.VERTICAL,
        "land_additional": admin.VERTICAL,
        "land_surface_area_units": admin.VERTICAL,
        "crf_status": admin.VERTICAL,
    }
