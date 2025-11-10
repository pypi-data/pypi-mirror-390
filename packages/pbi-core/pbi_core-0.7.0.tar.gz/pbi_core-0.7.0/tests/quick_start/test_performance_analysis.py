import pytest


@pytest.mark.slow
def test_performance_analysis(ssas_pbix):
    section = ssas_pbix.static_files.layout.sections[0]
    perf = section.get_performance(ssas_pbix.ssas)
    assert perf
