from .activities_panel import ActivitiesPanel
from usdm4.api.study import Study
from usdm4_excel.export.base.base_sheet import BaseSheet


class StudyActivitiesSheet(BaseSheet):
    SHEET_NAME = "studyDesignActivities"

    def save(self, study: Study):
        op = ActivitiesPanel(self.ct_version)
        result = op.execute(study)
        self.etw.add_table(result, self.SHEET_NAME)
        self.etw.format_cells(
            self.SHEET_NAME,
            (1, 1, 1, 3),
            font_style="bold",
            background_color=self.HEADING_BG,
        )
        self.etw.set_column_width(self.SHEET_NAME, [1, 2], 20.0)
        self.etw.set_column_width(self.SHEET_NAME, 3, 50.0)
