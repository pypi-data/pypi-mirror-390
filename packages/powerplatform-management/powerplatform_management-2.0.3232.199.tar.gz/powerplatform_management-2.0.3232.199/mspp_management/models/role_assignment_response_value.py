from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class RoleAssignmentResponse_value(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The Id of the creator principal
    created_by_principal_object_id: Optional[str] = None
    # The type of the creator principal
    created_by_principal_type: Optional[str] = None
    # The datetime of when the assignment was created
    created_on: Optional[datetime.datetime] = None
    # The Id of the assigned principal
    principal_object_id: Optional[str] = None
    # The type of the principal
    principal_type: Optional[str] = None
    # Role assignment Id
    role_assignment_id: Optional[str] = None
    # The Id of the role definition
    role_definition_id: Optional[str] = None
    # The assignment scope
    scope: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> RoleAssignmentResponse_value:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: RoleAssignmentResponse_value
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return RoleAssignmentResponse_value()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "createdByPrincipalObjectId": lambda n : setattr(self, 'created_by_principal_object_id', n.get_str_value()),
            "createdByPrincipalType": lambda n : setattr(self, 'created_by_principal_type', n.get_str_value()),
            "createdOn": lambda n : setattr(self, 'created_on', n.get_datetime_value()),
            "principalObjectId": lambda n : setattr(self, 'principal_object_id', n.get_str_value()),
            "principalType": lambda n : setattr(self, 'principal_type', n.get_str_value()),
            "roleAssignmentId": lambda n : setattr(self, 'role_assignment_id', n.get_str_value()),
            "roleDefinitionId": lambda n : setattr(self, 'role_definition_id', n.get_str_value()),
            "scope": lambda n : setattr(self, 'scope', n.get_str_value()),
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
        writer.write_str_value("createdByPrincipalObjectId", self.created_by_principal_object_id)
        writer.write_str_value("createdByPrincipalType", self.created_by_principal_type)
        writer.write_datetime_value("createdOn", self.created_on)
        writer.write_str_value("principalObjectId", self.principal_object_id)
        writer.write_str_value("principalType", self.principal_type)
        writer.write_str_value("roleAssignmentId", self.role_assignment_id)
        writer.write_str_value("roleDefinitionId", self.role_definition_id)
        writer.write_str_value("scope", self.scope)
        writer.write_additional_data_value(self.additional_data)
    

