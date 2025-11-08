from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.study_element import StudyElement
from usdm4.api.transition_rule import TransitionRule


class ElementsSheet(BaseSheet):
    SHEET_NAME = "studyDesignElements"

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
                    name = self._read_cell_by_name(index, ["studyElementName", "name"])
                    description = self._read_cell_by_name(
                        index, ["studyElementDescription", "description"]
                    )
                    label = self._read_cell_by_name(
                        index, "label", default="", must_be_present=False
                    )
                    start_rule_text = self._read_cell_by_name(
                        index, "transitionStartRule", must_be_present=False
                    )
                    end_rule_text = self._read_cell_by_name(
                        index, "transitionEndRule", must_be_present=False
                    )
                    notes = self._read_cell_multiple_by_name(
                        index, "notes", must_be_present=False
                    )

                    # Create transition rules if text is provided
                    start_rule = None
                    end_rule = None

                    if start_rule_text:
                        start_rule = self._create(
                            TransitionRule,
                            {
                                "name": f"ELEMENT_START_RULE_{index + 1}",
                                "text": start_rule_text,
                            },
                        )

                    if end_rule_text:
                        end_rule = self._create(
                            TransitionRule,
                            {
                                "name": f"ELEMENT_END_RULE_{index + 1}",
                                "text": end_rule_text,
                            },
                        )

                    item: StudyElement = self._create(
                        StudyElement,
                        {
                            "name": name,
                            "description": description,
                            "label": label,
                            "transitionStartRule": start_rule,
                            "transitionEndRule": end_rule,
                        },
                    )
                    if item:
                        self.items.append(item)
                        self._add_notes(item, notes)
        except Exception as e:
            print(f"EXCEPTION 1: {e}")
            self._sheet_exception(e)
