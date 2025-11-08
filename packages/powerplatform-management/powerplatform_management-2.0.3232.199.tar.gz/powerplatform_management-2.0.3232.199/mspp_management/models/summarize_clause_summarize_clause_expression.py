from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .summarize_clause_summarize_clause_expression_operator_name import SummarizeClause_SummarizeClauseExpression_OperatorName

@dataclass
class SummarizeClause_SummarizeClauseExpression(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The FieldList property
    field_list: Optional[list[str]] = None
    # For argmax, the field to maximize; for count, the alias
    operator_field_name: Optional[str] = None
    # The OperatorName property
    operator_name: Optional[SummarizeClause_SummarizeClauseExpression_OperatorName] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> SummarizeClause_SummarizeClauseExpression:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: SummarizeClause_SummarizeClauseExpression
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return SummarizeClause_SummarizeClauseExpression()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .summarize_clause_summarize_clause_expression_operator_name import SummarizeClause_SummarizeClauseExpression_OperatorName

        from .summarize_clause_summarize_clause_expression_operator_name import SummarizeClause_SummarizeClauseExpression_OperatorName

        fields: dict[str, Callable[[Any], None]] = {
            "FieldList": lambda n : setattr(self, 'field_list', n.get_collection_of_primitive_values(str)),
            "OperatorFieldName": lambda n : setattr(self, 'operator_field_name', n.get_str_value()),
            "OperatorName": lambda n : setattr(self, 'operator_name', n.get_enum_value(SummarizeClause_SummarizeClauseExpression_OperatorName)),
        }
        return fields
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        writer.write_collection_of_primitive_values("FieldList", self.field_list)
        writer.write_str_value("OperatorFieldName", self.operator_field_name)
        writer.write_enum_value("OperatorName", self.operator_name)
        writer.write_additional_data_value(self.additional_data)
    

