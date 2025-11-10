import datetime
from typing import TYPE_CHECKING, Final

from attrs import field, setters

from pbi_core.attrs import define
from pbi_core.ssas.model_tables.base import SsasRenameRecord
from pbi_core.ssas.model_tables.base.lineage import LinkedEntity
from pbi_core.ssas.server import SsasCommands
from pbi_core.ssas.server._commands import RenameCommands

from .enums import ModelPermission

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables import Model, RoleMembership, TablePermission


@define()
class Role(SsasRenameRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/94a8e609-b1ae-4814-b8dc-963005eebade)
    """

    description: str | None = field(default=None, eq=True)
    model_id: int = field(eq=True, repr=False)
    model_permission: ModelPermission = field(eq=True, default=ModelPermission.READ)
    name: str = field(eq=True)

    modified_time: Final[datetime.datetime] = field(eq=False, on_setattr=setters.frozen, repr=False)

    _commands: RenameCommands = field(default=SsasCommands.role, init=False, repr=False, eq=False)
    _discover_category: str = "TMSCHEMA_ROLES"
    _db_field_names = {
        "id": "ID",
        "model_id": "ModelID",
        "name": "Name",
        "model_permission": "ModelPermission",
        "modified_time": "ModifiedTime",
    }

    def model(self) -> "Model":
        return self._tabular_model.model

    def table_permissions(self) -> set["TablePermission"]:
        return self._tabular_model.table_permissions.find_all({"role_id": self.id})

    def role_memberships(self) -> set["RoleMembership"]:
        return self._tabular_model.role_memberships.find_all({"role_id": self.id})

    def parents_base(self) -> frozenset["LinkedEntity"]:
        return LinkedEntity.from_iter({self.model()}, by="model")

    def children_base(self) -> frozenset["LinkedEntity"]:
        return (
            LinkedEntity.from_iter(
                self.table_permissions(),
                by="table_permission",
            )
            | LinkedEntity.from_iter(self.role_memberships(), by="role_membership")
            | LinkedEntity.from_iter(
                self.annotations(),
                by="annotation",
            )
        )
