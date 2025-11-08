from .main_panel import MainPanel
from .dates_panel import DatesPanel

from usdm4.api.study import Study
from usdm4_excel.export.base.base_sheet import BaseSheet


class StudySheet(BaseSheet):
    def save(self, study: Study):
        mp = MainPanel(self.ct_version)
        result = mp.execute(study)
        last_row = self.etw.add_table(result, "study")
        cp = DatesPanel(self.ct_version)
        result = cp.execute(study)
        dates_first_row = last_row + 2
        last_row = self.etw.add_table(result, "study", dates_first_row)
        self.etw.format_cells(
            "study",
            (1, 1, last_row, 1),
            font_style="bold",
            background_color=self.HEADING_BG,
        )
        self.etw.format_cells(
            "study",
            (1, 2, last_row, 2),
            wrap_text=True,
        )
        self.etw.format_cells(
            "study",
            (dates_first_row, 1, dates_first_row, 7),
            font_style="bold",
            background_color=self.HEADING_BG,
        )
        self.etw.set_column_width("study", [1, 3, 4, 5, 6, 7], 20.0)
        self.etw.set_column_width("study", 2, 40.0)
