import re
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder


class RangeType:
    def __init__(
        self,
        range_info: str,
        builder: Builder,
        errors: Errors,
        units_reqd: bool = True,
        allow_empty: bool = True,
    ):
        try:
            self.upper = None
            self.lower = None
            self.units = None
            self.units_code = None
            self._empty = False
            self.valid = False
            self.label = range_info.strip()
            if range_info:
                match = re.match(
                    r"(?P<lower>[+|-]*\d+)(\s*\.\.\s*(?P<upper>[+|-]*\d+))?( \s*(?P<units>.+))?",
                    self.label,
                )
                if match:
                    parts = match.groupdict()
                    self.lower = parts["lower"].strip()
                    if parts["upper"]:
                        self.upper = parts["upper"].strip()
                    else:
                        self.upper = self.lower
                    if units_reqd:
                        if parts["units"]:
                            self.units = parts["units"].strip()
                            cdisc_code = builder.cdisc_unit_code(self.units)
                            if cdisc_code:
                                self.units_code = builder.alias_code(cdisc_code)
                                self.valid = True
                            else:
                                errors.error(
                                    f"Unable to set the units code for the range '{range_info}'"
                                )
                        else:
                            errors.error(
                                f"Could not decode the range value, possible typographical errors '{range_info}'"
                            )
                    else:
                        self.valid = True
                else:
                    errors.error(f"Could not decode the range value '{range_info}'")
            elif not allow_empty:
                errors.error(
                    f"Could not decode the range value, appears to be empty '{range_info}'"
                )
            else:
                self._empty = True
        except Exception as e:
            errors.exception(
                f"Exception encountered decoding quantity '{range_info}'", e
            )
