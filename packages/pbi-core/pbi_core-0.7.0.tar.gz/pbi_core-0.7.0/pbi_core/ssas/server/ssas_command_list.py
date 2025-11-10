import pathlib

from ._commands import BaseCommands, ModelCommands, RefreshCommands, RenameCommands

COMMAND_DIR: pathlib.Path = pathlib.Path(__file__).parent / "command_templates"

commands: dict[str, dict[str, str]] = {
    folder.name: {f.name: f.read_text() for f in folder.iterdir() if f.is_file()}
    for folder in (COMMAND_DIR / "schema").iterdir()
    if folder.is_dir()
}


class SsasCommands:
    annotation = RenameCommands.new("annotation", commands["Annotations"])
    calculation_group = BaseCommands.new("calculation_group", commands["CalculationGroup"])
    calculation_item = RenameCommands.new("calculation_item", commands["CalculationItems"])
    column = RenameCommands.new("column", commands["Columns"])
    column_permission = BaseCommands.new("column_permission", commands["ColumnPermissions"])
    culture = RenameCommands.new("culture", commands["Cultures"])
    data_source = RenameCommands.new("data_source", commands["DataSources"])
    detail_row_definition = BaseCommands.new("detail_row_definition", commands["DetailRowsDefinition"])
    expression = RenameCommands.new("expression", commands["Expressions"])
    extended_property = RenameCommands.new("extended_property", commands["ExtendedProperties"])
    format_string_definition = BaseCommands.new("format_string_definition", commands["FormatStringDefinitions"])
    hierarchy = RenameCommands.new("hierarchy", commands["Hierarchies"])
    kpi = BaseCommands.new("kpi", commands["Kpis"])
    level = RenameCommands.new("level", commands["Levels"])
    linguistic_metadata = BaseCommands.new("linguistic_metadata", commands["LinguisticMetadata"])
    measure = RenameCommands.new("measure", commands["Measures"])
    model = ModelCommands.new("model", commands["Model"])
    object_translation = BaseCommands.new("object_translation", commands["ObjectTranslations"])
    partition = RefreshCommands.new("partition", commands["Partitions"])
    perspective_column = BaseCommands.new("perspective_column", commands["PerspectiveColumns"])
    perspective_hierarchy = BaseCommands.new("perspective_hierarchy", commands["PerspectiveHierarchies"])
    perspective_measure = BaseCommands.new("perspective_measure", commands["PerspectiveMeasures"])
    perspective = RenameCommands.new("perspective", commands["Perspectives"])
    perspective_table = BaseCommands.new("perspective_table", commands["PerspectiveTables"])
    query_group = BaseCommands.new("query_group", commands["QueryGroups"])
    refresh_policy = BaseCommands.new("refresh_policy", commands["RefreshPolicy"])
    relationship = RenameCommands.new("relationship", commands["Relationships"])
    role_membership = BaseCommands.new("role_membership", commands["RoleMemberships"])
    role = RenameCommands.new("role", commands["Roles"])
    table_permission = BaseCommands.new("table_permission", commands["TablePermissions"])
    table = RefreshCommands.new("table", commands["Tables"])
    variation = RenameCommands.new("variation", commands["Variations"])
