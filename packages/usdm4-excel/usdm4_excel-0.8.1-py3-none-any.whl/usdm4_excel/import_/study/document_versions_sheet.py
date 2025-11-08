from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.study_definition_document_version import StudyDefinitionDocumentVersion
from usdm4.api.governance_date import GovernanceDate


class DocumentVersionsSheet(BaseSheet):
    SHEET_NAME = "documentVersions"

    def __init__(self, file_path: str, builder: Builder, errors: Errors):
        try:
            self._items = []
            self._map = {}
            super().__init__(
                file_path=file_path,
                builder=builder,
                errors=errors,
                sheet_name=self.SHEET_NAME,
                optional=True,
            )
            if self._success:
                for index, _ in self._sheet.iterrows():
                    date_name = self._read_cell_by_name(index, "date")
                    params = {
                        "name": self._read_cell_by_name(index, "name"),
                        "version": self._read_cell_by_name(index, "version"),
                        "date": self._get_cross_reference(GovernanceDate, date_name),
                        "status": self._read_cdisc_klass_attribute_cell_by_name(
                            "StudyProtocolVersion",
                            "protocolStatus",
                            index,
                            "status",
                        ),
                    }
                    notes = self._read_cell_multiple_by_name(
                        index, "notes", must_be_present=False
                    )
                    sheet_name = self._read_cell_by_name(index, "sheetName")
                    item: StudyDefinitionDocumentVersion = self._create(
                        StudyDefinitionDocumentVersion, params
                    )
                    if item:
                        self._items.append(item)
                        self._map[item.id] = sheet_name
                        self._add_notes(item, notes)
        except Exception as e:
            self._sheet_exception(e)

    @property
    def items(self):
        return self._items

    def sheet_name(self, id: str) -> str | None:
        return self._map[id] if id in self._map else None
