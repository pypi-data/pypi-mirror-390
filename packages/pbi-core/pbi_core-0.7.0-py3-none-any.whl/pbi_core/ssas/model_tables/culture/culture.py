import datetime
from typing import TYPE_CHECKING, Final

from attrs import field, setters

from pbi_core.attrs import define
from pbi_core.ssas.model_tables.base import SsasRenameRecord
from pbi_core.ssas.model_tables.base.lineage import LinkedEntity
from pbi_core.ssas.server import RenameCommands, SsasCommands

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables import LinguisticMetadata, Model


@define()
class Culture(SsasRenameRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/d3770118-47bf-4304-9edf-8025f4820c45)
    """

    linguistic_metadata_id: int | None = field(eq=True, default=None)
    model_id: int = field(eq=True, repr=False)
    name: str = field(eq=True)

    modified_time: Final[datetime.datetime] = field(eq=False, on_setattr=setters.frozen, repr=False)
    structure_modified_time: Final[datetime.datetime] = field(eq=False, on_setattr=setters.frozen, repr=False)

    _commands: RenameCommands = field(default=SsasCommands.culture, init=False, repr=False, eq=False)
    _discover_category: str = "TMSCHEMA_CULTURES"
    _db_field_names = {
        "id": "ID",
        "model_id": "ModelID",
        "name": "Name",
        "linguistic_metadata_id": "LinguisticMetadataID",
        "modified_time": "ModifiedTime",
        "structure_modified_time": "StructureModifiedTime",
    }

    def linguistic_metadata(self) -> "LinguisticMetadata | None":
        # Although standard cultures always have linguistic metadata, you are able to delete it's linguistic metadata
        # via XMLA.
        if self.linguistic_metadata_id is None:
            return None
        return self._tabular_model.linguistic_metadata.find({"id": self.linguistic_metadata_id})

    def model(self) -> "Model":
        return self._tabular_model.model

    def children_base(self) -> frozenset["LinkedEntity"]:
        """Is based on the culture spec, since it's a little ambiguous just from the data."""
        return LinkedEntity.from_iter(self.annotations(), by="annotation") | LinkedEntity.from_iter(
            {self.linguistic_metadata()},
            by="linguistic_metadata",
        )

    def parents_base(self) -> frozenset["LinkedEntity"]:
        return LinkedEntity.from_iter({self.model()}, by="model")
