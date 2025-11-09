from django.db import models

from .model_fields_mixins import (
    MnsiFieldsModelMixin,
    MnsiLeftFootFieldsModelMixin,
    MnsiRightFootFieldsModelMixin,
)
from .model_methods_mixins import MnsiMethodsModelMixin


class MnsiModelMixin(
    MnsiRightFootFieldsModelMixin,
    MnsiLeftFootFieldsModelMixin,
    MnsiFieldsModelMixin,
    MnsiMethodsModelMixin,
    models.Model,
):
    """Neuropathy screening tool.

    Uses Michigan Neuropathy Screening Instrument (MNSI), see:
        https://pubmed.ncbi.nlm.nih.gov/7821168/
        https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3641573/ (omits monofilament testing)
        https://medicine.umich.edu/sites/default/files/downloads/MNSI_howto.pdf

    """

    class Meta:
        abstract = True
        verbose_name = "Michigan Neuropathy Screening Instrument (MNSI)"
        verbose_name_plural = "Michigan Neuropathy Screening Instrument (MNSI)"
