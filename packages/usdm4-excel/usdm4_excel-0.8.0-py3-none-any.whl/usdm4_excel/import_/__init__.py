from usdm4 import USDM4
from usdm4.api.wrapper import Wrapper
from usdm4.api.study import Study
from usdm4.api.schedule_timeline import ScheduleTimeline
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4.builder.builder import Builder
from usdm4_excel.import_.study_design.actions.timeline import TimelineAction
from usdm4_excel.import_.study.actions.study import StudyAction
from usdm4_excel.__info__ import (
    __model_version__ as usdm_version,
    __package_version__ as system_version,
    __package_name__ as system_name,
)


class USDM4ExcelImport:
    MODULE = "usdm4_excel.import_.__init__.USDM4ExcelImport"

    def __init__(self):
        self._usdm: USDM4 = USDM4()
        self._errors: Errors = Errors()
        self._builder: Builder = self._usdm.builder(self._errors)

    def timeline(
        self, timeline_file_path: str, usdm_file_path: str
    ) -> ScheduleTimeline:
        try:
            action = TimelineAction(self._builder, self._errors)
            action.seed(usdm_file_path)
            return action.process(timeline_file_path)
        except Exception as e:
            self._errors.exception(
                f"Exception raised building timeline from file '{timeline_file_path}'",
                e,
                KlassMethodLocation(self.MODULE, "timeline"),
            )

    def from_excel(self, file_path: str) -> Wrapper:
        try:
            action = StudyAction(self._builder, self._errors)
            study: Study = action.process(file_path)
            return Wrapper(
                study=study,
                usdmVersion=usdm_version,
                systemName=system_name,
                systemVersion=system_version,
            )
        except Exception as e:
            self._errors.exception(
                f"Exception raised building USDM from file '{file_path}'",
                e,
                KlassMethodLocation(self.MODULE, "from_excel"),
            )

    @property
    def errors(self):
        return self._errors
