from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.condition import Condition


class ConditionsSheet(BaseSheet):
    SHEET_NAME = "studyDesignConditions"

    def __init__(self, file_path: str, builder: Builder, errors: Errors):
        try:
            print("CONDITIONS")
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
                    label = self._read_cell_by_name(index, "label")
                    text = self._read_cell_by_name(index, "text")
                    context = self._read_cell_by_name(index, "context")
                    context_refs = self._process_context_references(context, index)
                    applies_to = self._read_cell_by_name(index, "appliesTo")
                    applies_refs = self._process_applies_to_references(
                        applies_to, index
                    )

                    item: Condition = self._create(
                        Condition,
                        {
                            "name": name,
                            "description": description,
                            "label": label,
                            "text": text,
                            "appliesToIds": applies_refs,
                            "contextIds": context_refs,
                        },
                    )
                    if item:
                        self.items.append(item)
        except Exception as e:
            self._sheet_exception(e)

    def _process_context_references(self, references_list, index):
        return self._process_references(
            references_list,
            ["ScheduledActivityInstance", "Activity"],
            index,
            "context",
            False,
        )

    def _process_applies_to_references(self, references_list, index):
        return self._process_references(
            references_list,
            [
                "Procedure",
                "Activity",
                "BiomedicalConcept",
                "BiomedicalConceotCategory",
                "BiomedicalConceptSurrogate",
            ],
            index,
            "appliesTo",
            True,
        )

    def _process_references(
        self, references_list, klasses, index, column_name, references_required=True
    ):
        references = [x.strip() for x in self._state_split(references_list)]
        results = []
        for reference in references:
            if reference:
                found = False
                for klass in klasses:
                    xref = self._builder.cross_reference.get_by_name(klass, reference)
                    if xref:
                        results.append(xref.id)
                        found = True
                        break
                if not found:
                    self._errors.error(
                        f"Could not resolve condition reference '{reference}'",
                        self._get_grid_location(index, column_name),
                    )
        if not results and references_required:
            self._errors.error(
                f"No condition references found for '{references_list}', at least one required",
                self._get_grid_location(index, column_name),
            )
        return results

    def _get_grid_location(self, row_index, column_name):
        """Get grid location for error reporting"""
        try:
            col_index = self._column_present(column_name)
            return self._location(row_index, col_index)
        except Exception:
            return self._location(row_index, None)
