from datetime import datetime
from typing import Dict, NamedTuple, Optional, Set, Union
from uuid import UUID, uuid4

import celpy
from pydantic import BaseModel, Field, field_validator

from highlighter.core.enums import ContentTypeEnum
from highlighter.core.labeled_uuid import LabeledUUID

# ToDo: Consolidate this work with the data layer
# ToDo: Consolidate this work with the Entities object and Agents
# ToDo: Consolidate this work with Datasets

__all__ = ["ObservationsTable"]


class DotDict(dict):
    """
    Dictionary with dot notation access and recursive conversion.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getattr__(self, key):
        if key in self:
            return self[key]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        if key in self:
            del self[key]
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")

    def __repr__(self):
        return f"Attribtues({dict.__repr__(self)})"


class ObservationsTable:
    class Row(BaseModel):

        model_config = {"arbitrary_types_allowed": True}

        class Stream(BaseModel):
            id: str

        class Entity(BaseModel):
            id: UUID

        class DataSample(BaseModel):
            recorded_at: datetime
            content_type: ContentTypeEnum
            stream_frame_index: int
            media_frame_index: int
            width: Optional[int] = None
            height: Optional[int] = None

        class Annotation(BaseModel):

            class Location(BaseModel):
                wkt: str
                xmin: int
                ymin: int
                xmax: int
                ymax: int

                @property
                def area(self):
                    return (self.xmax - self.xmin) * (self.ymax - self.ymin)

            id: UUID
            location: Optional[Location] = None

        class Attribute(BaseModel):

            class Category(BaseModel):
                id: UUID
                name: str

            value: Union[int, float, str, Category]
            occurred_at: datetime
            confidence: Optional[float] = None

            @field_validator("value", mode="before")
            def handel_labeled_uuid(cls, v):
                if isinstance(v, LabeledUUID):
                    return cls.Category(id=v, name=v.label)
                if isinstance(v, UUID):
                    return cls.Category(id=v, name="__UNDEFINED__")
                return v

        # class _NullAttribute(dict):
        #    """A safe null object that returns None for any key access"""

        #    def __getitem__(self, key):
        #        return None

        #    def __getattr__(self, key):
        #        return None

        #    def get(self, key, default=None):
        #        return default

        # class SafeAttributes(dict):

        #    def __init__(self, attributes):
        #        # Convert Pydantic models to dicts for CEL
        #        self._attributes = {}
        #        for k, v in attributes.items():
        #            attr = ObservationsTable.Row.Attribute(**v)
        #            # Store as dict for CEL field selection support
        #            self._attributes[k] = {
        #                "value": attr.value,
        #                "occurred_at": attr.occurred_at,
        #                "confidence": attr.confidence,
        #            }
        #        # Initialize dict with the attributes
        #        super().__init__(self._attributes)

        #    def __getattr__(self, k):
        #        val = self._attributes.get(k, None)
        #        if val and isinstance(val, dict):
        #            # Convert back to Attribute for Python attribute access
        #            return ObservationsTable.Row.Attribute(**val)
        #        return val

        #    def __getitem__(self, k):
        #        """Support dict-like access for CEL, returns safe null object for missing keys"""
        #        val = self._attributes.get(k, None)
        #        if val is None:
        #            return ObservationsTable.Row._NullAttribute()
        #        return val

        #    def get(self, k, default=None):
        #        """Support dict.get() for CEL"""
        #        return self._attributes.get(k, default)

        entity: Entity
        stream: Stream
        data_sample: DataSample
        annotation: Annotation
        attribute: DotDict
        id: UUID = Field(default_factory=uuid4)

        @field_validator("attribute", mode="before")
        @classmethod
        def convert_attribute_dict(cls, v):
            if isinstance(v, dict) or isinstance(v, DotDict):
                return DotDict(**{key: cls.Attribute(**value) for key, value in v.items()})
            return v

        def to_cel_ctx_dict(self, all_attr_keys: Set[str]):
            attributes = {k: {"value": None, "occurred_at": None, "confidence": None} for k in all_attr_keys}
            for k, v in self.attribute.items():
                attributes[k] = v.model_dump(mode="json")

            return {
                "id": str(self.id),
                "entity": self.entity.model_dump(mode="json"),
                "stream": self.stream.model_dump(mode="json"),
                "data_sample": self.data_sample.model_dump(mode="json"),
                "annotation": self.annotation.model_dump(mode="json"),
                "attribute": attributes,
            }

    def __init__(self, rows: Dict[str, Row]):
        self._rows = rows

    def __getitem__(self, key):
        """Support indexing for CEL"""
        return self._rows[key]

    def __iter__(self):
        """Support iteration for CEL"""
        return iter(self._rows)

    def __len__(self):
        """Support len() for CEL"""
        return len(self._rows)

    @classmethod
    def from_row_records(cls, records):

        rows = {}
        for r in records:
            row = ObservationsTable.Row(**r)
            rows[str(row.id)] = row
        return cls(rows)

    def get_cel_ctx_rows(self):
        # Collect all attribute keys across all rows
        all_attr_keys = set()
        for r in self._rows.values():
            all_attr_keys.update(r.attribute.keys())

            yield celpy.json_to_cel(r.to_cel_ctx_dict(all_attr_keys))

    def filter(self, expr):
        env = celpy.Environment()
        ast = env.compile(expr)
        program = env.program(ast)

        # Evaluate each row individually and catch errors
        result = []
        for row_ctx in self.get_cel_ctx_rows():
            try:
                # Evaluate expression with row fields directly in context
                matches = program.evaluate(row_ctx)
                if matches:
                    result.append(self._rows[str(row_ctx["id"])])
            except (celpy.evaluation.CELEvalError, TypeError):
                # If evaluation fails (e.g., None comparison), treat as non-matching
                pass

        return result

    def any(self, expr):
        """
        Check if any row matches the given CEL expression.

        Args:
            expr: A CEL expression to evaluate against each row

        Returns:
            bool: True if at least one row matches, False otherwise
        """
        env = celpy.Environment()
        ast = env.compile(expr)
        program = env.program(ast)

        for row_ctx in self.get_cel_ctx_rows():
            try:
                matches = program.evaluate(row_ctx)
                if matches:
                    return True
            except (celpy.evaluation.CELEvalError, TypeError):
                # If evaluation fails, treat as non-matching
                pass

        return False

    def all(self, expr):
        """
        Check if all rows match the given CEL expression.

        Args:
            expr: A CEL expression to evaluate against each row

        Returns:
            bool: True if all rows match, False otherwise
        """
        env = celpy.Environment()
        ast = env.compile(expr)
        program = env.program(ast)

        for row_ctx in self.get_cel_ctx_rows():
            try:
                matches = program.evaluate(row_ctx)
                if not matches:
                    return False
            except (celpy.evaluation.CELEvalError, TypeError):
                # If evaluation fails, treat as non-matching
                return False

        return True

    def show(self):
        """Print a tabular representation of the rows to the terminal"""
        if not self._rows:
            print("Empty table")
            return

        # Collect all attribute keys across all rows
        all_attr_keys = sorted(set(key for row in self._rows.values() for key in row.attribute.keys()))

        # Define columns: id, entity_id, stream_id, recorded_at, then attributes
        columns = ["id", "entity_id", "stream_id", "recorded_at"] + all_attr_keys

        # Calculate column widths
        col_widths = {col: len(col) for col in columns}

        # Update widths based on data
        for row in self._rows.values():
            col_widths["id"] = max(col_widths["id"], len(str(row.id)[:8]))
            col_widths["entity_id"] = max(col_widths["entity_id"], len(str(row.entity.id)[:8]))
            col_widths["stream_id"] = max(col_widths["stream_id"], len(row.stream.id))
            col_widths["recorded_at"] = max(
                col_widths["recorded_at"], len(row.data_sample.recorded_at.strftime("%Y-%m-%d %H:%M"))
            )

            for attr_key in all_attr_keys:
                attr = row.attribute.get(attr_key)
                if attr:
                    value_str = str(attr["value"]) if isinstance(attr, dict) else str(attr.value)
                    col_widths[attr_key] = max(col_widths[attr_key], len(value_str))

        # Print header
        header = " | ".join(col.ljust(col_widths[col]) for col in columns)
        print(header)
        print("-" * len(header))

        # Print rows
        for row in self._rows.values():
            row_data = []
            row_data.append(str(row.id)[:8].ljust(col_widths["id"]))
            row_data.append(str(row.entity.id)[:8].ljust(col_widths["entity_id"]))
            row_data.append(row.stream.id.ljust(col_widths["stream_id"]))
            row_data.append(
                row.data_sample.recorded_at.strftime("%Y-%m-%d %H:%M").ljust(col_widths["recorded_at"])
            )

            for attr_key in all_attr_keys:
                attr = row.attribute.get(attr_key)
                if attr:
                    value_str = str(attr["value"]) if isinstance(attr, dict) else str(attr.value)
                    row_data.append(value_str.ljust(col_widths[attr_key]))
                else:
                    row_data.append("".ljust(col_widths[attr_key]))

            print(" | ".join(row_data))
