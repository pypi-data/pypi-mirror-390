from pbi_core import LocalReport
from pbi_core.ssas.model_tables.detail_row_definition.local import LocalDetailRowDefinition
from pbi_core.ssas.model_tables.enums.enums import ObjectType


def test_detail_row_definition_create():
    ssas_report = LocalReport.load_pbix("test_ssas.pbix")
    return
    column = next(c for c in ssas_report.ssas.columns if c.is_normal())
    LocalDetailRowDefinition(
        expression="1",
        object_id=column.id,
        object_type=ObjectType.COLUMN,
    ).load(ssas_report.ssas)
