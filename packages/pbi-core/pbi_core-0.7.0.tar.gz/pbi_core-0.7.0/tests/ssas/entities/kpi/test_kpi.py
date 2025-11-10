from pbi_core import LocalReport
from pbi_core.ssas.model_tables.kpi.local import LocalKPI


def test_kpi_create():
    ssas_report = LocalReport.load_pbix("test_ssas.pbix")
    measure = ssas_report.ssas.measures[0]
    LocalKPI(
        measure_id=measure.id,
    ).load(ssas_report.ssas)
