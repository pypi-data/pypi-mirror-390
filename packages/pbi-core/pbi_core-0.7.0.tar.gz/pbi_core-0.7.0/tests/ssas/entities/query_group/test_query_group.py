from pbi_core import LocalReport
from pbi_core.ssas.model_tables.query_group.local import LocalQueryGroup


def test_query_group_children(ssas_pbix):
    expr = ssas_pbix.ssas.query_groups.find(3383)
    children = expr.children()
    assert len(children) == 4
    assert {c.pbi_core_name() for c in children} == {"Section", "PBI_QueryGroupOrder", "Filter", "Visual"}
    assert {c.__class__.__name__ for c in children} == {"Annotation", "Partition"}


def test_query_group_parents(ssas_pbix):
    expr = ssas_pbix.ssas.query_groups.find(3383)
    parents = expr.parents()
    assert len(parents) == 1
    assert {p.pbi_core_name() for p in parents} == {"Model"}
    assert {p.__class__.__name__ for p in parents} == {"Model"}


def test_query_group_alter(ssas_pbix) -> None:
    expr = ssas_pbix.ssas.query_groups.find(3383)
    expr.description = "test description"
    expr.alter()


def test_query_group_delete():
    ssas_pbix = LocalReport.load_pbix("test_ssas.pbix")
    expr = ssas_pbix.ssas.query_groups.find(3383)
    expr.delete()


def test_query_group_create():
    ssas_report = LocalReport.load_pbix("test_ssas.pbix")
    LocalQueryGroup(
        folder="New Query Group",
        model_id=ssas_report.ssas.model.id,
    ).load(ssas_report.ssas)
