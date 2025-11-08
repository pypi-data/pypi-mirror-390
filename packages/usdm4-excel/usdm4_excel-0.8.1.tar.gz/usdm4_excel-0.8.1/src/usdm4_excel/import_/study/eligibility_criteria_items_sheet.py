from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.eligibility_criterion import EligibilityCriterionItem


class EligibilityCriteriaItemsSheet(BaseSheet):
    SHEET_NAME = "eligibilityCriteriaItems"

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
                        "description": self._read_cell_by_name(index, "description"),
                        "label": self._read_cell_by_name(index, "label"),
                        "text": self._read_cell_by_name(index, "text"),
                    }
                    params["dictionaryId"] = self._get_dictionary_id(
                        self._read_cell_by_name(index, "dictionary")
                    )
                    if item := self._create(EligibilityCriterionItem, params):
                        self._items.append(item)
        except Exception as e:
            self._sheet_exception(e)

    @property
    def items(self):
        return self._items
