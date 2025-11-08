from usdm4.api.study import Study
from usdm4.api.study_design import StudyDesign
from usdm4.api.encounter import Encounter
from usdm4.api.timing import Timing
from usdm4.api.schedule_timeline import ScheduleTimeline
from usdm4_excel.export.base.collection_panel import CollectionPanel


class EncountersPanel(CollectionPanel):
    def execute(self, study: Study) -> list[list[dict]]:
        collection = []
        for version in study.versions:
            for design in version.studyDesigns:
                for item in design.encounters:
                    self._add_encounter(collection, item, design)
        return super().execute(
            collection,
            [
                "name",
                "description",
                "label",
                "type",
                "environmentalSetting",
                "contactModes",
                "transitionStartRule",
                "transitionEndRule",
                "window",
            ],
        )

    def _add_encounter(self, collection: list, item: Encounter, design: StudyDesign):
        data = item.model_dump()
        data["type"] = self._pt_from_code(item.type)
        data["environmentalSetting"] = (", ").join(
            [self._pt_from_code(x) for x in item.environmentalSettings]
        )
        data["contactModes"] = (", ").join(
            [self._pt_from_code(x) for x in item.contactModes]
        )
        timing = self._find_timeing_in_design(design, item.scheduledAtId)
        data["window"] = timing.windowLabel if timing else ""
        collection.append(data)

    def _find_timeing_in_design(self, design: StudyDesign, id: str) -> Timing | None:
        for timeline in design.scheduleTimelines:
            if timing := self.find_timing(timeline, id):
                return timing
        return None

    def find_timing(self, timeline: ScheduleTimeline, id: str) -> Timing | None:
        return next((x for x in timeline.timings if x.id == id), None)
