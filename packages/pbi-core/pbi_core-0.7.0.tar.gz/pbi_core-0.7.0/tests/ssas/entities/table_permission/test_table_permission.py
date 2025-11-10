from pbi_core import LocalReport
from pbi_core.ssas.model_tables.role.local import LocalRole
from pbi_core.ssas.model_tables.table_permission.enums import MetadataPermission
from pbi_core.ssas.model_tables.table_permission.local import LocalTablePermission


def test_table_permission_parents(ssas_pbix):
    tp = ssas_pbix.ssas.table_permissions.find(2942)
    parents = tp.parents()
    assert len(parents) == 3
    assert {p.pbi_core_name() for p in parents} == {"Model", "main_table", "test_role"}
    assert {p.__class__.__name__ for p in parents} == {"Model", "Table", "Role"}


def test_table_permission_children(ssas_pbix):
    tp = ssas_pbix.ssas.table_permissions.find(2942)
    children = tp.children()
    assert len(children) == 0


def test_table_permission_alter():
    ssas_pbix = LocalReport.load_pbix("test_ssas.pbix")
    tp = ssas_pbix.ssas.table_permissions.find(2942)
    tp.metadata_permission = MetadataPermission.DEFAULT
    tp.filter_expression = "[a] > 5"
    tp.alter()


def test_table_permission_delete():
    ssas_pbix = LocalReport.load_pbix("test_ssas.pbix")
    tp = ssas_pbix.ssas.table_permissions.find(2942)
    tp.delete()


def test_table_permission_create():
    ssas_report = LocalReport.load_pbix("test_ssas.pbix")
    table = ssas_report.ssas.tables.find(lambda t: t.is_hidden is False and t.is_private is False)
    r = LocalRole(
        name="A local role",
        model_id=ssas_report.ssas.model.id,
        description="A local role description",
    ).load(ssas_report.ssas)
    LocalTablePermission(
        table_id=table.id,
        role_id=r.id,
        filter_expression="TRUE()",
    ).load(ssas_report.ssas)
