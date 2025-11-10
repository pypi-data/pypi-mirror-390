from pbi_core import LocalReport
from pbi_core.ssas.model_tables.annotation.local import LocalAnnotation
from pbi_core.ssas.model_tables.enums.enums import ObjectType


def test_annotation_children(ssas_pbix):
    annotation = ssas_pbix.ssas.annotations.find(36)
    children = annotation.children()
    assert len(children) == 0


def test_annotation_parents(ssas_pbix):
    annotation = ssas_pbix.ssas.annotations.find(36)
    parents = annotation.parents()
    assert len(parents) == 3
    assert {p.pbi_core_name() for p in parents} == {
        "Model",
        "DateTableTemplate_b1b26bde-e081-4a41-aa17-61487b3e6e3e",
        "Date",
    }
    assert {p.__class__.__name__ for p in parents} == {"Model", "Table", "Column"}


def test_annotation_alter(ssas_pbix):
    annotation = ssas_pbix.ssas.annotations.find(36)
    annotation.value = "Updated Annotation Value"
    annotation.alter()


def test_annotation_delete():
    ssas_pbix = LocalReport.load_pbix("test_ssas.pbix")
    annotation = ssas_pbix.ssas.annotations.find(36)
    annotation.delete()


def test_annotation_create(ssas_pbix):
    table = ssas_pbix.ssas.tables.find(lambda t: t.is_hidden is False and t.is_private is False)
    m = LocalAnnotation(
        object_id=table.id,
        object_type=ObjectType.TABLE,
        name="New Annotation",
        value="This is a test annotation",
    ).load(ssas_pbix.ssas)
    assert m.id != -1
