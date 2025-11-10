from typing import Any, ClassVar, Self

from attrs import Attribute, field, fields, setters
from structlog import get_logger

from pbi_core.attrs import BaseValidation, define

logger = get_logger()


@define()
class SsasMixin(BaseValidation):
    id: int = field(eq=True, repr=True, on_setattr=setters.frozen)
    _db_field_names: ClassVar[dict[str, str]]
    """Mapping of python attribute names to database field names.

    Example:
        For the Column class:
        {"ExplicitName": "explicit_name"...}
    """

    def get_altered_fields(self) -> list[Attribute]:
        """Returns a list of fields that have been altered since the last sync from SSAS."""
        ret = []
        for f in fields(self.__class__):
            if f.on_setattr is setters.frozen or f.name.startswith("_"):
                continue

            if self._original_data is None:
                ret.append(f)
                continue

            old_val = getattr(self._original_data, f.name, None)
            new_val = getattr(self, f.name)
            if old_val != new_val:
                ret.append(f)
        return ret

    def xml_fields(self) -> dict[str, Any]:
        base = self.model_dump()

        # All update/create commands require the ID field
        ret: dict[str, Any] = {
            "ID": self.id,
        }
        for f in self.get_altered_fields():
            db_name = self._db_field_names.get(f.name, f.name)
            ret[db_name] = base.get(f.name)
        return ret

    @classmethod
    def python_field_names(cls) -> dict[str, str]:
        return {v: k for k, v in cls._db_field_names.items()}

    @classmethod
    def model_validate(cls, data: dict) -> Self:  # pyright: ignore[reportIncompatibleMethodOverride]
        field_mapping = cls.python_field_names()
        try:
            formatted_data = {field_mapping[field_name]: field_value for field_name, field_value in data.items()}

        except KeyError:
            logger.exception("Error formatting data for model validation", cls=cls.__name__, data=data)
            raise
        return super().model_validate(formatted_data)
