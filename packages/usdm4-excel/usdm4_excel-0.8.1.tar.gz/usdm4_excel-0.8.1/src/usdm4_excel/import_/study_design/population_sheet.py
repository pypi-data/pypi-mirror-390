from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.population_definition import StudyDesignPopulation, StudyCohort
from usdm4.api.characteristic import Characteristic
from usdm4.api.indication import Indication


class PopulationSheet(BaseSheet):
    SHEET_NAME = "studyDesignPopulations"

    def __init__(self, file_path: str, builder: Builder, errors: Errors):
        try:
            self._cohorts = []
            self.population = None
            super().__init__(
                file_path=file_path,
                builder=builder,
                errors=errors,
                sheet_name=self.SHEET_NAME,
                optional=True,
            )
            if self._success and not self._sheet.empty:
                for index, row in self._sheet.iterrows():
                    level = self._read_cell_by_name(index, "level")
                    name = self._read_cell_by_name(index, "name")
                    description = self._read_cell_by_name(index, "description")
                    label = self._read_cell_by_name(index, "label")
                    completion_number = self._read_range_quantity(
                        index,
                        "plannedCompletionNumber",
                    )
                    enrollment_number = self._read_range_quantity(
                        index,
                        "plannedEnrollmentNumber",
                    )

                    planned_age = self._read_range_cell_by_name(
                        index, "plannedAge", require_units=True, allow_empty=True
                    )
                    healthy = self._read_boolean_cell_by_name(
                        index, "includesHealthySubjects"
                    )
                    characteristics = self._read_cell_multiple_by_name(
                        index, "characteristics", must_be_present=False
                    )
                    indications = self._read_cell_multiple_by_name(
                        index, "indications", must_be_present=False
                    )
                    codes = self._build_codes(row, index)
                    if level.upper() == "MAIN":
                        self.population = self._study_population(
                            name,
                            description,
                            label,
                            enrollment_number,
                            completion_number,
                            planned_age,
                            healthy,
                            codes,
                        )
                    else:
                        _ = self._study_cohort(
                            name,
                            description,
                            label,
                            enrollment_number,
                            completion_number,
                            planned_age,
                            healthy,
                            codes,
                            characteristics,
                            indications,
                        )
                if self.population:
                    self.population.cohorts = self._cohorts
                elif not self._sheet.empty:
                    self._errors.error("Not main study population detected")
        except Exception as e:
            self._sheet_exception(e)

    def _build_codes(self, row, index):
        code = self._read_cdisc_klass_attribute_cell_by_name(
            "StudyDesignPopulation",
            "plannedSex",
            index,
            "plannedSexOfParticipants",
            allow_empty=True,
        )
        return [code] if code else []

    def _study_population(
        self,
        name: str,
        description: str,
        label: str,
        enrollment_number,
        completion_number,
        planned_age,
        healthy: bool,
        codes: list,
    ) -> StudyDesignPopulation:
        params = {
            "name": name,
            "description": description,
            "label": label,
            "includesHealthySubjects": healthy,
            "plannedEnrollmentNumber": enrollment_number,
            "plannedCompletionNumber": completion_number,
            "plannedAge": planned_age,
            "plannedSex": codes,
        }
        item = self._create(StudyDesignPopulation, params)
        return item

    def _study_cohort(
        self,
        name: str,
        description: str,
        label: str,
        enrollment_number,
        completion_number,
        planned_age,
        healthy: bool,
        codes: list,
        characteristics: list,
        indications: list,
    ) -> StudyCohort:
        characteristic_refs = self._resolve_characteristics(characteristics)
        indication_refs = self._resolve_indications(indications)
        params = {
            "name": name,
            "description": description,
            "label": label,
            "includesHealthySubjects": healthy,
            "plannedEnrollmentNumber": enrollment_number,
            "plannedCompletionNumber": completion_number,
            "plannedAge": planned_age,
            "plannedSex": codes,
            "characteristics": characteristic_refs,
            "indicationIds": [indication.id for indication in indication_refs],
        }
        item = self._create(StudyCohort, params)
        if item:
            self._cohorts.append(item)
        return item

    def _resolve_characteristics(self, names):
        results = []
        for name in names:
            object = self._builder.cross_reference.get_by_name(Characteristic, name)
            if object:
                results.append(object)
            else:
                self._errors.warning(f"Characteristic '{name}' not found")
        return results

    def _resolve_indications(self, names):
        results = []
        for name in names:
            object = self._builder.cross_reference.get_by_name(Indication, name)
            if object:
                results.append(object)
            else:
                self._errors.warning(f"Indication '{name}' not found")
        return results

    def _read_range_quantity(self, index, field_name):
        text = self._read_cell_by_name(index, field_name)
        return (
            self._read_range_cell_by_name(
                index, field_name, require_units=False, allow_empty=True
            )
            if ".." in text
            else self._read_quantity_cell_by_name(
                index, field_name, allow_missing_units=True, allow_empty=True
            )
        )
