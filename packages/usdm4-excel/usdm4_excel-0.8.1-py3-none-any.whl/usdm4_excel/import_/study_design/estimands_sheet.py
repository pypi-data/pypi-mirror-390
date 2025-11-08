from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.intercurrent_event import IntercurrentEvent
from usdm4.api.analysis_population import AnalysisPopulation
from usdm4.api.estimand import Estimand
from usdm4.api.study_intervention import StudyIntervention
from usdm4.api.endpoint import Endpoint
from usdm4.api.population_definition import StudyDesignPopulation, StudyCohort


class EstimandsSheet(BaseSheet):
    SHEET_NAME = "studyDesignEstimands"

    def __init__(self, file_path: str, builder: Builder, errors: Errors):
        try:
            self._items = []
            self._populations = []
            super().__init__(
                file_path=file_path,
                builder=builder,
                errors=errors,
                sheet_name=self.SHEET_NAME,
                optional=True,
            )
            if self._success:
                current = None
                current_ice_name = None
                current_ice_description = None
                for index, row in self._sheet.iterrows():
                    e_name = self._read_cell_by_name(index, ["name", "xref"])
                    e_summary = self._read_cell_by_name(index, "summaryMeasure")
                    ap_description = self._read_cell_by_name(
                        index, "populationDescription"
                    )
                    ap_subset = self._read_cell_by_name(index, "populationSubset")
                    ice_name = self._read_cell_by_name(index, ["intercurrentEventName"])
                    ice_description = self._read_cell_by_name(
                        index, ["intercurrentEventDescription", "description"]
                    )
                    ice_label = self._read_cell_by_name(
                        index, "label", must_be_present=False
                    )
                    ice_strategy = self._read_cell_by_name(
                        index, "intercurrentEventStrategy"
                    )
                    ice_text = self._read_cell_by_name(index, "intercurrentEventText")
                    treatment_xref = self._read_cell_by_name(index, "treatmentXref")
                    endpoint_xref = self._read_cell_by_name(index, "endpointXref")
                    if not e_summary == "":
                        population = self._get_population(ap_subset)
                        if population:
                            ap = self._create(
                                AnalysisPopulation,
                                {
                                    "name": f"AP_{index + 1}",
                                    "text": ap_description,
                                    "subsetOfIds": [population.id],
                                },
                            )
                            if ap:
                                self._populations.append(ap)
                                params = {
                                    "name": e_name,
                                    "description": "",
                                    "label": e_name,
                                    "populationSummary": e_summary,
                                    "analysisPopulationId": ap.id,
                                    "interventionIds": [
                                        self._get_treatment_id(treatment_xref)
                                    ],
                                    "variableOfInterestId": self._get_endpoint_id(
                                        endpoint_xref
                                    ),
                                    "intercurrentEvents": [],
                                }
                                print(f"PARAMS: {params}")
                                current = self._create(Estimand, params)
                                if current:
                                    self._items.append(current)
                    if current is not None:
                        ice_name = current_ice_name if ice_name == "" else ice_name
                        ice_description = (
                            current_ice_description
                            if ice_description == ""
                            else ice_description
                        )
                        ice = self._create(
                            IntercurrentEvent,
                            {
                                "name": ice_name,
                                "description": ice_description,
                                "label": ice_label,
                                "strategy": ice_strategy,
                                "text": ice_text,
                            },
                        )
                        current_ice_name = ice_name
                        current_ice_description = ice_description
                        if ice:
                            current.intercurrentEvents.append(ice)
                    else:
                        self._errors.error(
                            "Failed to add IntercurrentEvent, no Estimand set"
                        )
        except Exception as e:
            self._sheet_exception(e)

    @property
    def items(self):
        return self._items

    @property
    def populations(self):
        return self._populations

    def _get_treatment_id(self, name):
        result = self._get_cross_reference(StudyIntervention, name)
        return result.id if result else None

    def _get_endpoint_id(self, name):
        result = self._get_cross_reference(Endpoint, name)
        return result.id if result else None

    def _get_population(self, name):
        return self._get_cross_reference([StudyDesignPopulation, StudyCohort], name)
