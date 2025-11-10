from pbi_core import LocalReport


def test_automatic_data_model_cleansing():
    report = LocalReport.load_pbix("test.pbix")
    report.cleanse_ssas_model()
    report.save_pbix("cull_test_out.pbix")
