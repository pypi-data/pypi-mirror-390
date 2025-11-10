from pbi_core import LocalReport


def test_model_has_all_children(ssas_pbix):
    # Needed to ensure there aren't orphaned python objects pointing to now dead SSAS objects
    ssas_pbix.ssas.sync_from()

    children = ssas_pbix.ssas.model.children(recursive=True)
    for f in ssas_pbix.ssas.TABULAR_FIELDS():
        group = getattr(ssas_pbix.ssas, f)
        for item in group:
            assert item in children, f"Orphaned {f}: {item.pbi_core_name()} ({item.id})"


def test_model_alter(ssas_pbix):
    model = ssas_pbix.ssas.model
    model.description = "Updated model description"
    model.alter()


def test_model_rename():
    ssas_pbix = LocalReport.load_pbix("test_ssas.pbix")
    model = ssas_pbix.ssas.model
    model.name = "Renamed Model"
    model.rename()


def test_model_refresh(ssas_pbix):
    ssas_pbix.ssas.model.refresh()
