import datetime
from typing import TYPE_CHECKING, Final

from attrs import field, setters

from pbi_core.attrs import define
from pbi_core.ssas.model_tables.base import SsasEditableRecord
from pbi_core.ssas.model_tables.base.lineage import LinkedEntity
from pbi_core.ssas.server import SsasCommands
from pbi_core.ssas.server._commands import BaseCommands

from .enums import MemberType

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables import Role


@define()
class RoleMembership(SsasEditableRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/dbecc1f4-142b-4765-8374-a4d4dc51313b)
    """

    identity_provider: str = field(eq=True)
    member_id: str = field(eq=True)
    member_name: str = field(eq=True)
    member_type: MemberType = field(eq=True)
    role_id: int = field(eq=True)

    modified_time: Final[datetime.datetime] = field(eq=False, on_setattr=setters.frozen, repr=False)

    _commands: BaseCommands = field(default=SsasCommands.role_membership, init=False, repr=False, eq=False)
    _discover_category: str = "TMSCHEMA_ROLE_MEMBERSHIPS"
    _db_field_names = {
        "id": "ID",
        "identity_provider": "IdentityProvider",
        "member_id": "MemberID",
        "member_name": "MemberName",
        "member_type": "MemberType",
        "role_id": "RoleID",
        "modified_time": "ModifiedTime",
    }

    def role(self) -> "Role":
        return self._tabular_model.roles.find(self.role_id)

    def children_base(self) -> frozenset["LinkedEntity"]:
        return LinkedEntity.from_iter(self.annotations(), by="annotation")

    def parents_base(self) -> frozenset["LinkedEntity"]:
        return LinkedEntity.from_iter({self.role()}, by="role")
