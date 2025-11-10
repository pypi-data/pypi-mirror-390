from collections.abc import Iterable
from typing import TYPE_CHECKING, Literal

from structlog import get_logger

from pbi_core.attrs import define
from pbi_core.lineage import LineageNode

if TYPE_CHECKING:
    from .ssas_tables import SsasTable
logger = get_logger()


@define()
class LinkedEntity:
    val: "SsasTable"
    """The parent/child SsasTable entity."""
    by: str
    """The field/method by which the entity is linked."""

    @staticmethod
    def from_iter(vals: Iterable["SsasTable | None"], by: str) -> frozenset["LinkedEntity"]:
        return frozenset(LinkedEntity(val=v, by=by) for v in vals if v is not None)


@define()
class LineageMixin:
    def parents_base(self) -> frozenset["LinkedEntity"]:  # noqa: PLR6301
        return frozenset()

    def children_base(self) -> frozenset["LinkedEntity"]:  # noqa: PLR6301
        return frozenset()

    def parents(self, *, recursive: bool = True) -> frozenset["SsasTable"]:
        base = self.parents_base()
        if recursive:
            ret: set[SsasTable] = set()
            for b in base:
                ret.add(b.val)
                ret.update(b.val.parents(recursive=True))
            return frozenset(ret)
        return frozenset(le.val for le in base)

    def children(self, *, recursive: bool = True) -> frozenset["SsasTable"]:
        base = self.children_base()
        if recursive:
            ret = set()
            for b in base:
                ret.add(b.val)
                ret.update(b.val.children(recursive=True))
            return frozenset(ret)
        return frozenset(le.val for le in base)

    def get_lineage(self, lineage_type: Literal["children", "parents"]) -> LineageNode:
        """Creates a lineage node tracking the data parents/children of a record."""
        ancestors = self.children_base() if lineage_type == "children" else self.parents_base()
        relatives = [a.val.get_lineage(lineage_type) for a in ancestors]
        for r, a in zip(relatives, ancestors, strict=True):
            r.by = a.by
        return LineageNode(self, lineage_type, relatives)
