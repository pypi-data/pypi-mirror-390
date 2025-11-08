from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.indication import Indication


class IndicationsSheet(BaseSheet):
    SHEET_NAME = "studyDesignIndications"

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
                    name = self._read_cell_by_name(index, "name")
                    description = self._read_cell_by_name(index, "description")
                    label = self._read_cell_by_name(index, "label", default="")
                    rare = self._read_boolean_cell_by_name(index, "isRareDisease")
                    codes = self._read_other_code_cell_multiple_by_name(index, "codes")
                    notes = self._read_cell_multiple_by_name(
                        index, "notes", must_be_present=False
                    )
                    item = self._create(
                        Indication,
                        {
                            "name": name,
                            "description": description,
                            "label": label,
                            "isRareDisease": rare,
                            "codes": codes,
                        },
                    )
                    if item:
                        self.items.append(item)
                        self._add_notes(item, notes)
        except Exception as e:
            self._sheet_exception(e)
