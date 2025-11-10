import datetime
from typing import TYPE_CHECKING

from attrs import field, setters

from pbi_core.attrs import define
from pbi_core.ssas.model_tables.enums.enums import DataType

from .column import Column
from .enums import Alignment, ColumnType, EncodingHint, SummarizedBy

if TYPE_CHECKING:
    from pbi_core.ssas.server import BaseTabularModel


@define()
class LocalColumn(Column):
    """Class for a Column that does not yet exist in SSAS.

    Generally created for it's load command which instantiates the remote object in SSAS
    and then returns that remote object.
    """

    id: int = field(default=-1, on_setattr=setters.frozen)
    table_id: int = field(default=-1)  # pyright: ignore[reportGeneralTypeIssues]
    alignment: Alignment = field(default=Alignment.DEFAULT, eq=True)
    attribute_hierarchy_id: int = field(default=-1, eq=True)
    column_storage_id: int = field(default=-1, eq=True)
    display_ordinal: int = field(default=-1, eq=True)
    encoding_hint: EncodingHint = field(default=EncodingHint.DEFAULT, eq=True)
    explicit_data_type: DataType = field(default=DataType.UNKNOWN, eq=True)
    inferred_data_type: int = field(default=-1, eq=True)
    is_available_in_mdx: bool = field(default=True, eq=True)
    is_default_image: bool = field(default=False, eq=True)
    is_default_label: bool = field(default=False, eq=True)
    is_hidden: bool = field(default=False, eq=True)
    is_key: bool = field(default=False, eq=True)
    is_nullable: bool = field(default=True, eq=True)
    is_unique: bool = field(default=False, eq=True)
    keep_unique_rows: bool = field(default=False, eq=True)
    summarize_by: SummarizedBy = field(default=SummarizedBy.NONE, eq=True)
    system_flags: int = field(default=0, eq=True)
    table_detail_position: int = field(default=-1, eq=True)
    type: ColumnType = field(default=ColumnType.CALCULATED, eq=True)

    modified_time: datetime.datetime = field(  # pyright: ignore[reportGeneralTypeIssues]
        factory=lambda: datetime.datetime.now(datetime.UTC),
        on_setattr=setters.frozen,
    )
    refreshed_time: datetime.datetime = field(  # pyright: ignore[reportGeneralTypeIssues]
        factory=lambda: datetime.datetime.now(datetime.UTC),
        on_setattr=setters.frozen,
    )
    structure_modified_time: datetime.datetime = field(  # pyright: ignore[reportGeneralTypeIssues]
        factory=lambda: datetime.datetime.now(datetime.UTC),
        on_setattr=setters.frozen,
    )

    def load(self, ssas: "BaseTabularModel") -> "Column":
        return self._create_helper(ssas, ssas.columns)

    @classmethod
    def _db_type_name(cls) -> str:
        return "Column"
