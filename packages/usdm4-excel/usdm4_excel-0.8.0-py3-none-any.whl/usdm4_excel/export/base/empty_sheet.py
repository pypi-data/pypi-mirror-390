from usdm4_excel.export.base.base_sheet import BaseSheet


class EmptySheet(BaseSheet):
    def blank(self, column_names: list, sheet_name: str) -> None:
        _ = self.etw.add_table([column_names], sheet_name)
        self.etw.format_cells(
            sheet_name,
            (1, 1, 1, len(column_names)),
            font_style="bold",
            background_color=self.HEADING_BG,
        )
        self.etw.set_column_width(sheet_name, [1, 2], 25.0)
