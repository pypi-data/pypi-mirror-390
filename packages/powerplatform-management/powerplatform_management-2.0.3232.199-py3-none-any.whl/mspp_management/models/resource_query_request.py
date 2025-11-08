from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .clause import Clause
    from .resource_query_request_options import ResourceQueryRequestOptions

@dataclass
class ResourceQueryRequest(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Ordered list of query clauses; evaluated in order
    clauses: Optional[list[Clause]] = None
    # The Options property
    options: Optional[ResourceQueryRequestOptions] = None
    # Target table/resource set (e.g., "PowerPlatformResources")
    table_name: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ResourceQueryRequest:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ResourceQueryRequest
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ResourceQueryRequest()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .clause import Clause
        from .resource_query_request_options import ResourceQueryRequestOptions

        from .clause import Clause
        from .resource_query_request_options import ResourceQueryRequestOptions

        fields: dict[str, Callable[[Any], None]] = {
            "Clauses": lambda n : setattr(self, 'clauses', n.get_collection_of_object_values(Clause)),
            "Options": lambda n : setattr(self, 'options', n.get_object_value(ResourceQueryRequestOptions)),
            "TableName": lambda n : setattr(self, 'table_name', n.get_str_value()),
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
        writer.write_collection_of_object_values("Clauses", self.clauses)
        writer.write_object_value("Options", self.options)
        writer.write_str_value("TableName", self.table_name)
        writer.write_additional_data_value(self.additional_data)
    

