from pbi_core.attrs import define
from pbi_core.static_files.layout.layout_node import LayoutNode


@define()
class ProtoSource(LayoutNode):
    Source: str


@define()
class ProtoSourceRef(LayoutNode):
    SourceRef: ProtoSource
