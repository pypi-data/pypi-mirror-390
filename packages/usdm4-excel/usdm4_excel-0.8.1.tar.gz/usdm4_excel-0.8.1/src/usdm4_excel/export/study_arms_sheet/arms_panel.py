from usdm4.api.study import Study
from usdm4.api.study_arm import StudyArm
from usdm4_excel.export.base.collection_panel import CollectionPanel


class ArmsPanel(CollectionPanel):
    def execute(self, study: Study) -> list[list[dict]]:
        collection = []
        for version in study.versions:
            for design in version.studyDesigns:
                for item in design.arms:
                    self._add_arm(collection, item)
        if len(collection) == 0:
            collection.append(self._default_arm())
        return super().execute(
            collection,
            [
                "name",
                "description",
                "label",
                "type",
                "dataOriginDescription",
                "dataOriginType",
            ],
        )

    def _add_arm(self, collection: list, item: StudyArm):
        data = item.model_dump()
        data["type"] = self._pt_from_code(item.type)
        data["dataOriginType"] = self._pt_from_code(item.dataOriginType)
        collection.append(data)

    def _default_arm(self) -> dict:
        return {
            "name": "DEFAULT_ARM",
            "description": "Default arm",
            "label": "Default Arm",
            "type": "Active Comparator Arm",
            "dataOriginDescription": "Data collected from subjects",
            "dataOriginType": "Data Generated Within Study",
        }
