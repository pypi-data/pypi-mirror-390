from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder

from usdm4.api.study_design import StudyDesign
from usdm4.api.biomedical_concept import BiomedicalConcept
from usdm4.api.biomedical_concept_surrogate import BiomedicalConceptSurrogate

from usdm4_excel.import_.study_design.soa_sheet import SoASheet
from usdm4_excel.import_.study_design.timing_sheet import TimingSheet
from usdm4_excel.import_.study_design.activities_sheet import ActivitiesSheet
from usdm4_excel.import_.study_design.arms_sheet import ArmsSheet
from usdm4_excel.import_.study_design.elements_sheet import ElementsSheet
from usdm4_excel.import_.study_design.epochs_sheet import EpochsSheet
from usdm4_excel.import_.study_design.encounters_sheet import EncountersSheet
from usdm4_excel.import_.study_design.study_design_sheet import StudyDesignSheet
from usdm4_excel.import_.study_design.actions.timing_references import (
    set_timing_references,
    check_timing_references,
)


class StudyDesignAction:
    def __init__(self, builder: Builder, errors: Errors):
        self._builder = builder
        self._errors = errors
        self._timing_sheet = None
        self._soa_sheets = []
        self._biomedical_concepts = []
        self._biomedical_concept_surrogates = []

    @property
    def biomedical_concepts(self) -> list[BiomedicalConcept]:
        return self._biomedical_concepts

    @property
    def biomedical_concept_surrogates(self) -> list[BiomedicalConceptSurrogate]:
        return self._biomedical_concept_surrogates

    def seed(self, file_path: str) -> None:
        self._builder.seed(file_path)

    def process(
        self,
        file_path: str,
    ) -> StudyDesign:
        self._activities_sheet: ActivitiesSheet = ActivitiesSheet(
            file_path, self._builder, self._errors
        )
        self._arms_sheet: ArmsSheet = ArmsSheet(file_path, self._builder, self._errors)
        self._epochs_sheet: EpochsSheet = EpochsSheet(
            file_path, self._builder, self._errors
        )
        self._elements_sheet: ElementsSheet = ElementsSheet(
            file_path, self._builder, self._errors
        )
        self._encounters_sheet: EncountersSheet = EncountersSheet(
            file_path, self._builder, self._errors
        )
        self._timing_sheet: TimingSheet = TimingSheet(
            file_path, self._builder, self._errors
        )
        self._study_design_sheet: StudyDesignSheet = StudyDesignSheet(
            file_path, self._builder, self._errors
        )
        study_design: StudyDesign = self._study_design_sheet.study_design
        if study_design:
            timelines = [
                {"main": True, "sheet_name": self._study_design_sheet._main_timeline}
            ] + [
                {"main": False, "sheet_name": x}
                for x in self._study_design_sheet._other_timelines
            ]
            for timeline in timelines:
                sheet: SoASheet = SoASheet(
                    file_path,
                    self._builder,
                    self._errors,
                    timeline["sheet_name"],
                    timeline["main"],
                )
                self._soa_sheets.append(sheet)
            set_timing_references(self._soa_sheets, self._timing_sheet, self._errors)
            check_timing_references(self._soa_sheets, self._timing_sheet, self._errors)

            activities = []
            activity_ids = []
            soa_sheet: SoASheet
            for soa_sheet in self._soa_sheets:
                study_design.scheduleTimelines.append(soa_sheet.timeline)
                for activity in soa_sheet.activities:
                    if activity.id not in activity_ids:
                        activities.append(activity)
                        activity_ids.append(activity.id)
                self._biomedical_concepts += soa_sheet.biomedical_concepts
                self._biomedical_concept_surrogates += (
                    soa_sheet.biomedical_concept_surrogates
                )
            study_design.activities = activities
            study_design.encounters = self._encounters_sheet.items
            # self._builder._double_link(study_design.activities, "previousId", "nextId")
        return study_design
