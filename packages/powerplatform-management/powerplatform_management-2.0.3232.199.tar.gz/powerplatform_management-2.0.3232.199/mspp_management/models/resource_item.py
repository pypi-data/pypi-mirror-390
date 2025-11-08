from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .resource_item_properties import ResourceItem_properties

@dataclass
class ResourceItem(AdditionalDataHolder, Parsable):
    """
    Standard Azure Resource Graph row with Power Platform–specific fields.Arbitrary properties may exist under `properties`.
    ARG resource table reference: https://learn.microsoft.com/azure/governance/resource-graph/reference/supported-tables-resources
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The environmentId property
    environment_id: Optional[str] = None
    # The environmentId1 property
    environment_id1: Optional[str] = None
    # The environmentName property
    environment_name: Optional[str] = None
    # The environmentRegion property
    environment_region: Optional[str] = None
    # The environmentType property
    environment_type: Optional[str] = None
    # The id property
    id: Optional[str] = None
    # The isManagedEnvironment property
    is_managed_environment: Optional[bool] = None
    # The kind property
    kind: Optional[str] = None
    # The location property
    location: Optional[str] = None
    # The managedBy property
    managed_by: Optional[str] = None
    # The name property
    name: Optional[str] = None
    # Free-form ARG properties bag
    properties: Optional[ResourceItem_properties] = None
    # The resourceGroup property
    resource_group: Optional[str] = None
    # The subscriptionId property
    subscription_id: Optional[str] = None
    # The tenantId property
    tenant_id: Optional[str] = None
    # The type property
    type: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ResourceItem:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ResourceItem
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ResourceItem()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .resource_item_properties import ResourceItem_properties

        from .resource_item_properties import ResourceItem_properties

        fields: dict[str, Callable[[Any], None]] = {
            "environmentId": lambda n : setattr(self, 'environment_id', n.get_str_value()),
            "environmentId1": lambda n : setattr(self, 'environment_id1', n.get_str_value()),
            "environmentName": lambda n : setattr(self, 'environment_name', n.get_str_value()),
            "environmentRegion": lambda n : setattr(self, 'environment_region', n.get_str_value()),
            "environmentType": lambda n : setattr(self, 'environment_type', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_str_value()),
            "isManagedEnvironment": lambda n : setattr(self, 'is_managed_environment', n.get_bool_value()),
            "kind": lambda n : setattr(self, 'kind', n.get_str_value()),
            "location": lambda n : setattr(self, 'location', n.get_str_value()),
            "managedBy": lambda n : setattr(self, 'managed_by', n.get_str_value()),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "properties": lambda n : setattr(self, 'properties', n.get_object_value(ResourceItem_properties)),
            "resourceGroup": lambda n : setattr(self, 'resource_group', n.get_str_value()),
            "subscriptionId": lambda n : setattr(self, 'subscription_id', n.get_str_value()),
            "tenantId": lambda n : setattr(self, 'tenant_id', n.get_str_value()),
            "type": lambda n : setattr(self, 'type', n.get_str_value()),
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
        writer.write_str_value("environmentId", self.environment_id)
        writer.write_str_value("environmentId1", self.environment_id1)
        writer.write_str_value("environmentName", self.environment_name)
        writer.write_str_value("environmentRegion", self.environment_region)
        writer.write_str_value("environmentType", self.environment_type)
        writer.write_str_value("id", self.id)
        writer.write_bool_value("isManagedEnvironment", self.is_managed_environment)
        writer.write_str_value("kind", self.kind)
        writer.write_str_value("location", self.location)
        writer.write_str_value("managedBy", self.managed_by)
        writer.write_str_value("name", self.name)
        writer.write_object_value("properties", self.properties)
        writer.write_str_value("resourceGroup", self.resource_group)
        writer.write_str_value("subscriptionId", self.subscription_id)
        writer.write_str_value("tenantId", self.tenant_id)
        writer.write_str_value("type", self.type)
        writer.write_additional_data_value(self.additional_data)
    

