from clinicedc_constants import NULL_STRING
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from edc_constants.choices import YES_NO_DONT_KNOW, YES_NO_DONT_KNOW_DWTA

from ..choices import FINANCIAL_STATUS, REMITTANCE_CURRENCY_CHOICES, STATUS
from ..model_mixin_factories import income_model_mixin_factory


class IncomeModelMixin(income_model_mixin_factory(), models.Model):
    external_remit_currency = models.CharField(
        verbose_name=_("In what currency do you receive remittances?"),
        max_length=50,
        choices=REMITTANCE_CURRENCY_CHOICES,
        default=NULL_STRING,
        blank=True,
    )

    external_remit_currency_other = models.CharField(
        verbose_name=_("If OTHER currency, specify ..."),
        max_length=50,
        default=NULL_STRING,
        blank=True,
    )

    more_sources_other = models.CharField(
        verbose_name=_("If YES additional sources, specify ..."),
        max_length=50,
        default=NULL_STRING,
        blank=True,
    )

    external_dependents = models.IntegerField(
        verbose_name=_(
            "Outside of this household, how many other people depend on this "
            "household's income?"
        ),
        validators=[MinValueValidator(0), MaxValueValidator(15)],
        help_text=_(
            "Insert '0' if no dependents other than the members in the household roster"
        ),
    )

    income_enough = models.CharField(
        verbose_name=(
            "Thinking about the income for this household, do you "
            "believe that it is enough money to cover your daily living "
            "needs and obligations?"
        ),
        max_length=15,
        choices=YES_NO_DONT_KNOW,
    )

    financial_status = models.CharField(
        verbose_name=_("Would you say your household's financial situation is?"),
        max_length=25,
        choices=STATUS,
    )

    financial_status_compare = models.CharField(
        verbose_name=_(
            "How would you rate your household's financial situation compared with others in "
            "your community?"
        ),
        max_length=25,
        choices=FINANCIAL_STATUS,
    )

    household_debt = models.CharField(
        verbose_name=_(
            "Does your household or any members of the household have current debt "
            "or outstanding loans?"
        ),
        max_length=25,
        choices=YES_NO_DONT_KNOW_DWTA,
    )

    household_debt_value = models.IntegerField(
        verbose_name=_("What is the approximate total amount of this debt or loan(s)?"),
        validators=[MinValueValidator(1), MaxValueValidator(9999999999)],
        null=True,
        blank=True,
        help_text=_("In local currency"),
    )

    class Meta:
        abstract = True
