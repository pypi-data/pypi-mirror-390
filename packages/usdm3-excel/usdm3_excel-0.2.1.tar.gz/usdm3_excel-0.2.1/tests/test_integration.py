from usdm3_excel import USDM3Excel
from tests.helpers.excel_yaml_helper import ExcelYamlHelper

SAVE = False


def run_test(usdm_file, excel_file, yaml_file):
    usdm3_excel = USDM3Excel()
    usdm3_excel.to_excel(usdm_file, excel_file)
    helper = ExcelYamlHelper(excel_file, yaml_file)
    if SAVE:
        helper.save()
    assert helper.compare


def test_integration_1():
    run_test(
        "tests/test_files/usdm_1.json",
        "tests/test_files/usdm_excel_1.xlsx",
        "tests/test_files/usdm_excel_1.yaml",
    )


def test_integration_2():
    run_test(
        "tests/test_files/usdm_2.json",
        "tests/test_files/usdm_excel_2.xlsx",
        "tests/test_files/usdm_excel_2.yaml",
    )
