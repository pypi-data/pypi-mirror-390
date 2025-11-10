from pbi_core import LocalReport
from pbi_core.ssas.model_tables.refresh_policy.enums import PolicyType
from pbi_core.ssas.model_tables.refresh_policy.local import LocalRefreshPolicy


def test_refresh_policy_create():
    ssas_report = LocalReport.load_pbix("test_ssas.pbix")
    t = ssas_report.ssas.tables[1]

    query_definition = """
    let
        Source = List.Generate(() =>
    [Result = try country(1) otherwise null, Page=1],
    each [Result] <> null,
    each [Result = try country([Page] + 1) otherwise null, Page=[Page] + 1],
    each [Result]
    ),
        #"Converted to Table" = Table.FromList(Source, Splitter.SplitByNothing(), null, null, ExtraValues.Error),
        #"Expanded Column1" = Table.ExpandTableColumn(#"Converted to Table", "Column1", {"iso2Code", "name", "region", "adminregion", "incomeLevel", "lendingType", "capitalCity", "longitude", "latitude", "Attribute:id"}, {"Column1.iso2Code", "Column1.name", "Column1.region", "Column1.adminregion", "Column1.incomeLevel", "Column1.lendingType", "Column1.capitalCity", "Column1.longitude", "Column1.latitude", "Column1.Attribute:id"}),
        #"Column1 region" = #"Expanded Column1"{11}[Column1.region],
        #"Changed Type" = Table.TransformColumnTypes(#"Column1 region",{{"Element:Text", type text}, {"Attribute:id", type text}, {"Attribute:iso2code", type text}}),
        #"Renamed Columns" = Table.RenameColumns(#"Changed Type",{{"Element:Text", "text_elements"}})
    in
        #"Renamed Columns"
    """  # noqa: E501
    source_query_definition = """
    let
        strRangeStart = DateTime.ToText(RangeStart,[Format="yyyy-MM-dd'T'HH:mm:ss'Z'", Culture="en-US"]),
        strRangeEnd = DateTime.ToText(RangeEnd,[Format="yyyy-MM-dd'T'HH:mm:ss'Z'", Culture="en-US"]),

        Source = List.Generate(() =>
    [Result = try country(1) otherwise null, Page=1],
    each [Result] <> null,
    each [Result = try country([Page] + 1) otherwise null, Page=[Page] + 1],
    each [Result]
    ),
        #"Converted to Table" = Table.FromList(Source, Splitter.SplitByNothing(), null, null, ExtraValues.Error),
        #"Expanded Column1" = Table.ExpandTableColumn(#"Converted to Table", "Column1", {"iso2Code", "name", "region", "adminregion", "incomeLevel", "lendingType", "capitalCity", "longitude", "latitude", "Attribute:id"}, {"Column1.iso2Code", "Column1.name", "Column1.region", "Column1.adminregion", "Column1.incomeLevel", "Column1.lendingType", "Column1.capitalCity", "Column1.longitude", "Column1.latitude", "Column1.Attribute:id"}),
        #"Column1 region" = #"Expanded Column1"{11}[Column1.region],
        #"Changed Type" = Table.TransformColumnTypes(#"Column1 region",{{"Element:Text", type text}, {"Attribute:id", type text}, {"Attribute:iso2code", type text}}),
        #"Renamed Columns" = Table.RenameColumns(#"Changed Type",{{"Element:Text", "text_elements"}})
    in
        #"Renamed Columns"
    """  # noqa: E501

    LocalRefreshPolicy(
        table_id=t.id,
        policy_type=PolicyType.BASIC,
        polling_expression=query_definition,
        source_expression=source_query_definition,
    ).load(ssas_report.ssas)
