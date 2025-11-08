from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.activity import Activity


class ActivitiesSheet(BaseSheet):
    SHEET_NAME = "studyDesignActivities"

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
                    name = self._read_cell_by_name(index, ["activityName", "name"])
                    description = self._read_cell_by_name(
                        index, ["activityDescription", "description"]
                    )
                    label = self._read_cell_by_name(
                        index, "label", default="", must_be_present=False
                    )
                    notes = self._read_cell_multiple_by_name(
                        index, "notes", must_be_present=False
                    )
                    item = self._create(
                        Activity,
                        {"name": name, "description": description, "label": label},
                    )
                    if item:
                        self.items.append(item)
                        self._add_notes(item, notes)
                self._double_link(self.items, "previousId", "nextId")
        except Exception as e:
            self._sheet_exception(e)
