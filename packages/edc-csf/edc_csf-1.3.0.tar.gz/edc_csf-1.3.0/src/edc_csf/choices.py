from clinicedc_constants import (
    MILLIGRAMS_PER_DECILITER,
    MILLIMOLES_PER_LITER,
    MM3,
    THERAPEUTIC_LP,
)
from edc_reportable.units import MILLIMOLES_PER_LITER_DISPLAY, MM3_DISPLAY

LP_REASON = (
    ("scheduled_per_protocol", "Scheduled per protocol"),
    (THERAPEUTIC_LP, "Therapeutic LP"),
    ("clincal_deterioration", "Clinical deterioration"),
)

MG_MMOL_UNITS = (
    (MILLIGRAMS_PER_DECILITER, MILLIGRAMS_PER_DECILITER),
    (MILLIMOLES_PER_LITER, MILLIMOLES_PER_LITER_DISPLAY),
)


MM3_PERC_UNITS = ((MM3, MM3_DISPLAY), ("%", "%"))
