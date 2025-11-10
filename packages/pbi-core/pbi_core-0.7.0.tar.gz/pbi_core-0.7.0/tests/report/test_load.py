from pbi_core import LocalReport


def test_pbix_load():
    LocalReport.load_pbix("test.pbix")


def test_pbix_save(ssas_pbix):
    # TODO: add a case where the save happens after chdir
    ssas_pbix.save_pbix("test_out.pbix")


def test_pbix_load_static():
    report = LocalReport.load_pbix("test.pbix", load_static_files=True, load_ssas=False)
    assert report.static_files is not None
    assert not hasattr(report, "ssas")


def test_pbix_load_ssas():
    report = LocalReport.load_pbix("test.pbix", load_static_files=False, load_ssas=True)
    assert report.ssas is not None
    assert not hasattr(report, "static_files")
