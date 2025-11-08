from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.narrative_content import NarrativeContentItem


class DocumentContentSheet(BaseSheet):
    SHEET_NAME = "documentContent"
    DIV_OPEN_NS = '<div xmlns="http://www.w3.org/1999/xhtml">'
    DIV_OPEN = "<div>"
    DIV_CLOSE = "</div>"

    def __init__(self, file_path: str, builder: Builder, errors: Errors):
        try:
            self._items = []
            self._map = {}
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
                        "text": self._wrap_div(self._read_cell_by_name(index, "text")),
                        "name": self._read_cell_by_name(index, "name"),
                    }
                    item: NarrativeContentItem = self._create(
                        NarrativeContentItem, params
                    )
                    if item:
                        self._items.append(item)
                        self._map[item.id] = item
        except Exception as e:
            self._sheet_exception(e)

    @property
    def items(self):
        return self._items

    def _wrap_div(self, text):
        if text.startswith(self.DIV_OPEN_NS):
            return text
        elif text.startswith(self.DIV_OPEN):
            return text.replace(self.DIV_OPEN, self.DIV_OPEN_NS)
        else:
            return f"{self.DIV_OPEN_NS}{text}{self.DIV_CLOSE}"
