import datetime
from typing import TYPE_CHECKING, Final

from attrs import field, setters

from pbi_core.attrs import define
from pbi_core.ssas.model_tables.base import SsasRenameRecord
from pbi_core.ssas.model_tables.base.lineage import LinkedEntity
from pbi_core.ssas.server import SsasCommands
from pbi_core.ssas.server._commands import RenameCommands

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables import Model


@define()
class Perspective(SsasRenameRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/8bbe314e-f308-4732-875c-9530a1b0fe95)
    """

    description: int = field(eq=True)
    model_id: int = field(eq=True)
    name: str = field(eq=True)

    modified_time: Final[datetime.datetime] = field(eq=False, on_setattr=setters.frozen, repr=False)

    _commands: RenameCommands = field(default=SsasCommands.perspective, init=False, repr=False, eq=False)
    _discover_category: str = "TMSCHEMA_PERSPECTIVES"
    _db_field_names = {}

    def model(self) -> "Model":
        return self._tabular_model.model

    def children_base(self) -> frozenset[LinkedEntity]:
        return LinkedEntity.from_iter(self.annotations(), by="annotation")

    def parents_base(self) -> frozenset[LinkedEntity]:
        return LinkedEntity.from_iter({self.model()}, by="model")
