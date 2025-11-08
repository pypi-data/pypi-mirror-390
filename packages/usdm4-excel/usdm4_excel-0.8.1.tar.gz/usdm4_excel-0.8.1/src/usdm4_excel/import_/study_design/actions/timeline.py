from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.schedule_timeline import ScheduleTimeline
from usdm4_excel.import_.study_design.soa_sheet import SoASheet
from usdm4_excel.import_.study_design.timing_sheet import TimingSheet
from usdm4_excel.import_.study_design.actions.timing_references import (
    set_timing_references,
    check_timing_references,
)


class TimelineAction:
    def __init__(self, builder: Builder, errors: Errors):
        self._builder = builder
        self._errors = errors
        self._timing = None
        self._soa = None

    def seed(self, file_path: str) -> None:
        self._builder.seed(file_path)

    def process(
        self,
        file_path: str,
    ) -> ScheduleTimeline:
        self._timing = TimingSheet(file_path, self._builder, self._errors)
        self._soa = SoASheet(file_path, self._builder, self._errors, "timeline", False)
        set_timing_references([self._soa], self._timing, self._errors)
        check_timing_references([self._soa], self._timing, self._errors)
        return self._soa.timeline
