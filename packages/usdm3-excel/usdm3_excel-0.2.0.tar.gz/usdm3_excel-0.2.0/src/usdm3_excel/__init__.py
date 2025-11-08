import os
from simple_error_log import Errors
from usdm3_excel.export.study_sheet.study_sheet import StudySheet
from usdm3_excel.export.study_population_sheet.study_population_sheet import StudyPopulationSheet
from usdm3_excel.export.study_identifiers_sheet.study_identifiers_sheet import (
    StudyIdentifiersSheet,
)
from usdm3_excel.export.study_content_sheet.study_content_sheet import (
    StudyContentSheet,
)
from usdm4_excel.export.study_activities_sheet.study_activities_sheet import (
    StudyActivitiesSheet,
)
from usdm4_excel.export.study_encounters_sheet.study_encounters_sheet import (
    StudyEncountersSheet,
)
from usdm4_excel.export.study_epochs_sheet.study_epochs_sheet import (
    StudyEpochsSheet,
)
from usdm4_excel.export.study_arms_sheet.study_arms_sheet import (
    StudyArmsSheet,
)
from usdm3_excel.export.study_design_sheet.study_design_sheet import (
    StudyDesignSheet,
)
from usdm3_excel.export.study_timeline_sheet.study_timeline_sheet import (
    StudyTimelineSheet,
)
from usdm4_excel.export.study_procedures_sheet.study_procedures_sheet import (
    StudyProceduresSheet,
)
from usdm4_excel.export.configuration_sheet.configuration_sheet import (
    ConfigurationSheet,
)
from usdm3_excel.export.study_timing_sheet.study_timing_sheet import StudyTimingSheet
from usdm4_excel.export.base.empty_sheet import EmptySheet
from usdm4_excel.export.base.ct_version import CTVersion
from usdm4_excel.export.excel_table_writer.excel_table_writer import ExcelTableWriter
from usdm4 import USDM4
from usdm4.api.wrapper import Wrapper


class USDM3Excel:
    def to_excel(self, usdm_filepath: str, excel_filepath: str):
        ct_version = CTVersion()
        self._remove_exisitng_file(excel_filepath)
        etw = ExcelTableWriter(excel_filepath, default_sheet_name="study")
        usdm = USDM4()
        errors = Errors()
        wrapper: Wrapper = usdm.load(usdm_filepath, errors)
        study = wrapper.study
        empty_sheets = {
            "studyDesignElements": [
                "name",
                "description",
                "label",
                "transitionStartRule",
                "transitionEndRule",
            ],
            "studyDesignIndications": ["name", "description", "label", "codes"],
            "studyDesignInterventions": [
                "name",
                "description",
                "label",
                "codes",
                "role",
                "type",
                "pharmacologicalClass",
                "productDesignation",
                "minimumResponseDuration",
                "administrationName",
                "administrationDescription",
                "administrationLabel",
                "administrationRoute",
                "administrationDose",
                "administrationFrequency",
                "administrationDurationDescription",
                "administrationDurationWillVary",
                "administrationDurationWillVaryReason",
                "administrationDurationQuantity",
            ],
            "studyDesignPopulations": [
                "level",
                "name",
                "description",
                "label",
                "plannedCompletionNumber",
                "plannedEnrollmentNumber",
                "plannedAge",
                "plannedSexOfParticipants",
                "includesHealthySubjects",
            ],
            "studyDesignEstimands": [
                "xref",
                "summaryMeasure",
                "populationDescription",
                "intercurrentEventName",
                "intercurrentEventDescription",
                "intercurrentEventStrategy",
                "treatmentXref",
                "endpointXref",
            ],
            "studyDesignOE": [
                "objectiveName",
                "objectiveDescription",
                "objectiveLabel",
                "objectiveText",
                "objectiveLevel",
                "endpointName",
                "endpointDescription",
                "endpointLabel",
                "endpointText",
                "endpointPurpose",
                "endpointLevel",
            ],
            "studyDesignEligibilityCriteria": [
                "category",
                "identifier",
                "name",
                "description",
                "label",
                "text",
                "dictionary",
            ],
        }
        for sheet_name, column_names in empty_sheets.items():
            _ = EmptySheet(ct_version, etw).blank(column_names, sheet_name)

        for klass in [
            StudySheet,
            StudyPopulationSheet,
            StudyIdentifiersSheet,
            StudyContentSheet,
            StudyActivitiesSheet,
            StudyTimingSheet,
            StudyEncountersSheet,
            StudyEpochsSheet,
            StudyArmsSheet,
            StudyDesignSheet,
            StudyTimelineSheet,
            StudyProceduresSheet,
            ConfigurationSheet,
        ]:
            klass(ct_version, etw).save(study)
        etw.save()

    def _remove_exisitng_file(self, excel_filepath: str) -> None:
        try:
            os.remove(excel_filepath)
        except Exception:
            pass
    