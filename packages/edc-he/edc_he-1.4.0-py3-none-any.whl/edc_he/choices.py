from clinicedc_constants import (
    DONT_KNOW,
    DWTA,
    MONTHLY,
    NOT_APPLICABLE,
    OPTION_RETIRED,
    OTHER,
    PRIMARY,
    SECONDARY,
    TERTIARY,
    WEEKLY,
    YEARLY,
)
from django.utils.translation import gettext_lazy as _

from .constants import (
    ACRES,
    ALL_WINDOWS_SCREENED,
    BROTHER_SISTER,
    DECIMALS,
    FAMILY_OWNED,
    GRANDCHILD,
    HECTARES,
    JOINT_OWNED,
    NON_FAMILY_OWNED,
    OWNER,
    PARENT,
    PARENTINLAW,
    SOME_WINDOWS_SCREENED,
    SON_DAUGHTER,
    SON_DAUGHTERINLAW,
    SQ_FEET,
    SQ_METERS,
    WIFE_HUSBAND,
)

EDUCATION_CERTIFICATES_CHOICES = (
    (PRIMARY, _("Primary Certificate")),
    (SECONDARY, _("Secondary Certificate")),
    (TERTIARY, _("post-Secondary/Tertiary/College")),
    (OTHER, _("Other, specify ...")),
    (NOT_APPLICABLE, _("Not applicable, never went to school")),
)

RELATIONSHIP_CHOICES = (
    (WIFE_HUSBAND, _("Wife/Husband")),
    (SON_DAUGHTER, _("Son/Daughter")),
    (SON_DAUGHTERINLAW, _("Son/Daughter-in-law")),
    (GRANDCHILD, _("Grandchild")),
    (PARENT, _("Parent")),
    (PARENTINLAW, _("Parent-in-law")),
    (BROTHER_SISTER, _("Brother/Sister")),
    (OTHER, _("Other, specify ...")),
    (DONT_KNOW, _("Don't know")),
    (NOT_APPLICABLE, _("Not applicable")),
)

EMPLOYMENT_STATUS_CHOICES = (
    ("1", _("Full time employed")),
    ("2", _("Regular part time employed ")),
    ("9", _("Self employed ")),
    ("3", _("Irregular/ occasional/ day worker employment")),
    ("4", _("Non-paid/ voluntary role ")),
    ("5", _("Student")),
    ("6", _("Homemaker")),
    ("7", _("Unemployed (able to work)")),
    ("8", _("Unemployed (unable to work)")),
    (DONT_KNOW, _("Don't know")),
    (NOT_APPLICABLE, _("Not applicable")),
)


MARITAL_CHOICES = (
    ("1", _("Never Married (but not co-habiting)")),
    ("2", _("Co-habiting")),
    ("3", _("Currently Married")),
    ("4", _("Separated/Divorced")),
    ("5", _("Widowed")),
    (OTHER, _("Other, specify ...")),
    (DONT_KNOW, _("Don't know")),
    (NOT_APPLICABLE, _("Not applicable")),
)


RESIDENCE_OWNERSHIP_CHOICES = (
    ("renter", _("Rent")),
    (OWNER, _("Own themselves")),
    (FAMILY_OWNED, _("Owned by someone else in family")),
    (NON_FAMILY_OWNED, _("Owned by someone else other than family member")),
    (JOINT_OWNED, _("Owned together with someone")),
)

WATER_SOURCE_CHOICES = (
    ("piped_into_plot", _("Piped into dwelling/yard plot")),
    ("piped_to_neighbour", _("Piped to neighbour")),
    ("standpipe", _("Public tap/standpipe")),
    ("borehole", _("Tube well or borehole")),
    ("protected_well", _("Protected dug well")),
    ("protected_spring", _("Protected spring")),
    ("rainwater", _("Rainwater")),
    (
        "bottled_water_improved",
        "Bottled water, improved source for cooking/hand washing (1-7)",
    ),
    ("unprotected_well", _("Unprotected dug well")),
    ("unprotected_spring", _("Unprotected spring")),
    ("tanker", _("Tanker truck/cart with small tank")),
    ("surface_water", _("Surface water (river etc.)")),
    (
        "bottled_water_unimproved",
        "Bottle water, unimproved source for cooking/hand washing (9-12)",
    ),
    (OTHER, _("Other, specify ...")),
)


WATER_OBTAIN_CHOICES = (
    ("on_premises", _("Water on premises (includes water piped to a neighbour)")),
    ("less_30min", _("Less than 30 minutes")),
    ("greater_30min", _("30 minutes or longer")),
    (DONT_KNOW, _("Don't know")),
)


TOILET_CHOICES = (
    ("1", _("1. Flush/pour flush to piped sewer system - private")),
    ("2", _("2. Flush/pour flush to septic tank - private ")),
    ("3", _("3. Flush/pour flush to pit latrine - private")),
    ("4", _("4. Ventilated improved pit (VIP) latrine - private ")),
    ("5", _("5. Pit latrine with slab - private")),
    ("6", _("6. Composting toilet - private")),
    ("7", _("7. EcoSan - private")),
    ("8", _("8. Flush/pour flush to piped sewer system - shared")),
    ("9", _("9. Flush/pour flush to septic tank - shared")),
    ("10", _("10. Flush/pour flush to pit latrine - shared")),
    ("11", _("11. Ventilated improved pit (VIP) latrine - shared")),
    ("12", _("12. Pit latrine with slab - shared")),
    ("13", _("13. Composting toilet - shared")),
    ("14", _("14. EcoSan - shared")),
    ("15", _("15. Flush/pour flush not to sewer/septic tank/pit latrine")),
    ("16", _("16. Pit latrine with slab (non-washable)")),
    ("17", _("17. Pit latrine without slab/open pit")),
    ("18", _("18. Bucket")),
    ("19", _("19. Hanging toilet/hanging latrine")),
    ("20", _("20. Open defecation (no facility/bush/field)")),
    (OTHER, _("Other, specify ...")),
)

ROOF_MATERIAL_CHOICES = (
    ("1", _("Thatch, Straw")),
    ("2", _("Mud and poles")),
    ("3", _("Tin")),
    ("4", _("Wood")),
    ("5", _("Iron sheet")),
    ("6", _("Tiles ")),
    ("7", _("Cement")),
    (OTHER, _("Other, specify ...")),
)

EAVES_CHOICES = (
    ("1", _("All eaves closed")),
    ("2", _("All eaves open")),
    ("3", _("Partially closed")),
)

EXTERNAL_WALL_MATERIALS_CHOICES = (
    ("1", _("Thatch, Straw")),
    ("2", _("Mud and poles")),
    ("3", _("Timber")),
    (OPTION_RETIRED, _("Un-burnt bricks")),
    ("5", _("Bricks with mud")),
    ("6", _("Bricks with cement")),
    ("7", _("Cement blocks")),
    ("8", _("Stone")),
    (OTHER, _("Other, specify ...")),
)

WINDOW_MATERIAL_CHOICES = (
    ("1", _("Glass")),
    ("2", _("Bags")),
    ("3", _("Wood")),
    ("4", _("Iron/metal")),
    ("5", _("Screens")),
    ("6", _("No windows")),
    (OTHER, _("Other, specify ...")),
)

WINDOW_SCREENING_CHOICES = (
    (ALL_WINDOWS_SCREENED, _("All windows screened")),
    ("2", _("No windows screened")),
    (SOME_WINDOWS_SCREENED, _("Some windows screened")),
)

WINDOW_SCREENING_TYPE_CHOICES = (
    ("1", _("Wire mesh")),
    ("2", _("Old bednet")),
    ("3", _("No windows screened")),
    ("4", _("No windows")),
    (NOT_APPLICABLE, _("Not applicable")),
)

FLOOR_MATERIALS_CHOICES = (
    ("6", _("Earth, sand")),
    ("7", _("Dung, wood, planks, palm, bamboo")),
    ("8", _("Parquet, polished wood, vinyl, asphalt strips")),
    ("9", _("Ceramic tiles")),
    ("10", _("Cement")),
    ("11", _("Carpet")),
    (OTHER, _("Other, specify ...")),
)

LAND_AREA_UNITS = (
    (HECTARES, _("hectares")),
    (ACRES, _("acres")),
    (DECIMALS, _("decimals (1 decimal = hundredth of an acre)")),
    (SQ_FEET, _("sq. feet (length * width)")),
    (SQ_METERS, _("sq. meters (length * width)")),
    (NOT_APPLICABLE, _("Not applicable")),
)
LIGHTING_CHOICES = (
    ("1", _("Electricity")),
    ("2", _("Paraffin, kerosene or gas lantern ")),
    ("3", _("Firewood")),
    ("4", _("Candle")),
    (OTHER, _("Other, specify ...")),
)

COOKING_FUEL_CHOICES = (
    ("1", _("Electricity")),
    ("2", _("LPG/natural gas/biogas")),
    ("3", _("Kerosene")),
    ("4", _("Charcoal")),
    ("5", _("Wood")),
    ("6", _("Coal/lignite, straw/shrubs/grass. agricultural crop, animal dung")),
    ("7", _("No food cooked in the household")),
    (OTHER, _("Other, specify ...")),
)

INCOME_TIME_ESTIMATE_CHOICES = (
    (WEEKLY, _("as weekly income")),
    (MONTHLY, _("as monthly income")),
    (YEARLY, _("as yearly income")),
    (DONT_KNOW, _("Don't know")),
    (DWTA, _("Don't want to answer")),
    (NOT_APPLICABLE, _("Not applicable")),
)

STATUS = (
    ("1", _("Very good")),
    ("2", _("Good")),
    ("3", _("Moderate")),
    ("4", _("Bad")),
    ("5", _("Very bad")),
    (DWTA, _("Don't want to answer")),
)

FINANCIAL_STATUS = (
    ("1", _("Among most wealthy")),
    ("2", _("Above average ")),
    ("3", _("Average wealth")),
    ("4", _("Below average")),
    ("5", _("Among least wealthy")),
    (DWTA, _("Don't want to answer")),
)

REMITTANCE_CURRENCY_CHOICES = (
    ("USD", _("USD")),
    ("GBP", _("GBP")),
    (OTHER, _("Other, specify ...")),
    (DONT_KNOW, _("Don't know")),
)
