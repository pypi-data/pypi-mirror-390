from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .clause_base_class import ClauseBaseClass

from .clause_base_class import ClauseBaseClass

@dataclass
class ProjectClause(ClauseBaseClass, Parsable):
    """
    KQL project operator: https://learn.microsoft.com/azure/data-explorer/kusto/query/projectoperator
    """
    # The FieldList property
    field_list: Optional[list[str]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ProjectClause:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ProjectClause
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ProjectClause()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .clause_base_class import ClauseBaseClass

        from .clause_base_class import ClauseBaseClass

        fields: dict[str, Callable[[Any], None]] = {
            "FieldList": lambda n : setattr(self, 'field_list', n.get_collection_of_primitive_values(str)),
        }
        super_fields = super().get_field_deserializers()
        fields.update(super_fields)
        return fields
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        super().serialize(writer)
        writer.write_collection_of_primitive_values("FieldList", self.field_list)
    

