from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .main import LayoutNode


def _xpath_attrs(parent: "LayoutNode", child: "LayoutNode", xpath: list[str | int]) -> list[str | int] | None:
    for attr in parent.data_attributes():
        val = getattr(parent, attr.name)
        ret = _get_xpath(val, child, xpath=[*xpath, attr.name])
        if ret is not None:
            return ret
    return None


def _xpath_list(parent: list, child: "LayoutNode", xpath: list[str | int]) -> list[str | int] | None:
    for i, val in enumerate(parent):
        ret = _get_xpath(val, child, xpath=[*xpath, i])
        if ret is not None:
            return ret
    return None


def _xpath_dict(parent: dict, child: "LayoutNode", xpath: list[str | int]) -> list[str | int] | None:
    for key, val in parent.items():
        ret = _get_xpath(val, child, xpath=[*xpath, key])
        if ret is not None:
            return ret
    return None


def _get_xpath(  # too complex, but it's actually not that complex
    parent: "LayoutNode | list | dict",
    child: "LayoutNode",
    xpath: list[str | int] | None = None,
) -> list[str | int] | None:
    from .main import LayoutNode  # noqa: PLC0415

    xpath = xpath or []
    if parent is child:
        return xpath

    if isinstance(parent, LayoutNode):
        return _xpath_attrs(parent, child, xpath)
    if isinstance(parent, list):
        return _xpath_list(parent, child, xpath)
    if isinstance(parent, dict):
        return _xpath_dict(parent, child, xpath)
    return None


class XPathMixin:
    def find_xpath(self, xpath: list[str | int]) -> "LayoutNode":
        """Find a node in the layout using an XPath-like list of attributes.

        Note: This method currently uses a DFS approach to find the node.
            Eventually, I'll find a way to type-safely include element parents in the LayoutNode.

        Raises:
            TypeError: If the XPath is invalid or if the node is not found.

        """
        from .main import LayoutNode  # noqa: PLC0415

        if len(xpath) == 0:
            assert isinstance(
                self,
                LayoutNode,
            )  # needed for type checking, since the Mixin doesn't explicitly know it's mixed into LayoutNode
            return self

        next_step = xpath.pop(0)
        if isinstance(next_step, int):
            msg = f"Cannot index {self.__class__.__name__} with an integer: {next_step}"
            raise TypeError(msg)
        attr = getattr(self, next_step)

        while isinstance(attr, (dict, list)):
            next_step = xpath.pop(0)
            attr = attr[next_step]  # pyright: ignore[reportCallIssue, reportArgumentType]

        if not isinstance(attr, LayoutNode):
            msg = f"Cannot index {self.__class__.__name__} with a non-LayoutNode: {attr}"
            raise TypeError(msg)
        return attr.find_xpath(xpath)

    def get_xpath(self, parent: "LayoutNode") -> list[str | int]:
        """Get the [XPath](https://developer.mozilla.org/en-US/docs/Web/XML/XPath) of this node.

        Args:
            parent (LayoutNode): The parent node to which the XPath is relative.

        Raises:
            ValueError: If the node is not found in the parent.

        """
        from .main import LayoutNode  # noqa: PLC0415

        assert isinstance(
            self,
            LayoutNode,
        )  # needed for type checking, since the Mixin doesn't explicitly know it's mixed into LayoutNode
        ret = _get_xpath(parent, self)
        if ret is None:
            msg = f"Node {self} not found in parent {parent}"
            raise ValueError(msg)
        return ret
