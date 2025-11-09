from django.contrib import admin
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django_audit_fields.admin import audit_fieldset_tuple
from edc_crf.admin import crf_status_fieldset_tuple


def get_income_fieldsets_tuple() -> list[tuple]:
    fieldsets = []
    sources = [
        ("wages", _("Wages / Salary")),
        ("selling", _("Selling, trading or hawking")),
        ("rental_income", _("Rental income")),
        ("pension", _("Pension, etc.")),
        ("ngo_assistance", _("NGO assistance")),
        ("interest", _("Interest and dividends")),
        ("internal_remit", _("Money transfers (domestic)")),
        ("external_remit", _("Remittances (from outside the country)")),
        ("more_sources", _("Other sources of income")),
    ]
    for fld, label in sources:
        fields = [
            fld,
            f"{fld}_value_known",
            f"{fld}_value",
        ]
        if fld == "external_remit":
            fields.extend(["external_remit_currency", "external_remit_currency_other"])
        if fld == "more_sources":
            fields.insert(1, "more_sources_other")

        fieldsets.append(
            (
                label,
                {
                    "description": format_html(
                        "{html}",
                        html=mark_safe(  # noqa: S308
                            _(
                                "Estimate the total amount of income from this source "
                                "for the <b>household</b> over the time period indicated"
                            )
                        ),  # nosec B703, B308
                    ),
                    "fields": tuple(fields),
                },
            )
        )
    return fieldsets


class HealthEconomicsIncomeModelAdminMixin:
    form = None

    additional_instructions = format_html(
        "{html}",
        html=mark_safe(  # noqa: S308
            render_to_string("edc_he/income/additional_instructions.html")
        ),
    )

    fieldsets = (
        (None, {"fields": ("subject_visit", "report_datetime")}),
        *get_income_fieldsets_tuple(),
        (
            "Dependents, financial status",
            {
                "fields": (
                    "external_dependents",
                    "income_enough",
                    "financial_status",
                    "financial_status_compare",
                )
            },
        ),
        (
            "Debt / Loans",
            {
                "description": format_html(
                    "{html}",
                    html=mark_safe(  # noqa: S308
                        render_to_string("edc_he/income/debt_loans.html")
                    ),
                ),
                "fields": (
                    "household_debt",
                    "household_debt_value",
                ),
            },
        ),
        crf_status_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {  # noqa: RUF012
        "wages": admin.VERTICAL,
        "wages_value_known": admin.VERTICAL,
        "selling": admin.VERTICAL,
        "selling_value_known": admin.VERTICAL,
        "rental_income": admin.VERTICAL,
        "rental_income_value_known": admin.VERTICAL,
        "pension": admin.VERTICAL,
        "pension_value_known": admin.VERTICAL,
        "ngo_assistance": admin.VERTICAL,
        "ngo_assistance_value_known": admin.VERTICAL,
        "interest": admin.VERTICAL,
        "interest_value_known": admin.VERTICAL,
        "internal_remit": admin.VERTICAL,
        "internal_remit_value_known": admin.VERTICAL,
        "external_remit": admin.VERTICAL,
        "external_remit_value_known": admin.VERTICAL,
        "external_remit_currency": admin.VERTICAL,
        "more_sources": admin.VERTICAL,
        "more_sources_value_known": admin.VERTICAL,
        "income_enough": admin.VERTICAL,
        "financial_status": admin.VERTICAL,
        "financial_status_compare": admin.VERTICAL,
        "household_debt": admin.VERTICAL,
        "crf_status": admin.VERTICAL,
    }
