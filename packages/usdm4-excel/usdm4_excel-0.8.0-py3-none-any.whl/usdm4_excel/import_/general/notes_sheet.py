from usdm4_excel.import_.excel_sheet_reader.base_sheet import BaseSheet
from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder
from usdm4.api.comment_annotation import CommentAnnotation


class NotesSheet(BaseSheet):
    SHEET_NAME = "notes"

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
                    name = self._read_cell_by_name(index, "name")
                    text = self._read_cell_by_name(index, "text")
                    codes = self._read_other_code_cell_multiple_by_name(index, "codes")
                    params = {"name": name, "text": text, "codes": codes}
                    item = self._create(CommentAnnotation, params)
                    if item:
                        self.items.append(item)
        except Exception as e:
            self._sheet_exception(e)
