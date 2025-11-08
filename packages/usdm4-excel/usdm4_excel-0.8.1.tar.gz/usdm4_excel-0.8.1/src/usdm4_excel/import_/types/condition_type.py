from simple_error_log.errors import Errors


class ConditionType:
    def __init__(self, conditon_info, errors: Errors):
        self.items = []
        if conditon_info:
            parts = conditon_info.split(",")
            for part in parts:
                name_value = part.split(":")
                if len(name_value) == 2:
                    name = self._remove_unprintable(name_value[0])
                    condition = self._remove_unprintable(name_value[1])
                    self.items.append({"name": name, "condition": condition})
                else:
                    errors.error(
                        f"Could not decode a condition, no ':' found in '{part}'"
                    )

    def _remove_unprintable(self, text):
        return "".join(c for c in text if c.isprintable()).strip()
