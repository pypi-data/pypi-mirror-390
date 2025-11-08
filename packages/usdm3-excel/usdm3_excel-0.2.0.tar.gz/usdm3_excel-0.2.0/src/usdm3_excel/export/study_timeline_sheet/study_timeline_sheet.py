from .main_panel import MainPanel
from .headings_panel import HeadingsPanel
from .activities_panel import ActivitiesPanel
from usdm4.api.study import Study
from usdm4_excel.export.base.base_sheet import BaseSheet


class StudyTimelineSheet(BaseSheet):
    SHEET_NAME = "mainTimeline"

    def save(self, study: Study):
        mp = MainPanel(self.ct_version)
        result = mp.execute(study)
        last_row = self.etw.add_table(result, self.SHEET_NAME, 1, 1)
        mp = HeadingsPanel(self.ct_version)
        result = mp.execute(study)
        last_row = self.etw.add_table(result, self.SHEET_NAME, 1, 3)
        ap = ActivitiesPanel(self.ct_version)
        result = ap.execute(study)
        last_row = self.etw.add_table(result, self.SHEET_NAME, 9, 1)
        self.etw.format_cells(
            self.SHEET_NAME,
            (1, 1, last_row, 1),
            font_style="bold",
            background_color=self.HEADING_BG,
        )
        self.etw.set_column_width(self.SHEET_NAME, [1, 3, 4, 5, 6, 7], 20.0)
