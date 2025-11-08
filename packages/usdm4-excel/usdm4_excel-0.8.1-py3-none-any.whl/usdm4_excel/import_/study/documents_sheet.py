from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.study_definition_document import StudyDefinitionDocument
from usdm4.api.study_definition_document_version import StudyDefinitionDocumentVersion


class DocumentsSheet(BaseSheet):
    SHEET_NAME = "documents"

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
                for index, row in self._sheet.iterrows():
                    params = {
                        "name": self._read_cell_by_name(index, "name"),
                        "label": self._read_cell_by_name(index, "label"),
                        "description": self._read_cell_by_name(index, "description"),
                        "type": self._read_cdisc_klass_attribute_cell_by_name(
                            "StudyDefinitionDocument", "type", index, "type"
                        ),
                        "templateName": self._read_cell_by_name(index, "templateName"),
                        "language": self._read_iso639_code_cell_by_name(
                            index, "language"
                        ),
                    }
                    notes = self._read_cell_multiple_by_name(
                        index, "notes", must_be_present=False
                    )
                    item: StudyDefinitionDocument = self._create(
                        StudyDefinitionDocument, params
                    )
                    if item:
                        self._items.append(item)
                        document_version = self._get_cross_reference(
                            StudyDefinitionDocumentVersion,
                            self._read_cell_by_name(index, "documentVersion"),
                        )
                        if document_version:
                            item.versions.append(document_version)
                        self._add_notes(item, notes)
        except Exception as e:
            self._sheet_exception(e)

    @property
    def items(self):
        return self._items
