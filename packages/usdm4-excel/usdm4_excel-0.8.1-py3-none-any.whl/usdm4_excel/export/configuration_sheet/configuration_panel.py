from usdm4.api.study import Study
from usdm4_excel.export.base.collection_panel import CollectionPanel


class ConfigurationPanel(CollectionPanel):
    def execute(self, study: Study) -> list[list[dict]]:
        result = []
        for name, version in self.ct_version.versions.items():
            result.append(["CT Version", f"{name}={version}"])
        return result
