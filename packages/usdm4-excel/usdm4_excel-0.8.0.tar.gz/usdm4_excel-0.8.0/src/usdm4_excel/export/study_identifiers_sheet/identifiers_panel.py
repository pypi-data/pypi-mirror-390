from usdm4.api.study import Study
from usdm4.api.identifier import StudyIdentifier
from usdm4.api.study_version import StudyVersion
from usdm4_excel.export.base.collection_panel import CollectionPanel


class IdentifiersPanel(CollectionPanel):
    def execute(self, study: Study) -> list[list[dict]]:
        collection = []
        for version in study.versions:
            for item in version.studyIdentifiers:
                self._add_identifier(collection, item, version)
        return super().execute(
            collection,
            ["studyIdentifier", "organization"],
        )

    def _add_identifier(
        self, collection: list, item: StudyIdentifier, version: StudyVersion
    ):
        data = {}
        org = version.organization(item.scopeId)
        data["studyIdentifier"] = item.text
        data["organization"] = org.name
        collection.append(data)
