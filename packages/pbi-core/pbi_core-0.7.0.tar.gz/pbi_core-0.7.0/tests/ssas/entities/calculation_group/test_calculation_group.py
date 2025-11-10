from pbi_core.ssas.model_tables.calculation_group.local import LocalCalculationGroup


def test_calculation_group_create(ssas_pbix):
    table = ssas_pbix.ssas.tables.find(lambda t: t.is_hidden is False and t.is_private is False)
    return  # TODO: create an example where a partition with a sourcetype of CalculationGroup
    m = LocalCalculationGroup(
        table_id=table.id,
        description="New Calculation Group",
        precedence=1,
    ).load(ssas_pbix.ssas)
    assert m.id != -1
