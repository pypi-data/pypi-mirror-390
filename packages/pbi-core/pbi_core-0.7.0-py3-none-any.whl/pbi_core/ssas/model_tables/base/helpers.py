from typing import cast

from attrs import Attribute, field, fields, setters
from structlog import get_logger

from pbi_core.attrs import define

logger = get_logger()


@define()
class HelperMixin:
    id: int = field(eq=True, repr=True, on_setattr=setters.frozen)
    """Unique identifier of the object."""
    _repr_name_field: str = field(default="name", repr=False, eq=False)

    @classmethod
    def _db_type_name(cls) -> str:
        return cls.__name__

    def pbi_core_name(self) -> str:
        """Returns the name displayed in the PBIX report.

        Uses the _repr_name_field to determine the field to use.
        Defaults to self.name
        """
        return str(getattr(self, self._repr_name_field))

    def __str__(self) -> str:
        display_fields = []
        for f in cast("list[Attribute]", fields(self.__class__)):
            if f.repr:
                val = getattr(self, f.name)
                if val != f.default:
                    if f.repr is True:
                        display_fields.append(f"{f.name}={val}")
                    else:
                        display_fields.append(f"{f.name}={f.repr(val)}")

        field_text = ", ".join(display_fields)
        return f"{self.__class__.__name__}({field_text})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.id}: {self.pbi_core_name()})"
