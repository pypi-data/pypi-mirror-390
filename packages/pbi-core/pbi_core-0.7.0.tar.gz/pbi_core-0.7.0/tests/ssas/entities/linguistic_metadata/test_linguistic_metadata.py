from pbi_core import LocalReport
from pbi_core.ssas.model_tables.culture.local import LocalCulture
from pbi_core.ssas.model_tables.linguistic_metadata.linguistic_metadata import ContentType
from pbi_core.ssas.model_tables.linguistic_metadata.local import LocalLinguisticMetadata


def test_linguistic_metadata_children(ssas_pbix):
    expr = ssas_pbix.ssas.linguistic_metadata.find(2944)
    children = expr.children()
    assert len(children) == 0


def test_linguistic_metadata_parents(ssas_pbix: LocalReport):
    expr = ssas_pbix.ssas.linguistic_metadata.find(2944)
    parents = expr.parents()
    assert len(parents) == 2
    assert {p.pbi_core_name() for p in parents} == {"Model", "en-US"}
    assert {p.__class__.__name__ for p in parents} == {"Model", "Culture"}


def test_linguistic_metadata_alter(ssas_pbix):
    expr = ssas_pbix.ssas.linguistic_metadata.find(2944)
    expr.content.Language = "de-DE"
    expr.alter()


def test_linguistic_metadata_delete():
    ssas_pbix = LocalReport.load_pbix("test_ssas.pbix")
    expr = ssas_pbix.ssas.linguistic_metadata.find(2944)
    expr.delete()


def test_linguistic_metadata_create():
    ssas_report = LocalReport.load_pbix("test_ssas.pbix")
    c = LocalCulture(
        name="New Culture",
        model_id=ssas_report.ssas.model.id,
    ).load(ssas_report.ssas)
    LocalLinguisticMetadata(
        culture_id=c.id,
        content_type=ContentType.JSON,
        content=ssas_report.ssas.linguistic_metadata[0].content,
    ).load(ssas_report.ssas)
