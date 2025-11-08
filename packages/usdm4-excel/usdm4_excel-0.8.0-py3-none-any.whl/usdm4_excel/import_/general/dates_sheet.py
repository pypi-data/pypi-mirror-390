from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.governance_date import GovernanceDate


class DatesSheet(BaseSheet):
    SHEET_NAME = "dates"

    def __init__(self, file_path: str, builder: Builder, errors: Errors):
        try:
            self._items = []
            super().__init__(
                file_path=file_path,
                builder=builder,
                errors=errors,
                sheet_name=self.SHEET_NAME,
                optional=True,
            )
            if self._success:
                for index, _ in self._sheet.iterrows():
                    params = {
                        "name": self._read_cell_by_name(index, "name"),
                        "label": self._read_cell_by_name(index, "label"),
                        "description": self._read_cell_by_name(index, "description"),
                        "type": self._read_cdisc_klass_attribute_cell_by_name(
                            "GovernanceDate", "type", index, "type"
                        ),
                        "dateValue": self._read_date_cell_by_name(index, "dateValue"),
                        "geographicScopes": self._read_geographic_scopes_cell_by_name(
                            index, "geographicScopes"
                        ),
                    }
                    item = self._create(GovernanceDate, params)
                    if item:
                        self._items.append(item)
        except Exception as e:
            self._sheet_exception(e)

    @property
    def items(self):
        return self._items
