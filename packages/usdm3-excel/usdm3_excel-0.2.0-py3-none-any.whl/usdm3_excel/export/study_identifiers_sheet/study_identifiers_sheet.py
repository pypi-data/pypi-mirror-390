from .identifiers_panel import IdentifiersPanel
from usdm4.api.study import Study
from usdm4_excel.export.base.base_sheet import BaseSheet


class StudyIdentifiersSheet(BaseSheet):
    SHEET_NAME = "studyIdentifiers"

    def save(self, study: Study):
        op = IdentifiersPanel(self.ct_version)
        result = op.execute(study)
        self.etw.add_table(result, self.SHEET_NAME)
        self.etw.format_cells(
            self.SHEET_NAME,
            (1, 1, 1, 6),
            font_style="bold",
            background_color=self.HEADING_BG,
        )
        self.etw.set_column_width(self.SHEET_NAME, [1, 6], 20.0)
