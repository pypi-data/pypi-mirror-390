from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4_excel.import_.study_design.soa.scheduled_instances import ScheduledInstances

from usdm4.api.timing import Timing
from usdm4.api.scheduled_instance import (
    ScheduledInstance as USDMScheduledInstance,
    ScheduledActivityInstance,
)
from usdm4.api.duration import Duration
from usdm4.api.schedule_timeline import ScheduleTimeline
from usdm4_excel.import_.study_design.soa.soa_activities import SoAActivities


class SoASheet(BaseSheet):
    NAME_ROW = 0
    DESCRIPTION_ROW = 1
    CONDITION_ROW = 2
    DURATION_ROW = 3
    DURATION_REASON_ROW = 4
    DURATION_DESCRIPTION_ROW = 5
    PARAMS_DATA_COL = 1

    def __init__(
        self, file_path: str, builder: Builder, errors: Errors, sheet_name: str, main
    ):
        print(f"SOA SHEET: {sheet_name}")
        try:
            self.name = ""
            self.description = ""
            self.condition = ""
            self.duration = None
            self.duration_reason = ""
            self.duration_text = ""
            self.timeline = None
            self.main_timeline = main
            self._activities = []
            self._raw_activities = None
            self._raw_instances = None
            self.biomedical_concepts = []
            self.biomedical_concept_surrogates = []
            print("SOA SHEET2:")
            super().__init__(
                file_path=file_path,
                builder=builder,
                errors=errors,
                sheet_name=sheet_name,
                header=None,
                optional=True,
            )
            if self._success:
                print("SOA SHEET3:")
                self._process_sheet()
                # Order important, activities then instances
                self._raw_activities = SoAActivities(self)
                self._raw_instances = ScheduledInstances(self)
                (
                    self._activities,
                    self.biomedical_concepts,
                    self.biomedical_concept_surrogates,
                ) = self._raw_activities.group_and_link()
                self._raw_activities.set_parents()
                self.timeline = self._add_timeline(
                    self.name,
                    self.description,
                    self.condition,
                    self._raw_instances.instances,
                    self._raw_instances.exits,
                )
        except Exception as e:
            self._sheet_exception(e)

    @property
    def activities(self) -> list[USDMScheduledInstance]:
        return self._activities

    def check_timing_references(self, timings, timing_check):
        timing_set = []
        for instance in self._raw_instances.items:
            item = instance.item
            if isinstance(item, ScheduledActivityInstance):
                found = False
                timing: Timing
                for timing in timings:
                    ids = [
                        timing.relativeFromScheduledInstanceId,
                        timing.relativeToScheduledInstanceId,
                    ]
                    # print(f"TIMING2: {timing.name}, {ids}")
                    if item.id in ids:
                        # print(f"TIMING3: found")
                        found = True
                        if not timing_check[timing.name]:
                            timing_check[timing.name] = self.name
                            timing_set.append(timing)
                        elif timing_check[timing.name] == self.name:
                            pass
                        else:
                            self._errors.warning(
                                f"Duplicate use of timing with name '{timing.name}' across timelines detected"
                            )
                        # break
                if not found:
                    self._errors.warning(
                        f"Unable to find timing reference for instance with name '{instance.name}'"
                    )
        return timing_set

    def timing_match(self, ref):
        return self._raw_instances.match(ref)

    def _process_sheet(self):
        for rindex in range(self.NAME_ROW, self.DURATION_DESCRIPTION_ROW + 1):
            if rindex == self.NAME_ROW:
                self.name = self._read_cell(rindex, self.PARAMS_DATA_COL)
            elif rindex == self.DESCRIPTION_ROW:
                self.description = self._read_cell(rindex, self.PARAMS_DATA_COL)
            elif rindex == self.CONDITION_ROW:
                self.condition = self._read_cell(rindex, self.PARAMS_DATA_COL)
            elif rindex == self.DURATION_ROW:
                self.duration = self._read_quantity_cell(rindex, self.PARAMS_DATA_COL)
            elif rindex == self.DURATION_REASON_ROW:
                self.duration_reason = self._read_cell(
                    rindex, self.PARAMS_DATA_COL, default=""
                )
            elif rindex == self.DURATION_DESCRIPTION_ROW:
                self.duration_text = self._read_cell(
                    rindex, self.PARAMS_DATA_COL, default=""
                )
            else:
                pass

    def _add_timeline(self, name, description, condition, instances, exit):
        duration = (
            self._builder.create(
                Duration,
                {
                    "text": self.duration_text,
                    "quantity": self.duration,
                    "durationWillVary": True if self.duration_reason else False,
                    "reasonDurationWillVary": self.duration_reason,
                },
            )
            if self.duration
            else None
        )
        return self._builder.create(
            ScheduleTimeline,
            {
                "mainTimeline": self.main_timeline,
                "name": name,
                "description": description,
                "label": name,
                "entryCondition": condition,
                "entryId": instances[0].id,
                "exits": exit,
                "plannedDuration": duration,
                "instances": instances,
            },
        )
