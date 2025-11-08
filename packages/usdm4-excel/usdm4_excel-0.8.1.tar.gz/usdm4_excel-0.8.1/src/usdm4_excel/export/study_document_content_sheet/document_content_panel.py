from usdm4.api.study import Study
from usdm4.api.narrative_content import NarrativeContentItem
from usdm4_excel.export.base.collection_panel import CollectionPanel


class DocumentContentPanel(CollectionPanel):
    def execute(self, study: Study) -> list[list[dict]]:
        collection = []
        for version in study.versions:
            for nci in version.narrativeContentItems:
                self._add_content_item(collection, nci)
        return super().execute(
            collection,
            ["name", "text"],
        )

    def _add_content_item(self, collection: list, item: NarrativeContentItem):
        data = item.model_dump()
        collection.append(data)
