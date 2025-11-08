from .main_panel import MainPanel
from .high_level_design_panel import HighLevelDesignPanel
from usdm4.api.study import Study
from usdm4_excel.export.base.base_sheet import BaseSheet


class StudyDesignSheet(BaseSheet):
    SHEET_NAME = "studyDesign"

    def save(self, study: Study):
        mp = MainPanel(self.ct_version)
        result = mp.execute(study)
        last_row = self.etw.add_table(result, self.SHEET_NAME)
        cp = HighLevelDesignPanel(self.ct_version)
        result = cp.execute(study)
        HighLevelDesignPanel_first_row = last_row + 2
        last_row = self.etw.add_table(
            result, self.SHEET_NAME, HighLevelDesignPanel_first_row
        )
        self.etw.format_cells(
            "study",
            (1, 1, last_row, 1),
            font_style="bold",
            background_color=self.HEADING_BG,
        )
        self.etw.set_column_width(self.SHEET_NAME, [1, 3, 4, 5, 6, 7], 20.0)
