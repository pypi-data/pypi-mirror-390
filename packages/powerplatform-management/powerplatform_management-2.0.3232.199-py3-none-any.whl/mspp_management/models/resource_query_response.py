from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .resource_item import ResourceItem

@dataclass
class ResourceQueryResponse(AdditionalDataHolder, Parsable):
    """
    ARG SDK - ResourceQueryResult: https://learn.microsoft.com/dotnet/api/azure.resourcemanager.resourcegraph.models.resourcequeryresult
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Rows in this page
    count: Optional[int] = None
    # The data property
    data: Optional[list[ResourceItem]] = None
    # 0 = truncated, 1 = not truncated
    result_truncated: Optional[int] = None
    # Continuation token for next page
    skip_token: Optional[str] = None
    # Total rows matching the query
    total_records: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ResourceQueryResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ResourceQueryResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ResourceQueryResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .resource_item import ResourceItem

        from .resource_item import ResourceItem

        fields: dict[str, Callable[[Any], None]] = {
            "count": lambda n : setattr(self, 'count', n.get_int_value()),
            "data": lambda n : setattr(self, 'data', n.get_collection_of_object_values(ResourceItem)),
            "resultTruncated": lambda n : setattr(self, 'result_truncated', n.get_int_value()),
            "skipToken": lambda n : setattr(self, 'skip_token', n.get_str_value()),
            "totalRecords": lambda n : setattr(self, 'total_records', n.get_int_value()),
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
        writer.write_int_value("count", self.count)
        writer.write_collection_of_object_values("data", self.data)
        writer.write_int_value("resultTruncated", self.result_truncated)
        writer.write_str_value("skipToken", self.skip_token)
        writer.write_int_value("totalRecords", self.total_records)
        writer.write_additional_data_value(self.additional_data)
    

