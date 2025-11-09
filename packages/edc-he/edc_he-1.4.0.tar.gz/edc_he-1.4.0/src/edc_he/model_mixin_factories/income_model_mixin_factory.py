from __future__ import annotations

from clinicedc_constants import NOT_APPLICABLE
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext as _
from edc_constants.choices import YES_NO_DONT_KNOW_DWTA

from ..choices import INCOME_TIME_ESTIMATE_CHOICES

default_field_data = {
    "wages": _("Income from wages, salary from job"),
    "selling": _("Earnings from selling, trading or hawking products?"),
    "rental_income": _("Income from rental of property?"),
    "pension": (
        _(
            "State old-age (veteran's/civil service) pension*, contributory pension "
            "fund, provident fund or social security benefit?"
        ),
        _("Pensions by work"),
    ),
    "ngo_assistance": _("Assistance from nongovernmental organization"),
    "interest": (
        _("Interest, dividends"),
        _("(for example, from savings account or fixed deposits)?"),
    ),
    "internal_remit": _(
        "Money transfers from family members or friends residing inside the country"
    ),
    "external_remit": _(
        "Money transfers from family members or friends residing outside the country"
    ),
    "more_sources": _("Do you have additional sources of income not included above?"),
}


def income_model_mixin_factory(field_data: dict[str, str] | None = None):
    field_data = field_data or default_field_data

    class AbstractModel(models.Model):
        class Meta:
            abstract = True

    opts = {}
    for field_name, prompt in field_data.items():
        try:
            prompt, help_text = prompt  # noqa: PLW2901
        except ValueError:
            help_text = None
        opts.update(
            {
                field_name: models.CharField(
                    verbose_name=prompt,
                    max_length=15,
                    choices=YES_NO_DONT_KNOW_DWTA,
                    help_text=help_text,
                ),
                f"{field_name}_value_known": models.CharField(
                    verbose_name=_("Over which <u>time period</u> are you able to estimate?"),
                    max_length=15,
                    choices=INCOME_TIME_ESTIMATE_CHOICES,
                    default=NOT_APPLICABLE,
                ),
                f"{field_name}_value": models.IntegerField(
                    verbose_name=_(
                        "Estimated <u>total amount of income</u> from this source over the "
                        "time period from above"
                    ),
                    validators=[MinValueValidator(1), MaxValueValidator(999999999)],
                    null=True,
                    blank=True,
                    help_text=_("Use cash equivalent in local currency"),
                ),
            }
        )
    for fld_name, fld_cls in opts.items():
        AbstractModel.add_to_class(fld_name, fld_cls)

    return AbstractModel
