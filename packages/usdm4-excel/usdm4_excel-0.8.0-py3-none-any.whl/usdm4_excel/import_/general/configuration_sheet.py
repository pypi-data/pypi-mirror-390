from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder


class ConfigurationSheet(BaseSheet):
    SHEET_NAME = "configuration"

    PARAMS_NAME_COL = 0
    PARAMS_VALUE_COL = 1

    def __init__(self, file_path: str, builder: Builder, errors: Errors):
        try:
            super().__init__(
                file_path=file_path,
                builder=builder,
                errors=errors,
                sheet_name=self.SHEET_NAME,
                optional=True,
                header=None,
            )
            if self._success:
                self._process_sheet()
        except Exception as e:
            self._sheet_exception(e)

    def _process_sheet(self):
        for rindex, row in self._sheet.iterrows():
            raw_name = self._read_cell(rindex, self.PARAMS_NAME_COL)
            name = raw_name.strip().upper()
            value = self._read_cell(rindex, self.PARAMS_VALUE_COL)
            if name == "CT VERSION":
                parts = value.split("=")
                if len(parts) == 2:
                    name = parts[0].strip()
                    version = parts[1].strip()
                    if name and version:
                        self._builder.other_ct_version_manager.add(name, version)
                    else:
                        self._errors.error(
                            "Badly formatted CT VERSION, '{value}' missing <CT name> or <version>",
                            self._location(rindex, 2),
                        )
                else:
                    self._errors.error(
                        "Badly formatted CT VERSION, '{value}' should be of the form <CT name> = <version>",
                        self._location(rindex, 2),
                    )
            else:
                self._errors.error(
                    f"Unrecognized configuration keyword '{raw_name}",
                    self._location(rindex, 1),
                )
