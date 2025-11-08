from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from usdm4.api.eligibility_criterion import (
    EligibilityCriterion,
    EligibilityCriterionItem,
)


class EligibilityCriteriaSheet(BaseSheet):
    SHEET_NAME = "eligibilityCriteria"

    def __init__(self, file_path: str, builder: Builder, errors: Errors):
        try:
            self._items = []
            self.criterion_items = []
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
                        "category": self._read_cdisc_klass_attribute_cell_by_name(
                            "EligibilityCriteria", "category", index, "category"
                        ),
                        "identifier": self._read_cell_by_name(index, "identifier"),
                        "name": self._read_cell_by_name(index, "name"),
                        "description": self._read_cell_by_name(index, "description"),
                        "label": self._read_cell_by_name(index, "label"),
                    }
                    eci: EligibilityCriterionItem = (
                        self._builder.cross_reference.get_by_name(
                            EligibilityCriterionItem,
                            self._read_cell_by_name(index, "item"),
                        )
                    )
                    if eci:
                        params["criterionItemId"] = eci.id
                        ec = self._create(EligibilityCriterion, params)
                        if ec:
                            self._items.append(ec)
                self._double_link(self._items, "previousId", "nextId")
        except Exception as e:
            self._sheet_exception(e)

    @property
    def items(self):
        return self._items
