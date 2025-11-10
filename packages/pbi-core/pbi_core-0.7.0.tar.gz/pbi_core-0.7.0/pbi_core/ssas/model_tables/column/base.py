import datetime
from typing import Final
from uuid import UUID, uuid4

from attrs import field, setters

from pbi_core.attrs import define
from pbi_core.logging import get_logger
from pbi_core.ssas.model_tables.enums import DataState, DataType

from .enums import Alignment, ColumnType, DataCategory, EncodingHint, SummarizedBy

logger = get_logger()


@define()
class ColumnDTO:
    """A column of an SSAS table.

    PowerBI spec: [Power BI](https://learn.microsoft.com/en-us/analysis-services/tabular-models/column-properties-ssas-tabular?view=asallproducts-allversions)

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/00a9ec7a-5f4d-4517-8091-b370fe2dc18b)
    """

    alignment: Alignment = field(eq=True)
    attribute_hierarchy_id: int = field(eq=True)
    column_origin_id: int | None = field(eq=True, default=None)
    column_storage_id: int = field(eq=True)
    data_category: DataCategory | None = field(eq=True, default=None)
    description: str | None = field(eq=True, default=None)
    display_folder: str | None = field(eq=True, default=None)
    display_ordinal: int = field(eq=True)
    encoding_hint: EncodingHint = field(eq=True)
    error_message: Final[str | None] = field(
        eq=False,
        default=None,
    )  # error message is read-only, so should not be edited
    explicit_data_type: DataType = field(eq=True)
    explicit_name: str | None = field(eq=True, default=None)
    expression: str | int | None = field(eq=True, default=None)
    format_string: int | str | None = field(eq=True, default=None)
    inferred_data_type: int = field(eq=True)
    inferred_name: str | None = field(eq=True, default=None)
    is_available_in_mdx: bool = field(eq=True)
    is_default_image: bool = field(eq=True)
    is_default_label: bool = field(eq=True)
    is_hidden: bool = field(eq=True)
    is_key: bool = field(eq=True)
    is_nullable: bool = field(eq=True)
    is_unique: bool = field(eq=True)
    keep_unique_rows: bool = field(eq=True)
    lineage_tag: UUID = field(factory=uuid4, eq=True, repr=False)
    sort_by_column_id: int | None = field(eq=True, default=None)
    source_column: str | None = field(eq=True, default=None)
    state: Final[DataState] = field(eq=False, default=DataState.READY, on_setattr=setters.frozen)
    summarize_by: SummarizedBy = field(eq=True)
    system_flags: int = field(eq=True)
    table_id: Final[int] = field(eq=True, on_setattr=setters.frozen)  # pyright: ignore[reportIncompatibleVariableOverride]
    table_detail_position: int = field(eq=True)
    type: ColumnType = field(eq=True)

    modified_time: Final[datetime.datetime] = field(eq=False, repr=False)
    refreshed_time: Final[datetime.datetime] = field(eq=False, repr=False)
    structure_modified_time: Final[datetime.datetime] = field(eq=False, repr=False)
