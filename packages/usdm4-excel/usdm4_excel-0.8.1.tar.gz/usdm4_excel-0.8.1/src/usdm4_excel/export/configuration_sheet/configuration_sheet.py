from .configuration_panel import ConfigurationPanel
from usdm4.api.study import Study
from usdm4_excel.export.base.base_sheet import BaseSheet


class ConfigurationSheet(BaseSheet):
    SHEET_NAME = "configuration"

    def save(self, study: Study):
        op = ConfigurationPanel(self.ct_version)
        result = op.execute(study)
        last_row = self.etw.add_table(result, self.SHEET_NAME)
        self.etw.format_cells(
            self.SHEET_NAME,
            (1, 1, last_row, 1),
            font_style="bold",
            background_color=self.HEADING_BG,
        )
        self.etw.set_column_width(self.SHEET_NAME, [1, 2], 25.0)
