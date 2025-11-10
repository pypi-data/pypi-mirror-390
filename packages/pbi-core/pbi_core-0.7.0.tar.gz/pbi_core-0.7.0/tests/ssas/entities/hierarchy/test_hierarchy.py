from pbi_core import LocalReport
from pbi_core.ssas.model_tables.hierarchy.local import LocalHierarchy


def test_hierarchy_children(ssas_pbix):
    expr = ssas_pbix.ssas.hierarchies.find(1655)
    children = expr.children()
    assert len(children) == 6
    assert {c.pbi_core_name() for c in children} == {"Variation", "Day", "Quarter", "Month", "TemplateId", "Year"}
    assert {c.__class__.__name__ for c in children} == {"Annotation", "Level", "Variation"}


def test_hierarchy_parents(ssas_pbix: LocalReport):
    expr = ssas_pbix.ssas.hierarchies.find(1655)
    parents = expr.parents()
    assert len(parents) == 2
    assert {p.pbi_core_name() for p in parents} == {"LocalDateTable_f1dd39f2-2d79-466b-a0dd-7ac4c0d918ee", "Model"}
    assert {p.__class__.__name__ for p in parents} == {"Table", "Model"}


def test_hierarchy_alter(ssas_pbix):
    expr = ssas_pbix.ssas.hierarchies.find(1655)
    expr.description = "test description"
    expr.alter()


def test_hierarchy_delete():
    ssas_pbix = LocalReport.load_pbix("test_ssas.pbix")
    expr = ssas_pbix.ssas.hierarchies.find(1655)
    expr.delete()


def test_hierarchy_create():
    ssas_report = LocalReport.load_pbix("test_ssas.pbix")
    column = next(c for c in ssas_report.ssas.columns if c.is_normal())
    LocalHierarchy(
        name="Test Hierarchy",
        table_id=column.table_id,
    ).load(ssas_report.ssas)
