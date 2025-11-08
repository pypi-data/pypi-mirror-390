import re
from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4_excel.import_.iso8601.duration import Duration
from usdm4_excel.import_.types.window_type import WindowType
from usdm4.api.timing import Timing


class TimingSheet(BaseSheet):
    SHEET_NAME = "studyDesignTiming"

    def __init__(self, file_path: str, builder: Builder, errors: Errors):
        try:
            print("TIMING")
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
                    window = WindowType(
                        self._read_cell_by_name(index, "window"), builder, errors
                    )
                    item: Timing = self._create(
                        Timing,
                        {
                            "type": self._set_type(
                                self._read_cell_by_name(index, "type")
                            ),
                            "value": self._set_text_and_encoded(
                                self._read_cell_by_name(index, "timingValue")
                            ),
                            "valueLabel": self._read_cell_by_name(index, "timingValue"),
                            "name": self._read_cell_by_name(index, "name"),
                            "description": self._read_cell_by_name(
                                index, "description"
                            ),
                            "label": self._read_cell_by_name(index, "label"),
                            "relativeToFrom": self._set_to_from_type(
                                self._read_cell_by_name(index, "toFrom")
                            ),
                            "windowLabel": window.label,
                            "windowLower": window.lower,
                            "windowUpper": window.upper,
                            "relativeFromScheduledInstanceId": self._read_cell_by_name(
                                index, "from"
                            ),
                            "relativeToScheduledInstanceId": self._read_cell_by_name(
                                index, "to"
                            ),
                        },
                    )
                    if item:
                        self.items.append(item)
        except Exception as e:
            self._sheet_exception(e)

    def _set_text_and_encoded(self, duration):
        the_duration = duration.strip()
        original_duration = the_duration
        for char in ["+", "-"]:
            if char in the_duration:
                the_duration = the_duration.replace(char, "")
                self._errors.warning(f"Ignoring '{char}' in {original_duration}")
        duration_parts = re.findall(r"[^\W\d_]+|\d+", the_duration)
        if len(duration_parts) == 2:
            try:
                return Duration().encode(
                    duration_parts[0].strip(), duration_parts[1].strip()
                )
            except Exception as e:
                self._errors.exception(
                    f"Exception raised decoding the duration value '{the_duration}'", e
                )
        else:
            self._errors.error(
                f"Could not decode the duration value, no value and units found in '{the_duration}'"
            )

    def _set_type(self, text):
        type_code = {
            "FIXED": {"c_code": "C201358", "pt": "Fixed Reference"},
            "AFTER": {"c_code": "C201356", "pt": "After"},
            "BEFORE": {"c_code": "C201357", "pt": "Before"},
        }
        key = text.strip().upper()
        return self._builder.cdisc_code(type_code[key]["c_code"], type_code[key]["pt"])

    def _set_to_from_type(self, text):
        type_code = {
            "S2S": {"c_code": "C201355", "pt": "Start to Start"},
            "S2E": {"c_code": "C201354", "pt": "Start to End"},
            "E2S": {"c_code": "C201353", "pt": "End to Start"},
            "E2E": {"c_code": "C201352", "pt": "End to End"},
        }
        key = "S2S" if not text else text.strip().upper()
        return self._builder.cdisc_code(type_code[key]["c_code"], type_code[key]["pt"])
