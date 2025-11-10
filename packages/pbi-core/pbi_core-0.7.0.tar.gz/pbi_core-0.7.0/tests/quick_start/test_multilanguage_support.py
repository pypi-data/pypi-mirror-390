from pbi_core import LocalReport
from pbi_core.misc.internationalization import get_static_elements, set_static_elements


def test_multilanguage_support():
    report = LocalReport.load_pbix("test.pbix")
    x = get_static_elements(report.static_files.layout)
    x.to_excel("multilang.xlsx")


def test_multilanguage_support_set() -> None:
    set_static_elements("multilang_example.xlsx", "test.pbix")
