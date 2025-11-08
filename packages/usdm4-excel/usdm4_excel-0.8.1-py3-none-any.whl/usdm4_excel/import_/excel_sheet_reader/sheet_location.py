from simple_error_log.error_location import ErrorLocation


class SheetLocation(ErrorLocation):
    """
    Error location for a excel sheet
    """

    def __init__(self, sheet_name: str, row: int | None, column: int | None):
        """
        Initialize the location
        """
        self._sheet_name = sheet_name
        self._row = row + 1 if row is not None else None
        self._column = column + 1 if column is not None else None

    def to_dict(self):
        """
        Convert the sheet location to a dictionary
        """
        return {
            "sheet": self._sheet_name,
            "row": self._row if self._row else "?",
            "column": self._column if self._column else "?",
        }

    def __str__(self):
        """
        Convert the sheet location to a string
        """
        if self._row:
            return f"Sheet: {self._sheet_name} [{self._row}, {self._column if self._column else '?'}]"
        else:
            return f"Sheet: {self._sheet_name}"
