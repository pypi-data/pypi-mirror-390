from usdm4.api.study import Study
from usdm4.api.activity import Activity
from usdm4_excel.export.base.collection_panel import CollectionPanel


class ActivitiesPanel(CollectionPanel):
    def execute(self, study: Study) -> list[list[dict]]:
        collection = []
        for version in study.versions:
            for design in version.studyDesigns:
                for item in design.activities:
                    self._add_activity(collection, item)
        return super().execute(
            collection,
            ["name", "label", "description"],
        )

    def _add_activity(self, collection: list, item: Activity):
        data = item.model_dump()
        collection.append(data)
