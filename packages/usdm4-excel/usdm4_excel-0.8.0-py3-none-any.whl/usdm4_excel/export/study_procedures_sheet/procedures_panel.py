from usdm4.api.study import Study
from usdm4.api.procedure import Procedure
from usdm4_excel.export.base.collection_panel import CollectionPanel


class ProceduresPanel(CollectionPanel):
    def execute(self, study: Study) -> list[list[dict]]:
        collection = []
        for version in study.versions:
            for design in version.studyDesigns:
                for activity in design.activities:
                    for item in activity.definedProcedures:
                        self._add_procedure(collection, item)
        return super().execute(
            collection,
            ["name", "description", "label", "procedureType", "procedureCode"],
        )

    def _add_procedure(self, collection: list, item: Procedure):
        data = item.model_dump()
        data["procedureCode"] = self._external_code(item.code)
        self.ct_version.add(item.code.codeSystem, item.code.codeSystemVersion)
        collection.append(data)
