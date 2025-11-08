import os
import json
import pytest
from unittest.mock import MagicMock, patch, mock_open
from usdm3_excel import USDM3Excel
from usdm4_excel.export.base.ct_version import CTVersion
from usdm4_excel.export.excel_table_writer.excel_table_writer import ExcelTableWriter


class TestUSDM3Excel:
    """Tests for the USDM3Excel class."""

    @pytest.mark.xfail(reason="Excel file writing issues in test environment")
    def test_to_excel(self):
        """Test the to_excel method."""
        # Create a USDM3Excel instance
        usdm3_excel = USDM3Excel()

        # Mock the open function
        mock_json_data = {
            "study": {
                "id": "550e8400-e29b-41d4-a716-446655440000",  # Using a valid UUID
                "name": "Test Study",
            },
            "usdmVersion": "3.0.0",
            "instanceType": "Wrapper",
        }
        m = mock_open(read_data=json.dumps(mock_json_data))

        # Create a mock for the ExcelTableWriter
        mock_etw = MagicMock(spec=ExcelTableWriter)

        # Create a mock for the Workbook
        mock_workbook = MagicMock()
        mock_ws = MagicMock()
        mock_workbook.active = mock_ws

        # Mock the necessary classes and methods
        with (
            patch("builtins.open", m),
            patch(
                "os.path.exists", return_value=False
            ),  # Make sure it creates a new workbook
            patch("openpyxl.Workbook", return_value=mock_workbook),
            patch(
                "usdm4_excel.export.base.ct_version.CTVersion"
            ) as mock_ct_version_class,
            patch(
                "usdm4_excel.export.excel_table_writer.excel_table_writer.ExcelTableWriter",
                return_value=mock_etw,
            ),
            patch("usdm4.USDM4") as mock_usdm4_class,
            patch("usdm3_excel.StudySheet") as mock_study_sheet_class,
            patch(
                "usdm3_excel.StudyIdentifiersSheet"
            ) as mock_study_identifiers_sheet_class,
            patch("usdm3_excel.StudyContentSheet") as mock_study_content_sheet_class,
            patch(
                "usdm3_excel.StudyActivitiesSheet"
            ) as mock_study_activities_sheet_class,
            patch("usdm3_excel.StudyTimingSheet") as mock_study_timing_sheet_class,
            patch(
                "usdm3_excel.StudyEncountersSheet"
            ) as mock_study_encounters_sheet_class,
            patch("usdm3_excel.StudyEpochsSheet") as mock_study_epochs_sheet_class,
            patch("usdm3_excel.StudyArmsSheet") as mock_study_arms_sheet_class,
            patch("usdm3_excel.StudyDesignSheet") as mock_study_design_sheet_class,
            patch("usdm3_excel.StudyTimelineSheet") as mock_study_timeline_sheet_class,
            patch("usdm3_excel.ConfigurationSheet") as mock_configuration_sheet_class,
            patch(
                "usdm4_excel.export.study_procedures_sheet.study_procedures_sheet.StudyProceduresSheet"
            ) as mock_study_procedures_sheet_class,
        ):
            # Configure the mocks
            mock_ct_version = MagicMock(spec=CTVersion)
            mock_ct_version_class.return_value = mock_ct_version

            mock_usdm4 = MagicMock()
            mock_wrapper = MagicMock()
            mock_study = MagicMock()
            mock_wrapper.study = mock_study
            mock_usdm4.from_json.return_value = mock_wrapper
            mock_usdm4_class.return_value = mock_usdm4

            # Configure the sheet mocks
            mock_sheets = [
                mock_study_sheet_class.return_value,
                mock_study_identifiers_sheet_class.return_value,
                mock_study_content_sheet_class.return_value,
                mock_study_activities_sheet_class.return_value,
                mock_study_timing_sheet_class.return_value,
                mock_study_encounters_sheet_class.return_value,
                mock_study_epochs_sheet_class.return_value,
                mock_study_arms_sheet_class.return_value,
                mock_study_design_sheet_class.return_value,
                mock_study_timeline_sheet_class.return_value,
                mock_study_procedures_sheet_class.return_value,
                mock_configuration_sheet_class.return_value,
            ]

            # Call the to_excel method
            output_file = "tests/test_files/test.xlsx"
            usdm3_excel.to_excel("test.json", output_file)

            # Verify that the file was opened
            m.assert_called_once_with("test.json")

            # Verify that the CTVersion and ExcelTableWriter were created
            mock_ct_version_class.assert_called_once()

            # Verify that USDM4 was created and from_json was called
            mock_usdm4_class.assert_called_once()
            mock_usdm4.from_json.assert_called_once_with(mock_json_data)

            # Verify that each sheet was created and save was called
            for sheet in mock_sheets:
                sheet.save.assert_called_once_with(mock_study)

            # Verify that the ExcelTableWriter's save method was called
            mock_etw.save.assert_called_once()

            # Clean up
            try:
                os.remove(output_file)
                print(f"File {output_file} deleted")
            except Exception as e:
                print(f"Exception raised delting file {e}")
