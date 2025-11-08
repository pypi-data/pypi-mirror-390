from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .clause_base_class import ClauseBaseClass
    from .order_by_clause_field_names_asc_desc import OrderByClause_FieldNamesAscDesc

from .clause_base_class import ClauseBaseClass

@dataclass
class OrderByClause(ClauseBaseClass, Parsable):
    """
    KQL sort by operator: https://learn.microsoft.com/en-us/kusto/query/sort-operator
    """
    # The FieldNamesAscDesc property
    field_names_asc_desc: Optional[OrderByClause_FieldNamesAscDesc] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> OrderByClause:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: OrderByClause
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return OrderByClause()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .clause_base_class import ClauseBaseClass
        from .order_by_clause_field_names_asc_desc import OrderByClause_FieldNamesAscDesc

        from .clause_base_class import ClauseBaseClass
        from .order_by_clause_field_names_asc_desc import OrderByClause_FieldNamesAscDesc

        fields: dict[str, Callable[[Any], None]] = {
            "FieldNamesAscDesc": lambda n : setattr(self, 'field_names_asc_desc', n.get_object_value(OrderByClause_FieldNamesAscDesc)),
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
        writer.write_object_value("FieldNamesAscDesc", self.field_names_asc_desc)
    

