from django.utils.translation.trans_null import gettext as _
from edc_crf.model_mixins import CrfModelMixin
from edc_model.models import BaseUuidModel

from ..model_mixins import EducationModelMixin


class Education(EducationModelMixin, CrfModelMixin, BaseUuidModel):
    class Meta(CrfModelMixin.Meta, BaseUuidModel.Meta):
        verbose_name = _("Health Economics: Education")
        verbose_name_plural = _("Health Economics: Education")
        indexes = (*CrfModelMixin.Meta.indexes, *BaseUuidModel.Meta.indexes)
