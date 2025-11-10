from pbi_core import LocalReport
from pbi_core.ssas.model_tables.hierarchy.local import LocalHierarchy
from pbi_core.ssas.model_tables.level.local import LocalLevel


def test_level_children(ssas_pbix):
    expr = ssas_pbix.ssas.levels.find(1660)
    children = expr.children()
    assert len(children) == 0


def test_level_parents(ssas_pbix):
    expr = ssas_pbix.ssas.levels.find(1660)
    parents = expr.parents()
    assert len(parents) == 5
    assert {p.pbi_core_name() for p in parents} == {
        "LocalDateTable_f1dd39f2-2d79-466b-a0dd-7ac4c0d918ee",
        "Date Hierarchy",
        "Day",
        "Model",
        "Date",
    }
    assert {p.__class__.__name__ for p in parents} == {"Column", "Hierarchy", "Table", "Model"}


def test_level_alter():
    ssas_pbix = LocalReport.load_pbix("test_ssas.pbix")
    expr = ssas_pbix.ssas.levels.find(1660)
    expr.description = "test description"
    expr.alter()


def test_level_delete():
    ssas_pbix = LocalReport.load_pbix("test_ssas.pbix")
    expr = ssas_pbix.ssas.levels.find(1660)
    expr.delete()


def test_level_create():
    ssas_report = LocalReport.load_pbix("test_ssas.pbix")
    column = next(c for c in ssas_report.ssas.columns if c.is_normal())
    h = LocalHierarchy(
        name="Test Hierarchy",
        table_id=column.table_id,
    ).load(ssas_report.ssas)
    LocalLevel(
        column_id=column.id,
        hierarchy_id=h.id,
        name="Test Level",
    ).load(ssas_report.ssas)
