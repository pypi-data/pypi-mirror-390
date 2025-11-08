from usdm4.api.study import Study
from usdm4.api.study_epoch import StudyEpoch
from usdm4_excel.export.base.collection_panel import CollectionPanel


class EpochsPanel(CollectionPanel):
    def execute(self, study: Study) -> list[list[dict]]:
        collection = []
        for version in study.versions:
            for design in version.studyDesigns:
                for item in design.epochs:
                    self._add_activity(collection, item)
        return super().execute(
            collection,
            ["name", "description", "label", "type"],
        )

    def _add_activity(self, collection: list, item: StudyEpoch):
        data = item.model_dump()
        data["type"] = self._pt_from_code(item.type)
        collection.append(data)
