from usdm4_excel.export import USDM4ExcelExport
from usdm4_excel.import_ import USDM4ExcelImport
from usdm4.api.wrapper import Wrapper
from simple_error_log.errors import Errors


class USDM4Excel:
    def __init__(self):
        self._errors = None

    def to_legacy_excel(self, usdm_file_path: str, excel_file_path: str):
        exporter = USDM4ExcelExport()
        exporter.to_excel(usdm_file_path, excel_file_path)

    def from_excel(self, file_path: str) -> Wrapper:
        importer = USDM4ExcelImport()
        result = importer.from_excel(file_path)
        self._errors = importer.errors
        return result

    def errors(self) -> Errors:
        return self._errors
