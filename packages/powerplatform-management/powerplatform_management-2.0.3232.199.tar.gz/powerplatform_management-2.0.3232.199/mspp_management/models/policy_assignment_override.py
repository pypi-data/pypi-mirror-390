from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .policy_assignment_override_behavior_type import PolicyAssignmentOverride_behaviorType
    from .policy_assignment_override_resource_type import PolicyAssignmentOverride_resourceType

@dataclass
class PolicyAssignmentOverride(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The Behavior type.
    behavior_type: Optional[PolicyAssignmentOverride_behaviorType] = None
    # Resource Id ex. the environment group id.
    resource_id: Optional[str] = None
    # The Resource type.
    resource_type: Optional[PolicyAssignmentOverride_resourceType] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PolicyAssignmentOverride:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PolicyAssignmentOverride
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return PolicyAssignmentOverride()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .policy_assignment_override_behavior_type import PolicyAssignmentOverride_behaviorType
        from .policy_assignment_override_resource_type import PolicyAssignmentOverride_resourceType

        from .policy_assignment_override_behavior_type import PolicyAssignmentOverride_behaviorType
        from .policy_assignment_override_resource_type import PolicyAssignmentOverride_resourceType

        fields: dict[str, Callable[[Any], None]] = {
            "behaviorType": lambda n : setattr(self, 'behavior_type', n.get_enum_value(PolicyAssignmentOverride_behaviorType)),
            "resourceId": lambda n : setattr(self, 'resource_id', n.get_str_value()),
            "resourceType": lambda n : setattr(self, 'resource_type', n.get_enum_value(PolicyAssignmentOverride_resourceType)),
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
        writer.write_enum_value("behaviorType", self.behavior_type)
        writer.write_str_value("resourceId", self.resource_id)
        writer.write_enum_value("resourceType", self.resource_type)
        writer.write_additional_data_value(self.additional_data)
    

