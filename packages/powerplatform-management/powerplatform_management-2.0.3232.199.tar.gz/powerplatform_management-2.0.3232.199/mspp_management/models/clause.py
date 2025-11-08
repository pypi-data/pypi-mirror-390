from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .count_clause import CountClause
    from .distinct_clause import DistinctClause
    from .extend_clause import ExtendClause
    from .join_clause import JoinClause
    from .order_by_clause import OrderByClause
    from .project_clause import ProjectClause
    from .summarize_clause import SummarizeClause
    from .take_clause import TakeClause
    from .where_clause import WhereClause

@dataclass
class Clause(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes CountClause, DistinctClause, ExtendClause, JoinClause, OrderByClause, ProjectClause, SummarizeClause, TakeClause, WhereClause
    """
    # Composed type representation for type CountClause
    count_clause: Optional[CountClause] = None
    # Composed type representation for type DistinctClause
    distinct_clause: Optional[DistinctClause] = None
    # Composed type representation for type ExtendClause
    extend_clause: Optional[ExtendClause] = None
    # Composed type representation for type JoinClause
    join_clause: Optional[JoinClause] = None
    # Composed type representation for type OrderByClause
    order_by_clause: Optional[OrderByClause] = None
    # Composed type representation for type ProjectClause
    project_clause: Optional[ProjectClause] = None
    # Composed type representation for type SummarizeClause
    summarize_clause: Optional[SummarizeClause] = None
    # Composed type representation for type TakeClause
    take_clause: Optional[TakeClause] = None
    # Composed type representation for type WhereClause
    where_clause: Optional[WhereClause] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Clause:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Clause
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        try:
            child_node = parse_node.get_child_node("$type")
            mapping_value = child_node.get_str_value() if child_node else None
        except AttributeError:
            mapping_value = None
        result = Clause()
        if mapping_value and mapping_value.casefold() == "count".casefold():
            from .count_clause import CountClause

            result.count_clause = CountClause()
        elif mapping_value and mapping_value.casefold() == "distinct".casefold():
            from .distinct_clause import DistinctClause

            result.distinct_clause = DistinctClause()
        elif mapping_value and mapping_value.casefold() == "extend".casefold():
            from .extend_clause import ExtendClause

            result.extend_clause = ExtendClause()
        elif mapping_value and mapping_value.casefold() == "join".casefold():
            from .join_clause import JoinClause

            result.join_clause = JoinClause()
        elif mapping_value and mapping_value.casefold() == "orderby".casefold():
            from .order_by_clause import OrderByClause

            result.order_by_clause = OrderByClause()
        elif mapping_value and mapping_value.casefold() == "project".casefold():
            from .project_clause import ProjectClause

            result.project_clause = ProjectClause()
        elif mapping_value and mapping_value.casefold() == "summarize".casefold():
            from .summarize_clause import SummarizeClause

            result.summarize_clause = SummarizeClause()
        elif mapping_value and mapping_value.casefold() == "take".casefold():
            from .take_clause import TakeClause

            result.take_clause = TakeClause()
        elif mapping_value and mapping_value.casefold() == "where".casefold():
            from .where_clause import WhereClause

            result.where_clause = WhereClause()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .count_clause import CountClause
        from .distinct_clause import DistinctClause
        from .extend_clause import ExtendClause
        from .join_clause import JoinClause
        from .order_by_clause import OrderByClause
        from .project_clause import ProjectClause
        from .summarize_clause import SummarizeClause
        from .take_clause import TakeClause
        from .where_clause import WhereClause

        if self.count_clause:
            return self.count_clause.get_field_deserializers()
        if self.distinct_clause:
            return self.distinct_clause.get_field_deserializers()
        if self.extend_clause:
            return self.extend_clause.get_field_deserializers()
        if self.join_clause:
            return self.join_clause.get_field_deserializers()
        if self.order_by_clause:
            return self.order_by_clause.get_field_deserializers()
        if self.project_clause:
            return self.project_clause.get_field_deserializers()
        if self.summarize_clause:
            return self.summarize_clause.get_field_deserializers()
        if self.take_clause:
            return self.take_clause.get_field_deserializers()
        if self.where_clause:
            return self.where_clause.get_field_deserializers()
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        if self.count_clause:
            writer.write_object_value(None, self.count_clause)
        elif self.distinct_clause:
            writer.write_object_value(None, self.distinct_clause)
        elif self.extend_clause:
            writer.write_object_value(None, self.extend_clause)
        elif self.join_clause:
            writer.write_object_value(None, self.join_clause)
        elif self.order_by_clause:
            writer.write_object_value(None, self.order_by_clause)
        elif self.project_clause:
            writer.write_object_value(None, self.project_clause)
        elif self.summarize_clause:
            writer.write_object_value(None, self.summarize_clause)
        elif self.take_clause:
            writer.write_object_value(None, self.take_clause)
        elif self.where_clause:
            writer.write_object_value(None, self.where_clause)
    

