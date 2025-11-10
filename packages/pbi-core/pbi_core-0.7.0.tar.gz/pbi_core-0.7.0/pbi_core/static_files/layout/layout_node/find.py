from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from .main import LayoutNode

LAYOUT_ENCODING = "utf-16-le"


T = TypeVar("T", bound="LayoutNode")


def _gen_find_filter_callable(attributes: dict[str, Any] | Callable[[T], bool] | None) -> Callable[[T], bool]:
    if attributes is None:
        attribute_lambda: Callable[[T], bool] = lambda _: True  # noqa: E731
    elif isinstance(attributes, dict):
        attribute_lambda = lambda x: all(  # noqa: E731
            getattr(x, field_name) == field_value for field_name, field_value in attributes.items()
        )
    else:
        attribute_lambda = attributes
    return attribute_lambda


class FindMixin:
    def find_all(
        self,
        cls_type: type[T] | tuple[type[T], ...],
        attributes: dict[str, Any] | Callable[[T], bool] | None = None,
    ) -> list["T"]:
        from .main import LayoutNode  # noqa: PLC0415

        assert isinstance(self, LayoutNode)

        attribute_lambda = _gen_find_filter_callable(attributes)
        return _find_all(self, cls_type, attribute_lambda)

    def find(
        self,
        cls_type: type[T] | tuple[type[T], ...],
        attributes: dict[str, Any] | Callable[[T], bool] | None = None,
    ) -> "T":
        from .main import LayoutNode  # noqa: PLC0415

        assert isinstance(self, LayoutNode)

        attribute_lambda = _gen_find_filter_callable(attributes)
        candidate = _find(self, cls_type, attribute_lambda)
        if candidate is not None:
            return candidate

        msg = f"Object not found: {cls_type}"
        raise ValueError(msg)


def _find_all(
    val: "list[Any] | dict[str, Any] | LayoutNode",
    cls_type: type[T] | tuple[type[T], ...],
    attribute_lambda: Callable[[T], bool],
) -> list[T]:
    from .main import LayoutNode  # noqa: PLC0415

    ret: list[T] = []
    if isinstance(val, LayoutNode):
        if isinstance(val, cls_type) and attribute_lambda(val):
            ret.append(val)
        for attr in val.data_attributes():
            child_val = getattr(val, attr.name)
            ret.extend(_find_all(child_val, cls_type, attribute_lambda))
    elif isinstance(val, list):
        for item in val:
            ret.extend(_find_all(item, cls_type, attribute_lambda))
    elif isinstance(val, dict):
        for item in val.values():
            ret.extend(_find_all(item, cls_type, attribute_lambda))
    return ret


def _find(  # noqa: C901
    val: "list[Any] | dict[str, Any] | LayoutNode",
    cls_type: type[T] | tuple[type[T], ...],
    attribute_lambda: Callable[[T], bool],
) -> T | None:
    from .main import LayoutNode  # noqa: PLC0415

    if isinstance(val, LayoutNode):
        if isinstance(val, cls_type) and attribute_lambda(val):
            return val
        for attr in val.data_attributes():
            child_val = getattr(val, attr.name)
            if candidate := _find(child_val, cls_type, attribute_lambda):
                return candidate
    elif isinstance(val, list):
        for item in val:
            if candidate := _find(item, cls_type, attribute_lambda):
                return candidate
    elif isinstance(val, dict):
        for item in val.values():
            if candidate := _find(item, cls_type, attribute_lambda):
                return candidate
    return None
