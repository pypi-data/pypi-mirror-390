from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .clause_base_class import ClauseBaseClass
    from .sub_query import SubQuery

from .clause_base_class import ClauseBaseClass

@dataclass
class JoinClause(ClauseBaseClass, Parsable):
    """
    KQL join operator (join kinds): https://learn.microsoft.com/azure/data-explorer/kusto/query/joinoperator
    """
    # KQL join kind (e.g., innerunique, leftouter)
    join_kind: Optional[str] = None
    # The LeftColumnName property
    left_column_name: Optional[str] = None
    # The RightColumnName property
    right_column_name: Optional[str] = None
    # The RightTable property
    right_table: Optional[SubQuery] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> JoinClause:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: JoinClause
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return JoinClause()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .clause_base_class import ClauseBaseClass
        from .sub_query import SubQuery

        from .clause_base_class import ClauseBaseClass
        from .sub_query import SubQuery

        fields: dict[str, Callable[[Any], None]] = {
            "JoinKind": lambda n : setattr(self, 'join_kind', n.get_str_value()),
            "LeftColumnName": lambda n : setattr(self, 'left_column_name', n.get_str_value()),
            "RightColumnName": lambda n : setattr(self, 'right_column_name', n.get_str_value()),
            "RightTable": lambda n : setattr(self, 'right_table', n.get_object_value(SubQuery)),
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
        writer.write_str_value("JoinKind", self.join_kind)
        writer.write_str_value("LeftColumnName", self.left_column_name)
        writer.write_str_value("RightColumnName", self.right_column_name)
        writer.write_object_value("RightTable", self.right_table)
    

