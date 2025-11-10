from pbi_core import LocalReport
from pbi_core.ssas.model_tables.variation.local import LocalVariation


def test_variation_children(ssas_pbix):
    expr = ssas_pbix.ssas.variations.find(1656)
    children = expr.children()
    assert len(children) == 0


def test_variation_parents():
    ssas_pbix = LocalReport.load_pbix("test_ssas.pbix")
    expr = ssas_pbix.ssas.variations.find(1656)
    parents = expr.parents()
    assert len(parents) == 8
    assert {p.pbi_core_name() for p in parents} == {
        "Date Hierarchy",
        "5f3f7cd6-eb9b-4ba5-a040-09c1574c6f2b",
        "main_table",
        "Date",
        "LocalDateTable_f1dd39f2-2d79-466b-a0dd-7ac4c0d918ee",
        "date_Column",
        "a",
        "Model",
    }
    assert {p.__class__.__name__ for p in parents} == {"Hierarchy", "Relationship", "Table", "Column", "Model"}


def test_variation_alter(ssas_pbix):
    expr = ssas_pbix.ssas.variations.find(1656)
    expr.description = "test description"
    expr.alter()


def test_variation_delete():
    ssas_pbix = LocalReport.load_pbix("test_ssas.pbix")
    expr = ssas_pbix.ssas.variations.find(1656)
    expr.delete()


def test_variation_create():
    ssas_report = LocalReport.load_pbix("test_ssas.pbix")

    v = ssas_report.ssas.variations[0]
    return

    LocalVariation(
        name="New Variation",
        column_id=v.column_id,
        default_hierarchy_id=v.default_hierarchy_id,
        relationship_id=v.relationship_id,
        is_default=False,
    ).load(ssas_report.ssas)
