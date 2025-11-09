from django.utils.translation import gettext_lazy as _
from edc_crf.model_mixins import CrfModelMixin, SingletonCrfModelMixin
from edc_model.models import BaseUuidModel

from ..model_mixins import IncomeModelMixin


class HealthEconomicsIncome(
    SingletonCrfModelMixin,
    IncomeModelMixin,
    CrfModelMixin,
    BaseUuidModel,
):
    class Meta(CrfModelMixin.Meta, BaseUuidModel.Meta):
        verbose_name = _("Health Economics: Income")
        verbose_name_plural = _("Health Economics: Income")
        indexes = (*CrfModelMixin.Meta.indexes, *BaseUuidModel.Meta.indexes)
