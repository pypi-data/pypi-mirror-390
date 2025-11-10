from pbi_core import LocalReport


def test_data_source_create():
    ssas_report = LocalReport.load_pbix("test_ssas.pbix")
    # LocalDataSource(
    #     name="New DataSource",
    #     model_id=ssas_report.ssas.model.id,
    #     connection_string="Provider=SQLNCLI11.1;Data Source=MyServer;Initial Catalog=MyDB;",
    # ).load(ssas_report.ssas)
