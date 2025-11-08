from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.study_amendment import StudyAmendment
from usdm4.api.study_change import StudyChange
from usdm4.api.document_content_reference import DocumentContentReference


class AmendmentChangesSheet(BaseSheet):
    SHEET_NAME = "amendmentChanges"

    def __init__(self, file_path: str, builder: Builder, errors: Errors):
        try:
            self.items = []
            super().__init__(
                file_path=file_path,
                builder=builder,
                errors=errors,
                sheet_name=self.SHEET_NAME,
                optional=True,
            )
            if self._success:
                for index, row in self._sheet.iterrows():
                    amendment = self._read_cell_by_name(index, "amendment")
                    name = self._read_cell_by_name(index, "name")
                    description = self._read_cell_by_name(index, "description")
                    label = self._read_cell_by_name(
                        index, "label", default="", must_be_present=False
                    )
                    rationale = self._read_cell_by_name(index, "rationale")
                    summary = self._read_cell_by_name(index, "summary")
                    sections = self._section_list(index)
                    item = self._create(
                        StudyChange,
                        {
                            "name": name,
                            "description": description,
                            "label": label,
                            "rationale": rationale,
                            "summary": summary,
                            "changedSections": sections,
                        },
                    )
                    if item:
                        self.items.append(item)
                        parent = self._builder.cross_reference.get_by_name(
                            StudyAmendment, amendment
                        )
                        if parent:
                            parent.changes.append(item)
                        else:
                            try:
                                column = self._column_present("amendment")
                                self._errors.error(
                                    f"Failed to find amendment with name '{amendment}'",
                                    self._location(index, column),
                                )
                            except Exception:
                                self._errors.error(
                                    f"Failed to find amendment with name '{amendment}'",
                                    self._location(index, None),
                                )
        except Exception as e:
            self._sheet_exception(e)

    def _section_list(self, index):
        result = []
        section_list = self._read_cell_multiple_by_name(index, "sections")
        for section in section_list:
            parts = section.split(":")
            if len(parts) == 2:
                ref = self._create(
                    DocumentContentReference,
                    {
                        "sectionNumber": parts[0].strip(),
                        "sectionTitle": parts[1].strip(),
                        "appliesToId": "TempId",
                    },
                )
                if ref:
                    result.append(ref)
            else:
                try:
                    column = self._column_present("sections")
                    self._errors.error(
                        f"Could not decode section reference '{section}'.",
                        self._location(index, column),
                    )
                except Exception:
                    self._errors.error(
                        f"Could not decode section reference '{section}'.",
                        self._location(index, None),
                    )
        return result
