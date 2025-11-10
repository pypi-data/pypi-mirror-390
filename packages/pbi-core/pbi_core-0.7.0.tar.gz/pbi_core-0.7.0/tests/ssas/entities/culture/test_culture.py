from pbi_core import LocalReport
from pbi_core.ssas.model_tables.culture.local import LocalCulture


def test_culture_parents(ssas_pbix):
    culture = ssas_pbix.ssas.cultures.find({"name": "en-US"})
    parents = culture.parents()
    assert len(parents) == 1
    assert {p.pbi_core_name() for p in parents} == {"Model"}
    assert {p.__class__.__name__ for p in parents} == {"Model"}


def test_culture_children(ssas_pbix):
    culture = ssas_pbix.ssas.cultures.find({"name": "en-US"})
    children = culture.children()
    assert len(children) == 1
    assert {c.pbi_core_name() for c in children} == {"en-US"}
    assert {c.__class__.__name__ for c in children} == {"LinguisticMetadata"}


def test_culture_alter(ssas_pbix):
    culture = ssas_pbix.ssas.cultures.find({"name": "en-US"})
    culture.linguistic_metadata_id = None
    culture.alter()


def test_culture_rename():
    ssas_pbix = LocalReport.load_pbix("test_ssas.pbix")
    culture = ssas_pbix.ssas.cultures.find({"name": "en-US"})
    culture.name = "de-DE"
    culture.rename()


def test_culture_create():
    ssas_report = LocalReport.load_pbix("test_ssas.pbix")

    LocalCulture(
        name="New Culture",
        model_id=ssas_report.ssas.model.id,
    ).load(ssas_report.ssas)
