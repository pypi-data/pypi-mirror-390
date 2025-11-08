from enum import Enum

class PolicyAssignmentOverride_resourceType(str, Enum):
    NotSpecified = "NotSpecified",
    EnvironmentGroup = "EnvironmentGroup",
    Environment = "Environment",
    Tenant = "Tenant",

