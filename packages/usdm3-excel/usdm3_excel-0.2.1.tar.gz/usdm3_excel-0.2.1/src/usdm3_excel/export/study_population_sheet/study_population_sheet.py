from .study_population_panel import StudyPopulationPanel
from usdm4.api.study import Study
from usdm4_excel.export.base.base_sheet import BaseSheet


class StudyPopulationSheet(BaseSheet):
    SHEET_NAME = "studyDesignPopulations"

    def save(self, study: Study):
        op = StudyPopulationPanel(self.ct_version)
        result = op.execute(study)
        self.etw.add_table(result, self.SHEET_NAME)
        self.etw.format_cells(
            self.SHEET_NAME,
            (1, 1, 1, 4),
            font_style="bold",
            background_color=self.HEADING_BG,
        )
        self.etw.set_column_width(self.SHEET_NAME, [1, 2, 3, 4], 25.0)
