from pbi_core import LocalReport
from pbi_core.ssas.model_tables.column.enums import DataCategory
from pbi_core.ssas.model_tables.column.local import LocalColumn


def test_column_alteration(ssas_pbix: LocalReport) -> None:
    column = ssas_pbix.ssas.columns.find({"name": "Value"})

    column.data_category = DataCategory.POSTAL_CODE
    column.format_string = "#,0"
    column.alter()


def test_column_data(ssas_pbix: LocalReport) -> None:
    column = ssas_pbix.ssas.columns.find({"name": "Value"})
    data = column.data(head=10)
    assert len(data) == 10


def test_column_table(ssas_pbix: LocalReport) -> None:
    column = ssas_pbix.ssas.columns.find({"name": "Value"})
    table = column.table()
    assert table.name == "Table"


def test_column_parents(ssas_pbix: LocalReport) -> None:
    column = ssas_pbix.ssas.columns.find({"name": "Value"})
    parents = column.parents()
    assert len(parents) == 2
    assert {p.pbi_core_name() for p in parents} == {"Table", "Model"}


def test_column_children(ssas_pbix: LocalReport) -> None:
    column = ssas_pbix.ssas.columns.find({"name": "Value"})
    children = column.children()
    print({c.pbi_core_name() for c in children})
    assert len(children) == 4
    assert {c.pbi_core_name() for c in children} == {"Measure 4", "complicated_measure", "Value", "SummarizationSetBy"}
    assert {c.__class__.__name__ for c in children} == {"Annotation", "Measure", "AttributeHierarchy"}


def test_column_create(ssas_pbix: LocalReport) -> None:
    LocalColumn(
        explicit_name="New Column",
        table_id=ssas_pbix.ssas.tables[0].id,
        expression="1",
    ).load(ssas_pbix.ssas)
