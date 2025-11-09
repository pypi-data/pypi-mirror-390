from clinicedc_constants import NOT_APPLICABLE
from django.contrib import admin
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django_audit_fields.admin import audit_fieldset_tuple
from edc_crf.admin import crf_status_fieldset_tuple


class HealthEconomicsHouseholdHeadModelAdminMixin:
    form = None

    additional_instructions = format_html(
        "{html}",
        html=mark_safe(
            "<H5><B><font color='orange'>Interviewer to read</font></B></H5>"
            "<p>We want to learn about the household and we use these questions "
            "to get an understanding of wealth and opportunities in the community.</p>"
        ),  # nosec B703, B308
    )

    household_description = _(
        "we mean a person or persons (people/ members) "
        "who share the same kitchen (pot), live together, and run the household "
        "expenditure from the same income is known as a household"
    )
    household_member_description = _(
        "we mean a person identified on "
        "the basis that they shared a place of living together most of time for "
        "the past one year"
    )

    household_description_extra = _(
        "When it is difficult to demarcate "
        "'most of the time', living together for the past six months or more "
        "should be used to find out whether or not the person is a "
        "household member"
    )

    fieldsets = (
        (None, {"fields": ("subject_visit", "report_datetime")}),
        (
            "Household members",
            {
                "description": format_html(
                    "{html}",
                    html=mark_safe(  # noqa: S308
                        render_to_string(
                            "edc_he/household_head/household_members_description.html",
                            context=dict(
                                household_description=household_description,
                                household_member_description=household_member_description,
                                household_description_extra=household_description_extra,
                            ),
                        )
                    ),  # nosec B703, B308
                ),
                "fields": (
                    "hh_count",
                    "hh_minors_count",
                ),
            },
        ),
        (
            "Household head: Gender and age",
            {
                "description": "",
                "fields": (
                    "hoh",
                    "hoh_gender",
                    "hoh_age",
                ),
            },
        ),
        (
            "Head of household",
            {
                "description": format_html(
                    "{html}",
                    html=mark_safe(  # noqa: S308
                        render_to_string(
                            "edc_he/household_head/household_head_description.html"
                        )
                    ),  # nosec B703, B308
                ),
                "fields": (
                    "relationship_to_hoh",
                    "relationship_to_hoh_other",
                ),
            },
        ),
        (
            "Head of household: Religion",
            {
                "description": "",
                "fields": (
                    "hoh_religion",
                    "hoh_religion_other",
                ),
            },
        ),
        (
            "Head of household: Ethnicity",
            {
                "description": "",
                "fields": (
                    "hoh_ethnicity",
                    "hoh_ethnicity_other",
                ),
            },
        ),
        (
            "Head of household: Education",
            {
                "description": "",
                "fields": (
                    "hoh_education",
                    "hoh_education_other",
                ),
            },
        ),
        (
            "Head of household: Employment",
            {
                "description": "",
                "fields": (
                    "hoh_employment_status",
                    "hoh_employment_type",
                    "hoh_employment_type_other",
                ),
            },
        ),
        (
            "Head of household: Marital status",
            {
                "description": "",
                "fields": (
                    "hoh_marital_status",
                    "hoh_marital_status_other",
                ),
            },
        ),
        (
            "Head of household: Insurance",
            {
                "description": "",
                "fields": (
                    "hoh_insurance",
                    "hoh_insurance_other",
                ),
            },
        ),
        crf_status_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {  # noqa: RUF012
        "hoh": admin.VERTICAL,
        "relationship_to_hoh": admin.VERTICAL,
        "hoh_gender": admin.VERTICAL,
        "hoh_religion": admin.VERTICAL,
        "hoh_ethnicity": admin.VERTICAL,
        "hoh_education": admin.VERTICAL,
        "hoh_employment_status": admin.VERTICAL,
        "hoh_employment_type": admin.VERTICAL,
        "hoh_marital_status": admin.VERTICAL,
        "crf_status": admin.VERTICAL,
    }

    filter_horizontal = ("hoh_insurance",)

    def get_changeform_initial_data(self, request):
        defaults = super().get_changeform_initial_data(request)
        for fld in self.model._meta.get_fields():
            if fld.name in self.filter_horizontal:
                qs = fld.related_model.objects.filter(name=NOT_APPLICABLE)
                defaults.update({fld.name: qs})
            elif fld.name in self.radio_fields:
                if fld.related_model:
                    try:
                        value = fld.related_model.objects.get(name=NOT_APPLICABLE)
                    except AttributeError as e:
                        if "related_model" not in str(e):
                            raise
                    else:
                        defaults.update({fld.name: value})
        return defaults
