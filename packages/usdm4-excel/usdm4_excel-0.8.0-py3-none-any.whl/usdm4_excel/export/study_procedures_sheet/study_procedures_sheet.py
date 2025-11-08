from .procedures_panel import ProceduresPanel
from usdm4.api.study import Study
from usdm4_excel.export.base.base_sheet import BaseSheet


class StudyProceduresSheet(BaseSheet):
    SHEET_NAME = "studyDesignProcedures"

    def save(self, study: Study):
        op = ProceduresPanel(self.ct_version)
        result = op.execute(study)
        self.etw.add_table(result, self.SHEET_NAME)
        self.etw.format_cells(
            self.SHEET_NAME,
            (1, 1, 1, 5),
            font_style="bold",
            background_color=self.HEADING_BG,
        )
        self.etw.set_column_width(self.SHEET_NAME, [1, 2, 3, 4, 5], 25.0)
