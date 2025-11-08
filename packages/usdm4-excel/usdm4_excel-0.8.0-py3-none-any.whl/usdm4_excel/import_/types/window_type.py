from usdm4_excel.import_.iso8601.duration import Duration
from usdm4_excel.import_.types.range_type import RangeType
from usdm4.builder.builder import Builder
from simple_error_log.errors import Errors


class WindowType:
    def __init__(self, timing_info: str, builder: Builder, errors: Errors):
        try:
            self.upper = None
            self.lower = None
            self.valid = False
            self.label = timing_info.strip() if timing_info else ""
            if self.label:
                range = RangeType(self.label, builder, errors)
                if range.valid:
                    self.lower = self._set_encoded(range.lower, range.units)
                    self.upper = self._set_encoded(range.upper, range.units)
                    self.valid = True
        except Exception as e:
            errors.exception(
                f"Exception encountered decoding quantity '{timing_info}'", e
            )

    def _set_encoded(self, value, units):
        for char in ["+", "-"]:
            if char in value:
                value = value.replace(char, "")
        value = Duration().encode(value, units)
        return value
