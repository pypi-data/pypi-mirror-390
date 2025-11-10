from pbi_core import LocalReport


def test_server_sync():
    ssas_pbix = LocalReport.load_pbix("test_ssas.pbix")
    col_count = len(ssas_pbix.ssas.columns)

    c = ssas_pbix.ssas.columns.find(lambda c: c.is_normal())
    c.delete()
    ssas_pbix.ssas.sync_from()
    assert len(ssas_pbix.ssas.columns) == col_count - 1
