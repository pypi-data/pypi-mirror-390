from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.procedure import Procedure


class ProcedureSheet(BaseSheet):
    SHEET_NAME = "studyDesignProcedures"

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
                    name = self._read_cell_by_name(index, ["procedureName", "name"])
                    description = self._read_cell_by_name(
                        index, ["procedureDescription", "description"]
                    )
                    label = self._read_cell_by_name(
                        index, "label", default="", must_be_present=False
                    )
                    procedure_type = self._read_cell_by_name(index, "procedureType")
                    code = self._read_other_code_cell_by_name(
                        index, ["procedureCode", "code"]
                    )
                    item = self._create(
                        Procedure,
                        {
                            "name": name,
                            "description": description,
                            "label": label,
                            "procedureType": procedure_type,
                            "code": code,
                        },
                    )
                    if item:
                        self.items.append(item)
        except Exception as e:
            self._sheet_exception(e)
