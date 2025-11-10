from pbi_core import LocalReport
from pbi_core.ssas.model_tables.enums.enums import ObjectType
from pbi_core.ssas.model_tables.object_translation.enums import Property
from pbi_core.ssas.model_tables.object_translation.local import LocalObjectTranslation


def test_object_translation_create():
    ssas_report = LocalReport.load_pbix("test_ssas.pbix")
    LocalObjectTranslation(
        culture_id=ssas_report.ssas.cultures[0].id,
        object_id=ssas_report.ssas.measures[0].id,
        object_type=ObjectType.MEASURE,
        property=Property.CAPTION,
        value="New Folder",
        altered=True,
    ).load(ssas_report.ssas)
