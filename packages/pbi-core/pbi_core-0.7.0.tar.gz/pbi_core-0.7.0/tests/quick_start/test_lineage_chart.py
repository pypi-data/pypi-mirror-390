

def test_lineage_chart(ssas_pbix):
    col = ssas_pbix.ssas.measures.find({"name": "Measure 4"})
    col.get_lineage("parents").to_mermaid()
