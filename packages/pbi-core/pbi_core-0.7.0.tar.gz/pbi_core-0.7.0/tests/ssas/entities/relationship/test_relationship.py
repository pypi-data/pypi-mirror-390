from pbi_core import LocalReport
from pbi_core.ssas.model_tables.relationship.enums import FromCardinality, ToCardinality
from pbi_core.ssas.model_tables.relationship.local import LocalRelationship


def test_relationship_children(ssas_pbix):
    expr = ssas_pbix.ssas.relationships.find(1646)
    children = expr.children()
    assert len(children) == 1
    assert {c.pbi_core_name() for c in children} == {"Variation"}
    assert {c.__class__.__name__ for c in children} == {"Variation"}


def test_relationship_parents(ssas_pbix):
    expr = ssas_pbix.ssas.relationships.find(1646)
    parents = expr.parents()
    assert len(parents) == 6
    assert {p.pbi_core_name() for p in parents} == {
        "a",
        "main_table",
        "LocalDateTable_f1dd39f2-2d79-466b-a0dd-7ac4c0d918ee",
        "Model",
        "date_Column",
        "Date",
    }
    assert {p.__class__.__name__ for p in parents} == {"Column", "Table", "Model"}


def test_relationship_alter(ssas_pbix):
    expr = ssas_pbix.ssas.relationships.find(1646)
    expr.name = "test name"
    expr.alter()


def test_relationship_delete():
    ssas_pbix = LocalReport.load_pbix("test_ssas.pbix")
    expr = ssas_pbix.ssas.relationships.find(1646)
    expr.delete()


def test_relationship_create():
    ssas_report = LocalReport.load_pbix("test_ssas.pbix")
    c1 = ssas_report.ssas.columns.find(lambda c: c.name() == "Value" and c.table().name == "Table")
    c2 = ssas_report.ssas.columns.find(lambda c: c.name() == "a" and c.table().name == "main_table")

    LocalRelationship(
        name="New Relationship",
        from_column_id=c1.id,
        from_table_id=c1.table().id,
        to_column_id=c2.id,
        to_table_id=c2.table().id,
        from_cardinality=FromCardinality.MANY,
        to_cardinality=ToCardinality.MANY,
        model_id=ssas_report.ssas.model.id,
    ).load(ssas_report.ssas)
