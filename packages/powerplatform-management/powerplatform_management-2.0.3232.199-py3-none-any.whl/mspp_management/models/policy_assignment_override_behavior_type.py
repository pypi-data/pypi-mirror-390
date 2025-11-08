from enum import Enum

class PolicyAssignmentOverride_behaviorType(str, Enum):
    NotSpecified = "NotSpecified",
    Include = "Include",
    Exclude = "Exclude",

