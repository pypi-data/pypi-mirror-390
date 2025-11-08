from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.study_amendment import StudyAmendment
from usdm4.api.study_amendment_impact import StudyAmendmentImpact


class AmendmentImpactSheet(BaseSheet):
    SHEET_NAME = "amendmentImpact"

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
                    amendment = self._read_cell_by_name(index, "amendment")
                    text = self._read_cell_by_name(index, "text")
                    substantial = self._read_boolean_cell_by_name(index, "substantial")
                    type = self._read_cdisc_klass_attribute_cell_by_name(
                        "StudyAmendmentImpact", "type", index, "type"
                    )
                    notes = self._read_cell_multiple_by_name(
                        index, "notes", must_be_present=False
                    )
                    item = self._create(
                        StudyAmendmentImpact,
                        {"text": text, "isSubstantial": substantial, "type": type},
                    )
                    if item:
                        self.items.append(item)
                        self._add_notes(item, notes)
                        parent = self._builder.cross_reference.get_by_name(
                            StudyAmendment, amendment
                        )
                        if parent:
                            parent.impacts.append(item)
                        else:
                            try:
                                column = self._column_present("amendment")
                                self._errors.error(
                                    f"Failed to find amendment with name '{amendment}'",
                                    self._location(index, column),
                                )
                            except Exception:
                                self._errors.error(
                                    f"Failed to find amendment with name '{amendment}'",
                                    self._location(index, None),
                                )
        except Exception as e:
            self._sheet_exception(e)
