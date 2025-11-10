from pbi_core import LocalReport


def test_altering_data_model():
    report = LocalReport.load_pbix("test.pbix")
    for column in report.ssas.columns:
        if column.is_key:
            continue
        column.description = "pbi_core has touched this"
        column.alter()  # saves the changes to the SSAS DB

    report.save_pbix("api_out.pbix")
