from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.identifier import StudyIdentifier
from usdm4.api.organization import Organization


class IdentifiersSheet(BaseSheet):
    SHEET_NAME = "studyIdentifiers"

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
                self._process_sheet()
        except Exception as e:
            self._sheet_exception(e)

    @property
    def items(self) -> list[StudyIdentifier]:
        print(f"IDENTIFIERS: {self._items}")
        return self._items

    def _process_sheet(self):
        for index, row in self._sheet.iterrows():
            org_name = self._read_cell_by_name(index, "organization")
            organization: Organization = self._builder.cross_reference.get_by_name(
                Organization, org_name
            )
            if organization:
                item: StudyIdentifier = self._create(
                    StudyIdentifier,
                    {
                        "text": self._read_cell_by_name(
                            index, ["studyIdentifier", "identifier"]
                        ),
                        "scopeId": organization.id,
                    },
                )
                if item:
                    self._items.append(item)
            else:
                col_index = self._column_present("organization")
                self._errors.error(
                    f"Failed to find organization with name '{org_name}'",
                    self._location(index, col_index),
                )
