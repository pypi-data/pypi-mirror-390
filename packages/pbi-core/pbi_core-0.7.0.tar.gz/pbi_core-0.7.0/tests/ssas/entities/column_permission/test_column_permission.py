from pbi_core import LocalReport
from pbi_core.ssas.model_tables.column_permission.local import LocalColumnPermission
from pbi_core.ssas.model_tables.role.local import LocalRole
from pbi_core.ssas.model_tables.table_permission.local import LocalTablePermission


def test_column_permission_create():
    ssas_report = LocalReport.load_pbix("test_ssas.pbix")

    table = ssas_report.ssas.tables.find(lambda t: t.is_hidden is False and t.is_private is False)
    column = next(c for c in table.columns() if c.is_normal())
    r = LocalRole(
        name="A local role",
        model_id=ssas_report.ssas.model.id,
        description="A local role description",
    ).load(ssas_report.ssas)
    m = LocalTablePermission(
        table_id=table.id,
        role_id=r.id,
        filter_expression="TRUE()",
    ).load(ssas_report.ssas)
    LocalColumnPermission(
        table_permission_id=m.id,
        column_id=column.id,
    ).load(ssas_report.ssas)
