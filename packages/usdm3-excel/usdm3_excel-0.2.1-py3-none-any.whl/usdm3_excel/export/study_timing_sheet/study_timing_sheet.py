from .timing_panel import TimingPanel
from usdm4.api.study import Study
from usdm4_excel.export.base.base_sheet import BaseSheet


class StudyTimingSheet(BaseSheet):
    SHEET_NAME = "studyDesignTiming"

    def save(self, study: Study):
        op = TimingPanel(self.ct_version)
        result = op.execute(study)
        self.etw.add_table(result, self.SHEET_NAME)
        self.etw.format_cells(
            self.SHEET_NAME,
            (1, 1, 1, 9),
            font_style="bold",
            background_color=self.HEADING_BG,
        )
        self.etw.set_column_width(self.SHEET_NAME, [1, 2, 3], 30.0)
        self.etw.set_column_width(self.SHEET_NAME, [4, 5, 6, 7, 8, 9], 15.0)
