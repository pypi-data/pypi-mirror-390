from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4.builder.builder import Builder
from usdm4.api.study_epoch import StudyEpoch
from usdm4.api.study_arm import StudyArm
from usdm4.api.study_element import StudyElement
from usdm4.api.study_cell import StudyCell
from usdm4.api.study_design import (
    ObservationalStudyDesign,
    InterventionalStudyDesign,
)
from usdm4.api.biospecimen_retention import BiospecimenRetention
from usdm4.api.population_definition import StudyDesignPopulation


class StudyDesignSheet(BaseSheet):
    MODULE = "usdm4_excel.import_.study_design.study_design_sheet.StudyDesignSheet"
    SHEET_NAME = "studyDesign"

    NAME_KEY = ["studyDesignName", "name"]
    DESCRIPTION_KEY = ["studyDesignDescription", "description"]
    LABEL_KEY = ["label"]
    TA_KEY = ["therapeuticAreas"]
    RATIONALE_KEY = ["studyDesignRationale"]
    BLINDING_KEY = ["studyDesignBlindingScheme"]
    INTENT_KEY = ["trialIntentTypes"]
    SUB_TYPES_KEY = ["trialSubTypes"]
    MODEL_KEY = ["interventionModel", "model"]
    MAIN_TIMELINE_KEY = ["mainTimeline"]
    OTHER_TIMELINES_KEY = ["otherTimelines"]
    MASKING_ROLE_KEY = ["masking"]
    PHASE_KEY = ["studyDesignPhase", "studyPhase"]
    STUDY_TYPE_KEY = ["studyDesignType", "studyType"]
    SPECIMEN_RETENTION_KEY = ["specimenRetentions"]
    TIME_PERSPECTIVE_KEY = ["timePerspective"]
    SAMPLING_METHOD_KEY = ["samplingMethod"]
    CHARACTERISTICS_KEY = ["characteristics"]

    PARAMS_NAME_COL = 0
    PARAMS_DATA_COL = 1

    def __init__(self, file_path: str, builder: Builder, errors: Errors):
        try:
            self._interventional = True
            self._name = "TEST"
            self._description = "USDM Example Study Design"
            self._label = "USDM Example Study Design"
            self._epochs = []
            self._epoch_names = {}
            self._arms = []
            self._arm_names = {}
            self._cells = []
            self._elements = {}
            self._therapeutic_areas = []
            self._rationale = ""
            self._blinding = None
            self._trial_intents = []
            self._study_type = None
            self._int_sub_types = []
            self._obs_sub_types = []
            self._intervention_model = None
            self._main_timeline = None
            self._other_timelines = []
            self._masks = []
            self._phase = None
            self._specimen_retentions = []
            self._time_perspective = None
            self._sampling_methods = []
            self._characteristics = []
            self._study_design = None
            super().__init__(
                file_path=file_path,
                builder=builder,
                errors=errors,
                sheet_name=self.SHEET_NAME,
                header=None,
                optional=True,
            )
            if self._success:
                self._process_sheet()
        except Exception as e:
            self._sheet_exception(e)

    @property
    def study_design(self):
        print(f"STUDY DESIGN: {self._study_design}")
        return self._study_design

    def _process_sheet(self):
        general_params = True
        resolved_epochs = [None] * self._sheet.shape[1]
        resolved_arms = [None] * self._sheet.shape[0]
        for rindex, row in self._sheet.iterrows():
            key = self._read_cell(rindex, self.PARAMS_NAME_COL)
            if general_params:
                if key in self.NAME_KEY:
                    self._name = self._read_cell(rindex, self.PARAMS_DATA_COL)
                elif key in self.LABEL_KEY:
                    self._label = self._read_cell(rindex, self.PARAMS_DATA_COL)
                elif key in self.DESCRIPTION_KEY:
                    self._description = self._read_cell(rindex, self.PARAMS_DATA_COL)
                elif key in self.TA_KEY:
                    self._therapeutic_areas = self._read_other_code_cell_multiple(
                        rindex, self.PARAMS_DATA_COL
                    )
                elif key in self.RATIONALE_KEY:
                    self._rationale = self._read_cell(rindex, self.PARAMS_DATA_COL)
                elif key in self.BLINDING_KEY:
                    blinding = self._read_cdisc_klass_attribute_cell(
                        "InterventionalStudyDesign",
                        "blindingSchema",
                        rindex,
                        self.PARAMS_DATA_COL,
                    )
                    self._blinding = self._builder.alias_code(blinding)
                elif key in self.INTENT_KEY:
                    self._trial_intents = (
                        self._read_cdisc_klass_attribute_cell_multiple(
                            "InterventionalStudyDesign",
                            "intentTypes",
                            rindex,
                            self.PARAMS_DATA_COL,
                        )
                    )
                elif key in self.STUDY_TYPE_KEY:
                    self._study_type = self._read_cdisc_klass_attribute_cell(
                        "StudyDesign", "studyType", rindex, self.PARAMS_DATA_COL
                    )
                    if self._study_type.code == "C16084":
                        self._interventional = False
                elif key in self.SUB_TYPES_KEY:
                    self._int_sub_types = (
                        self._read_cdisc_klass_attribute_cell_multiple(
                            "InterventionalStudyDesign",
                            "subTypes",
                            rindex,
                            self.PARAMS_DATA_COL,
                        )
                    )
                    self._obs_sub_types = (
                        self._read_cdisc_klass_attribute_cell_multiple(
                            "ObservationallStudyDesign",
                            "subTypes",
                            rindex,
                            self.PARAMS_DATA_COL,
                        )
                    )
                elif key in self.MODEL_KEY:
                    self._intervention_model = self._read_cdisc_klass_attribute_cell(
                        "StudyDesign", "interventionModel", rindex, self.PARAMS_DATA_COL
                    )
                elif key in self.MAIN_TIMELINE_KEY:
                    self._main_timeline = self._read_cell(rindex, self.PARAMS_DATA_COL)
                elif key in self.OTHER_TIMELINES_KEY:
                    self._other_timelines = self._read_cell_multiple(
                        rindex, self.PARAMS_DATA_COL
                    )
                elif key in self.MASKING_ROLE_KEY:
                    self._errors.warning(
                        rindex,
                        self.PARAMS_NAME_COL,
                        "Masking has been moved to the 'roles' sheet, value ignored",
                    )
                    # self._set_masking(rindex, self.PARAMS_DATA_COL)
                elif key in self.PHASE_KEY:
                    phase = self._read_cdisc_klass_attribute_cell(
                        "StudyDesign", "studyPhase", rindex, self.PARAMS_DATA_COL
                    )
                    self._phase = self._builder.alias_code(phase)
                elif key in self.SPECIMEN_RETENTION_KEY:
                    specimen_refs = self._read_cell_multiple(
                        rindex, self.PARAMS_DATA_COL
                    )
                    for ref in specimen_refs:
                        specimen = self._builder.cross_reference.get_by_name(
                            BiospecimenRetention, ref
                        )
                        if specimen is not None:
                            self._specimen_retentions.append(specimen)
                elif key in self.TIME_PERSPECTIVE_KEY:
                    self._time_perspective = self._read_cdisc_klass_attribute_cell(
                        "StudyDesign", "timePerspective", rindex, self.PARAMS_DATA_COL
                    )
                elif key in self.SAMPLING_METHOD_KEY:
                    self._sampling_methods = self._read_cdisc_klass_attribute_cell(
                        "StudyDesign", "samplingMethod", rindex, self.PARAMS_DATA_COL
                    )
                elif key in self.CHARACTERISTICS_KEY:
                    self._characteristics = (
                        self._read_cdisc_klass_attribute_cell_multiple(
                            "StudyDesign",
                            "characteristics",
                            rindex,
                            self.PARAMS_DATA_COL,
                        )
                    )
                elif key == "":
                    general_params = False
                    start_row = rindex + 1
                else:
                    self._errors.warning(
                        f"Unrecognized key '{key}', ignored",
                        self._location(rindex, self.PARAMS_NAME_COL),
                    )
            else:
                for cindex in range(0, len(self._sheet.columns)):
                    epoch_index = cindex - 1
                    cell = self._read_cell(rindex, cindex)
                    # print(f"ARMS EPOCHS: {rindex} = {cell}")
                    if rindex == start_row:
                        if cindex != 0:
                            resolved_epochs[epoch_index] = self._add_epoch(cell)
                    else:
                        arm_index = rindex - start_row - 1
                        if cindex == 0:
                            resolved_arms[arm_index] = self._add_arm(cell)
                        else:
                            cell_elements = []
                            element_names = self._read_cell_multiple(rindex, cindex)
                            for name in element_names:
                                element = self._add_element(name)
                                if element is not None:
                                    cell_elements.append(element.id)
                            cell_arm = resolved_arms[arm_index].id
                            cell_epoch = resolved_epochs[epoch_index].id
                            if cell_arm is not None and cell_epoch is not None:
                                self._cells.append(
                                    self._add_cell(
                                        arm=cell_arm,
                                        epoch=cell_epoch,
                                        elements=cell_elements,
                                    )
                                )
                            else:
                                self._errors.error(
                                    f"Cannot resolve arm and/or epoch for cell [{arm_index + 1},{epoch_index + 1}]",
                                    self._location(rindex, cindex),
                                )

            self._double_link(self._epochs, "previousId", "nextId")
        self._study_design = self._create_design()

    def _add_arm(self, name):
        arm = self._builder.cross_reference.get_by_name(StudyArm, name)
        if arm is not None:
            if name not in self._arm_names:
                self._arm_names[name] = True
                self._arms.append(arm)
            return arm
        else:
            self._errors.error(
                f"No arm definition found for arm '{name}'",
                KlassMethodLocation(self.MODULE, "_add_arm"),
            )
            return None

    def _add_epoch(self, name):
        epoch = self._builder.cross_reference.get_by_name(StudyEpoch, name)
        if epoch is not None:
            if name not in self._epoch_names:
                self._epoch_names[name] = True
                self._epochs.append(epoch)
            return epoch
        else:
            self._errors.error(
                f"No epoch definition found for epoch '{name}'",
                KlassMethodLocation(self.MODULE, "_add_epoch"),
            )
            return None

    def _add_element(self, name):
        element = self._builder.cross_reference.get_by_name(StudyElement, name)
        if element is not None:
            if name not in self._elements:
                self._elements[name] = element
            return element
        else:
            self._errors.error(
                f"No element definition found for element '{name}'",
                KlassMethodLocation(self.MODULE, "_add_element"),
            )
            return None

    def _add_cell(self, arm, epoch, elements):
        try:
            return self._create(
                StudyCell,
                {
                    "armId": arm,
                    "epochId": epoch,
                    "elementIds": elements,
                },
            )
        except Exception as e:
            self._errors.exception(
                "Exception raised creat StudyCell object",
                e,
                KlassMethodLocation(self.MODULE, "_add_cell"),
            )
            return None

    def _create_design(self):
        try:
            dummy_population = self._builder.create(
                StudyDesignPopulation,
                {
                    "id": "DummyPopulationId",
                    "name": "Dummy Population",
                    "includesHealthySubjects": True,
                },
            )
            if self._interventional:
                result = self._builder.create(
                    InterventionalStudyDesign,
                    {
                        "name": self._name,
                        "description": self._description,
                        "label": self._label,
                        "intentTypes": self._trial_intents,
                        "studyType": self._study_type,
                        "studyPhase": self._phase,
                        "subTypes": self._int_sub_types,
                        "model": self._intervention_model,
                        "studyCells": self._cells,
                        "arms": self._arms,
                        "epochs": self._epochs,
                        "elements": list(self._elements.values()),
                        "therapeuticAreas": self._therapeutic_areas,
                        "rationale": self._rationale,
                        "blindingSchema": self._blinding,
                        "biospecimenRetentions": self._specimen_retentions,
                        "characteristics": self._characteristics,
                        "population": dummy_population,
                    },
                )
            else:
                result = self._builder.create(
                    ObservationalStudyDesign,
                    {
                        "name": self._name,
                        "description": self._description,
                        "label": self._label,
                        "studyType": self._study_type,
                        "studyPhase": self._phase,
                        "subTypes": self._obs_sub_types,
                        "model": self._intervention_model,
                        "timePerspective": self._time_perspective,
                        "samplingMethod": self._sampling_methods,
                        "studyCells": self._cells,
                        "arms": self._arms,
                        "epochs": self._epochs,
                        "elements": list(self._elements.values()),
                        "therapeuticAreas": self._therapeutic_areas,
                        "rationale": self._rationale,
                        "biospecimenRetentions": self._specimen_retentions,
                        "characteristics": self._characteristics,
                        "population": dummy_population,
                    },
                )
            return result
        except Exception as e:
            self._errors.exception(
                "Exception raised creating StudyDesign object",
                e,
                KlassMethodLocation(self.MODULE, "_create_design"),
            )
            return None
