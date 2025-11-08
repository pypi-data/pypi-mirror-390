from usdm4.api.study import Study
from usdm4.api.study_version import StudyVersion
from usdm4.api.study_design import StudyDesign
from usdm4.api.schedule_timeline import ScheduleTimeline
from usdm4_excel.export.base.base_panel import BasePanel


class MainPanel(BasePanel):
    def execute(self, study: Study) -> list[list[dict]]:
        result = []
        version: StudyVersion = study.versions[0]
        design: StudyDesign = version.studyDesigns[0]
        timeline: ScheduleTimeline = design.main_timeline()
        result.append(["Name", timeline.name if timeline else ""])
        result.append(["Description", timeline.description if timeline else ""])
        result.append(["Condition", timeline.entryCondition if timeline else ""])
        return result
