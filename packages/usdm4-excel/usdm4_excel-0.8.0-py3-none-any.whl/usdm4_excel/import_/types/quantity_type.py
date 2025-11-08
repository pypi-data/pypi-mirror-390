import re
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder


class QuantityType:
    def __init__(
        self,
        quantity_info: str,
        builder: Builder,
        errors: Errors,
        allow_missing_units: bool = True,
        allow_empty: bool = True,
    ):
        try:
            self.value = None
            self.units = None
            self.units_code = None
            self._empty = False
            self.valid = False
            self.label = quantity_info.strip()
            if quantity_info:
                match = re.match(
                    r"(?P<value>[+|-]*\d+)\.?\d{0,5}(\s*(?P<units>.+))?", self.label
                )
                if match:
                    parts = match.groupdict()
                    self.value = parts["value"].strip()
                    if parts["units"]:
                        self.units = parts["units"].strip()
                        self.units_code = builder.cdisc_unit_code(self.units)
                        if not self.units_code:
                            errors.error(
                                f"Unable to set the units code for the quantity '{quantity_info}'"
                            )
                        else:
                            self.valid = True
                    elif allow_missing_units:
                        self.valid = True
                    else:
                        errors.error(
                            f"Could not decode the quantity value, possible typographical errors '{quantity_info}'"
                        )
                else:
                    errors.error(
                        f"Could not decode the quantity value '{quantity_info}'"
                    )
            elif not allow_empty:
                errors.error(
                    f"Could not decode the quantity value, appears to be empty '{quantity_info}'"
                )
            else:
                self._empty = True
        except Exception as e:
            errors.exception(
                f"Exception encountered decoding quantity '{quantity_info}'", e
            )
