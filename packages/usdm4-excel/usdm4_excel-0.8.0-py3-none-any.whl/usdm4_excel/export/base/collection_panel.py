from .base_panel import BasePanel
from usdm4.api.geographic_scope import GeographicScope
from datetime import date


class CollectionPanel(BasePanel):
    def execute(self, collection: list, columns: list[str]) -> list[list[dict]]:
        result = []
        result.append(columns)
        for item in collection:
            filtered_data = [item[k] for k in columns]
            result.append(filtered_data)
        return result

    def _date_from_date(self, date: date):
        return date.strftime("%d/%m/%Y")

    def _scopes(self, scopes: list[GeographicScope]):
        items = []
        for scope in scopes:
            if scope.type.decode == "Global":
                items.append(scope.type.decode)
            else:
                items.append(f"{scope.type.decode}: {scope.code.standardCode.decode}")
        return (", ").join(items)
