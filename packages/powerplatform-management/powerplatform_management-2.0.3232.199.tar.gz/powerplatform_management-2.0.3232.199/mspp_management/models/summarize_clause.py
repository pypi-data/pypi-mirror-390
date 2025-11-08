from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .clause_base_class import ClauseBaseClass
    from .summarize_clause_summarize_clause_expression import SummarizeClause_SummarizeClauseExpression

from .clause_base_class import ClauseBaseClass

@dataclass
class SummarizeClause(ClauseBaseClass, Parsable):
    """
    KQL summarize operator: https://learn.microsoft.com/azure/data-explorer/kusto/query/summarizeoperator
    """
    # The SummarizeClauseExpression property
    summarize_clause_expression: Optional[SummarizeClause_SummarizeClauseExpression] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> SummarizeClause:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: SummarizeClause
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return SummarizeClause()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .clause_base_class import ClauseBaseClass
        from .summarize_clause_summarize_clause_expression import SummarizeClause_SummarizeClauseExpression

        from .clause_base_class import ClauseBaseClass
        from .summarize_clause_summarize_clause_expression import SummarizeClause_SummarizeClauseExpression

        fields: dict[str, Callable[[Any], None]] = {
            "SummarizeClauseExpression": lambda n : setattr(self, 'summarize_clause_expression', n.get_object_value(SummarizeClause_SummarizeClauseExpression)),
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
        writer.write_object_value("SummarizeClauseExpression", self.summarize_clause_expression)
    

