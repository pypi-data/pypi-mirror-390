from django.db import models

from ..calculator import MnsiCalculator


class MnsiMethodsModelMixin(models.Model):
    def update_mnsi_calculated_fields(self) -> None:
        """Calculates the MNSI scores and updates fields.

        Called in a signal.
        """
        mnsi_calculator = MnsiCalculator(model_obj=self)
        self.calculated_patient_history_score = mnsi_calculator.patient_history_score()
        self.calculated_physical_assessment_score = mnsi_calculator.physical_assessment_score()
        self.save(
            update_fields=[
                "calculated_patient_history_score",
                "calculated_physical_assessment_score",
            ]
        )

    class Meta:
        abstract = True
