from __future__ import annotations

from clinicedc_constants import NO
from django.db import models
from django.utils.translation import gettext_lazy as _
from edc_constants.choices import YES_NO

default_field_data = {
    "solar_panels": _("Solar panels"),
    "radio": _("Radio"),
    "television": _("Television"),
    "mobile_phone": _("Mobile phone"),
    "computer": _("Computer"),
    "telephone": _("Non-mobile telephone"),
    "fridge": _("Fridge"),
    "generator": _("Generator"),
    "iron": _("Flat iron"),
    "bicycle": _("Bicycle"),
    "motorcycle": _("Motorcycle/scooter (PikiPiki/Boda Boda)"),
    "dala_dala": _("Dala Dala"),
    "car": _("Car"),
    "motorboat": _("Boat with a motor"),
    "large_livestock": _("Large Livestock (e.g. cows, bulls, other cattle, horses, donkeys)"),
    "small_animals": _("Small animals (goats, sheep, chickens or other poultry, etc)"),
    "shop": _("A business or shop"),
}


def assets_model_mixin_factory(field_data: dict[str, str] | None = None):
    field_data = field_data or default_field_data

    class AbstractModel(models.Model):
        class Meta:
            abstract = True

    opts = {}
    for field_name, prompt in field_data.items():
        opts.update(
            {
                field_name: models.CharField(
                    verbose_name=prompt,
                    max_length=15,
                    choices=YES_NO,
                    default=NO,
                ),
            }
        )
    for fld_name, fld_cls in opts.items():
        AbstractModel.add_to_class(fld_name, fld_cls)

    return AbstractModel
