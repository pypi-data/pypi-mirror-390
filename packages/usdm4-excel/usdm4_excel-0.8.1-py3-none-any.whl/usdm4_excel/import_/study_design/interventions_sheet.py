from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.study_intervention import StudyIntervention
from usdm4.api.administration import Administration
from usdm4.api.duration import Duration
from usdm4.api.administrable_product import AdministrableProduct


class InterventionsSheet(BaseSheet):
    SHEET_NAME = "studyDesignInterventions"

    def __init__(self, file_path: str, builder: Builder, errors: Errors):
        try:
            self.items = []
            super().__init__(
                file_path=file_path,
                builder=builder,
                errors=errors,
                sheet_name=self.SHEET_NAME,
                optional=True,
            )
            if self._success:
                self.current_name = None
                self.current_intervention = None
                for index, row in self._sheet.iterrows():
                    admin_duration = self._create_administration_duration(index)
                    agent_admin = self._create_administration(index, admin_duration)
                    self._create_intervention(index, agent_admin)
        except Exception as e:
            self._sheet_exception(e)

    def _create_intervention(self, index, agent_admin):
        name = self._read_cell_by_name(index, "name")
        if name and name != self.current_name:
            self.current_name = name
            role = self._read_cdisc_klass_attribute_cell_by_name(
                "StudyIntervention", "role", index, "role", allow_empty=True
            )
            params = {
                "name": name,
                "description": self._read_cell_by_name(
                    index, "description", must_be_present=False
                ),
                "label": self._read_cell_by_name(index, "label", must_be_present=False),
                "codes": self._read_other_code_cell_multiple_by_name(index, "codes"),
                "role": role,
                "type": self._read_cdisc_klass_attribute_cell_by_name(
                    "StudyIntervention", "type", index, "type"
                ),
                "minimumResponseDuration": self._read_quantity_cell_by_name(
                    index, "minimumResponseDuration"
                ),
                "administrations": [agent_admin] if agent_admin else [],
            }
            item = self._create(StudyIntervention, params)
            if item:
                self.current_intervention = item
                self.items.append(item)
            else:
                self.current_intervention = None
        elif self.current_intervention and agent_admin:
            self.current_intervention.administrations.append(agent_admin)

    def _create_administration(self, index, admin_duration):
        product_name = self._read_cell_by_name(index, "product", must_be_present=False)
        product = self._builder.cross_reference.get_by_name(
            AdministrableProduct, product_name
        )
        product_id = product.id if product else None
        params = {
            "name": self._read_cell_by_name(index, "administrationName"),
            "description": self._read_cell_by_name(
                index, "administrationDescription", must_be_present=False
            ),
            "label": self._read_cell_by_name(
                index, "administrationLabel", must_be_present=False
            ),
            "duration": admin_duration,
            "dose": self._read_quantity_cell_by_name(index, "administrationDose"),
            "route": self._builder.alias_code(
                self._read_cdisc_klass_attribute_cell_by_name(
                    "Administration", "route", index, "administrationRoute"
                )
            ),
            "frequency": self._builder.alias_code(
                self._read_cdisc_klass_attribute_cell_by_name(
                    "Administration", "frequency", index, "administrationFrequency"
                )
            ),
            "administrableProductId": product_id,
        }
        item = self._create(Administration, params)
        return item

    def _create_administration_duration(self, index):
        params = {
            "text": self._read_cell_by_name(
                index, "administrationDurationDescription", must_be_present=False
            ),
            "durationWillVary": self._read_boolean_cell_by_name(
                index, "administrationDurationWillVary"
            ),
            "reasonDurationWillVary": self._read_cell_by_name(
                index, "administrationDurationWillVaryReason"
            ),
            "quantity": self._read_quantity_cell_by_name(
                index, "administrationDurationQuantity"
            ),
        }
        return self._create(Duration, params)
