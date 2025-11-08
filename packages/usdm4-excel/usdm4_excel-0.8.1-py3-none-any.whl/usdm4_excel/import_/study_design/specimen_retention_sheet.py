from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.biospecimen_retention import BiospecimenRetention


class SpecimenRetentionSheet(BaseSheet):
    SHEET_NAME = "studyDesignSpecimen"

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
                    name = self._read_cell_by_name(index, ["name"])
                    description = self._read_cell_by_name(
                        index, "description", default="", must_be_present=False
                    )
                    label = self._read_cell_by_name(
                        index, "label", default="", must_be_present=False
                    )
                    retained = self._read_boolean_cell_by_name(index, "retained")
                    includesDNA = self._read_boolean_cell_by_name(index, "includesDNA")
                    item = self._create(
                        BiospecimenRetention,
                        {
                            "name": name,
                            "description": description,
                            "label": label,
                            "isRetained": retained,
                            "includesDNA": includesDNA,
                        },
                    )
                    if item:
                        self.items.append(item)
        except Exception as e:
            self._sheet_exception(e)
