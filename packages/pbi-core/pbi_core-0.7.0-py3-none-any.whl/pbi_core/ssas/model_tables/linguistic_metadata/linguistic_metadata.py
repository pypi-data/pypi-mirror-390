import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Final

from attrs import field, setters

from pbi_core.attrs import BaseValidation, Json, define
from pbi_core.ssas.model_tables.base import SsasEditableRecord
from pbi_core.ssas.model_tables.base.lineage import LinkedEntity
from pbi_core.ssas.server import SsasCommands
from pbi_core.ssas.server._commands import BaseCommands

if TYPE_CHECKING:
    from pbi_core.ssas.model_tables import Culture


class ContentType(Enum):
    XML = 0
    JSON = 1


@define(repr=True)
class EntityDefinitionBinding(BaseValidation):
    ConceptualEntity: str
    ConceptualProperty: str | None = None
    VariationSource: str | None = None
    VariationSet: str | None = None
    Hierarchy: str | None = None
    HierarchyLevel: str | None = None


@define(repr=True)
class EntityDefinition(BaseValidation):
    Binding: EntityDefinitionBinding


class TermSourceType(Enum):
    EXTERNAL = "External"


@define(repr=True)
class TermSource(BaseValidation):
    Type: TermSourceType | None = None
    Agent: str


class TermDefinitionState(Enum):
    SUGGESTED = "Suggested"
    GENERATED = "Generated"
    DELETED = "Deleted"


class TermDefinitionType(Enum):
    NOUN = "Noun"


@define(repr=True)
class TermDefinition(BaseValidation):
    State: TermDefinitionState | None = None
    Source: TermSource | None = None
    Weight: float | None = None
    Type: TermDefinitionType | None = None
    LastModified: datetime.datetime | None = None


class VisibilityValue(Enum):
    HIDDEN = "Hidden"


class VisibilityState(Enum):
    AUTHORED = "Authored"


@define(repr=True)
class VisibilityType(BaseValidation):
    Value: VisibilityValue
    State: VisibilityState | None = None


class NameTypeType(Enum):
    IDENTIFIER = "Identifier"
    NAME = "Name"


@define(repr=True)
class LinguisticMetadataEntity(BaseValidation):
    Weight: float | None = None
    State: TermDefinitionState
    Terms: list[dict[str, TermDefinition]] | None = None
    Definition: EntityDefinition | None = None
    Binding: EntityDefinitionBinding | None = None
    SemanticType: str | None = None
    Visibility: VisibilityType | None = None
    Hidden: bool = False
    NameType: NameTypeType | None = None
    Units: list[str] = field(factory=list)


@define(repr=True)
class RelationshipBinding(BaseValidation):
    ConceptualEntity: str


@define(repr=True)
class PhrasingAttributeRole(BaseValidation):
    Role: str


class RelationshipPhrasingState(Enum):
    GENERATED = "Generated"


# TODO: Subtype
@define(repr=True)
class PhrasingAttribute(BaseValidation):
    Adjective: PhrasingAttributeRole | None = None
    Measurement: PhrasingAttributeRole | None = None
    Object: PhrasingAttributeRole | None = None
    Subject: PhrasingAttributeRole | None = None
    Name: PhrasingAttributeRole | None = None

    PrepositionalPhrases: list[dict[str, Any]] = field(factory=list)
    Adjectives: list[dict[str, TermDefinition]] = field(factory=list)
    Antonyms: list[dict[str, TermDefinition]] = field(factory=list)
    Prepositions: list[dict[str, TermDefinition]] = field(factory=list)
    Verbs: list[dict[str, TermDefinition]] = field(factory=list)
    Nouns: list[dict[str, TermDefinition]] = field(factory=list)


@define(repr=True)
class RelationshipPhrasing(BaseValidation):
    Name: PhrasingAttribute | None = None
    Attribute: PhrasingAttribute | None = None
    Verb: PhrasingAttribute | None = None
    Adjective: PhrasingAttribute | None = None
    Preposition: PhrasingAttribute | None = None
    DynamicAdjective: PhrasingAttribute | None = None
    State: RelationshipPhrasingState | None = None
    Weight: float | None = None


@define(repr=True)
class RelationshipRoleEntity(BaseValidation):
    Entity: str


@define(repr=True)
class RelationshipRole(BaseValidation):
    Target: RelationshipRoleEntity
    Nouns: Any | None = None


@define(repr=True)
class SemanticSlot(BaseValidation):
    Where: PhrasingAttributeRole | None = None
    When: PhrasingAttributeRole | None = None


class ConditionOperator(Enum):
    EQUALS = "Equals"
    GREATER_THAN = "GreaterThan"


@define(repr=True)
class Condition(BaseValidation):
    Target: PhrasingAttributeRole
    Operator: ConditionOperator
    Value: dict[str, list[int | str]]


@define(repr=True)
class LinguisticMetadataRelationship(BaseValidation):
    Binding: RelationshipBinding = field(eq=True)
    Phrasings: list[RelationshipPhrasing] = field(factory=list, eq=True)
    Roles: dict[str, RelationshipRole | int] = field(eq=True)
    State: str | None = field(eq=True, default=None)  # TODO: Enum
    SemanticSlots: SemanticSlot | None = field(eq=True, default=None)
    Conditions: list[Condition] | None = field(eq=True, default=None)


@define(repr=True)
class LinguisticMetadataContent(BaseValidation):
    Version: str = field(eq=True)  # SemanticVersion
    Language: str = field(eq=True)
    DynamicImprovement: str | None = field(default=None, eq=True)
    Relationships: dict[str, LinguisticMetadataRelationship] | None = field(default=None, eq=str)
    Entities: dict[str, LinguisticMetadataEntity] | None = field(default=None, eq=str)
    Examples: list[dict[str, dict[str, str]]] | None = field(default=None, eq=str)


@define()
class LinguisticMetadata(SsasEditableRecord):
    """TBD.

    SSAS spec: [Microsoft](https://learn.microsoft.com/en-us/openspecs/sql_server_protocols/ms-ssas-t/f8924a45-70da-496a-947a-84b8d5beaae6)
    """

    content: Json[LinguisticMetadataContent] = field(eq=True)
    content_type: ContentType = field(eq=True)
    culture_id: int = field(eq=True)

    modified_time: Final[datetime.datetime] = field(eq=False, on_setattr=setters.frozen, repr=False)

    _commands: BaseCommands = field(
        default=SsasCommands.linguistic_metadata,
        init=False,
        repr=False,
        eq=False,
    )
    _discover_category: str = "TMSCHEMA_LINGUISTIC_METADATA"
    _db_field_names = {
        "id": "ID",
        "culture_id": "CultureID",
        "content": "Content",
        "modified_time": "ModifiedTime",
        "content_type": "ContentType",
    }

    def culture(self) -> "Culture":
        return self._tabular_model.cultures.find({"id": self.culture_id})

    def pbi_core_name(self) -> str:
        """Returns the name displayed in the PBIX report."""
        return self.culture().pbi_core_name()

    def children_base(self) -> frozenset["LinkedEntity"]:
        return LinkedEntity.from_iter(self.annotations(), by="annotation")

    def parents_base(self) -> frozenset["LinkedEntity"]:
        return LinkedEntity.from_iter({self.culture()}, by="culture")
