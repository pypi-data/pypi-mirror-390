from usdm4.api.study import Study
from usdm4.api.study_version import StudyVersion
from usdm4.api.study_design import StudyDesign
from usdm4.api.schedule_timeline import ScheduleTimeline
from usdm4.api.scheduled_instance import (
    ScheduledActivityInstance,
    ScheduledDecisionInstance,
)
from usdm4_excel.export.base.collection_panel import CollectionPanel


class HeadingsPanel(CollectionPanel):
    def execute(self, study: Study) -> list[list[dict]]:
        collection = [
            ["name"],
            ["description"],
            ["label"],
            ["type"],
            ["default"],
            ["condition"],
            ["epoch"],
            ["encounter"],
        ]
        version: StudyVersion = study.versions[0]
        design: StudyDesign = version.studyDesigns[0]
        timeline: ScheduleTimeline = design.main_timeline()
        if timeline:
            for timepoint in timeline.timepoint_list():
                self._add_instance(collection, timepoint, design, timeline)
        return collection

    def _add_instance(
        self,
        collection: list,
        item: ScheduledActivityInstance | ScheduledDecisionInstance,
        study_design: StudyDesign,
        timeline: ScheduleTimeline,
    ):
        data = item.model_dump()
        data["type"] = (
            "Activity"
            if item.instanceType == "ScheduledActivityInstance"
            else "Decision"
        )
        default = timeline.find_timepoint(item.defaultConditionId)
        data["default"] = default.name if default else ""
        data["condition"] = ""  # @todo Not needed in this release
        epoch = study_design.find_epoch(item.epochId)
        data["epoch"] = epoch.name if epoch else ""
        encounter = study_design.find_encounter(item.encounterId)
        data["encounter"] = encounter.name if encounter else ""
        for k, v in data.items():
            for row in collection:
                if row[0] == k:
                    row.append(v)
