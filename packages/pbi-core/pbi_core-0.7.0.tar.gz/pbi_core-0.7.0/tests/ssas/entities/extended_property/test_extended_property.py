from pbi_core import LocalReport
from pbi_core.ssas.model_tables.enums.enums import ObjectType
from pbi_core.ssas.model_tables.extended_property.extended_property import ExtendedPropertyType, ExtendedPropertyValue
from pbi_core.ssas.model_tables.extended_property.local import LocalExtendedProperty


def test_extended_property_create():
    ssas_report = LocalReport.load_pbix("test_ssas.pbix")
    column = next(c for c in ssas_report.ssas.columns if c.is_normal())
    LocalExtendedProperty(
        object_id=column.id,
        object_type=ObjectType.COLUMN,
        name="Test Extended Property",
        type=ExtendedPropertyType.JSON,
        value=ExtendedPropertyValue(
            version=1,
            daxTemplateName="Test Template",
            groupedColumns=None,
            binningMetadata=None,
        ),
    ).load(ssas_report.ssas)
