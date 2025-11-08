from .document_panel import DocumentPanel
from usdm4.api.study import Study
from usdm4_excel.export.base.base_sheet import BaseSheet


class StudyDocumentSheet(BaseSheet):
    SHEET_NAME = "document"

    def save(self, study: Study):
        op = DocumentPanel(self.ct_version)
        result = op.execute(study)
        last_row = self.etw.add_table(result, self.SHEET_NAME)
        self.etw.format_cells(
            self.SHEET_NAME,
            (2, 1, last_row, 6),
            wrap_text=True,
            vertical_alignment="top",
        )
        self.etw.format_cells(
            self.SHEET_NAME,
            (1, 1, 1, 6),
            font_style="bold",
            background_color=self.HEADING_BG,
        )
        self.etw.set_column_width(self.SHEET_NAME, [1, 2, 3, 5, 6], 20.0)
        self.etw.set_column_width(self.SHEET_NAME, 4, 75.0)
