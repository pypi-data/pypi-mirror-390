def test_attribute_hierarchy_children(ssas_pbix):
    ah = ssas_pbix.ssas.attribute_hierarchies.find(51)
    children = ah.children()
    assert len(children) == 0


def test_attribute_hierarchy_parents(ssas_pbix):
    ah = ssas_pbix.ssas.attribute_hierarchies.find(51)
    parents = ah.parents()
    assert len(parents) == 3
    assert {p.pbi_core_name() for p in parents} == {
        "Model",
        "DateTableTemplate_b1b26bde-e081-4a41-aa17-61487b3e6e3e",
        "Date",
    }
    assert {p.__class__.__name__ for p in parents} == {"Model", "Table", "Column"}
