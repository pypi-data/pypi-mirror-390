from django.db import models
from django.utils import timezone
from edc_identifier.model_mixins import UniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.managers import CurrentSiteManager
from edc_sites.model_mixins import SiteModelMixin

from ..model_mixins import MnsiModelMixin


class Mnsi(
    UniqueSubjectIdentifierFieldMixin,
    MnsiModelMixin,
    SiteModelMixin,
    BaseUuidModel,
):
    report_datetime = models.DateTimeField(default=timezone.now)

    objects = models.Manager()
    on_site = CurrentSiteManager()
    history = HistoricalRecords()

    class Meta(MnsiModelMixin.Meta, BaseUuidModel.Meta):
        pass
