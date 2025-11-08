from enum import Enum

class ClauseBaseClass_Type(str, Enum):
    Where = "where",
    Project = "project",
    Take = "take",
    Orderby = "orderby",
    Distinct = "distinct",
    Count = "count",
    Summarize = "summarize",
    Extend = "extend",
    Join = "join",

