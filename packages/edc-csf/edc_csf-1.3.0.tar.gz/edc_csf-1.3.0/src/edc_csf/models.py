from django.db import models
from django.utils import timezone
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.managers import CurrentSiteManager
from edc_sites.model_mixins import SiteModelMixin
from edc_visit_tracking.managers import CrfModelManager

from .model_mixins import (
    BiosynexSemiQuantitativeCragMixin,
    CsfCultureModelMixin,
    CsfModelMixin,
    LpModelMixin,
    QuantitativeCultureModelMixin,
)


class LpCsf(
    UniqueSubjectIdentifierFieldMixin,
    LpModelMixin,
    CsfModelMixin,
    CsfCultureModelMixin,
    BiosynexSemiQuantitativeCragMixin,
    QuantitativeCultureModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):
    report_datetime = models.DateTimeField(default=timezone.now)

    objects = CrfModelManager()

    on_site = CurrentSiteManager()

    history = HistoricalRecords()

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Lumbar Puncture/Cerebrospinal Fluid"
        verbose_name_plural = "Lumbar Puncture/Cerebrospinal Fluid"
