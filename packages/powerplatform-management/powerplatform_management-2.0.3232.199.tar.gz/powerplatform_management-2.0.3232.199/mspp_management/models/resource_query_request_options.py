from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class ResourceQueryRequestOptions(AdditionalDataHolder, Parsable):
    """
    ARG .NET SDK - ResourceQueryRequestOptions: https://learn.microsoft.com/dotnet/api/azure.resourcemanager.resourcegraph.models.resourcequeryrequestoptions
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Offset; typically 0 when using SkipToken
    skip: Optional[int] = None
    # Continuation token from previous page
    skip_token: Optional[str] = None
    # Max rows per page
    top: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ResourceQueryRequestOptions:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ResourceQueryRequestOptions
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ResourceQueryRequestOptions()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "Skip": lambda n : setattr(self, 'skip', n.get_int_value()),
            "SkipToken": lambda n : setattr(self, 'skip_token', n.get_str_value()),
            "Top": lambda n : setattr(self, 'top', n.get_int_value()),
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
        writer.write_int_value("Skip", self.skip)
        writer.write_str_value("SkipToken", self.skip_token)
        writer.write_int_value("Top", self.top)
        writer.write_additional_data_value(self.additional_data)
    

