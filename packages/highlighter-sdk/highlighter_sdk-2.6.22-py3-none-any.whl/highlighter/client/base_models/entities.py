from typing import Dict, List, Optional
from uuid import UUID

from highlighter.core.enums import ContentTypeEnum
from highlighter.core.gql_base_model import GQLBaseModel

from .entity import Entity


class Entities(GQLBaseModel):
    """Entity container

    Enables erganomic management of a set of entities.
    Entities can be looked-up by ID:
        `entity = entities[entity_id]`
    Entities can be added:
        `entities[entity_id] = entity`
        `entities.add(entity)`
        `entities.update(other_entities)`
    Entities can be queried (not yet implemented):
        `specific_entities = entities.where(object_class=object_class_id)`
        `specific_entities = entities.where(has_attribute=attribute_id)`
        `specific_entities = entities.where(has_attribute_value=enum_id)`
    """

    _entities: Dict[UUID, Entity] = {}

    def add(self, entity: Entity):
        self._entities[entity.id] = entity

    def __getitem__(self, key: UUID | int):
        if isinstance(key, int):
            return list(self._entities.values())[key]
        return self._entities[key]

    def __delitem__(self, key: UUID):
        return self._entities.__delitem__(key)

    def remove(self, entity: Entity):
        del self[entity.id]

    def __len__(self) -> int:
        return len(self._entities)

    def __iter__(self):
        return iter(list(self._entities.values()))

    def get(self, key: UUID, default: Entity | None = None):
        return self._entities.get(key, default)

    def __setitem__(self, entity_id: UUID, entity: Entity):
        self._entities[entity_id] = entity

    def update(self, *args, **kwargs):
        # Handles both dicts and iterable of pairs
        if args:
            other = args[0]
            if hasattr(other, "items"):
                for k, v in other.items():
                    self[k] = v  # goes through __setitem__
            else:
                for value in other:
                    if isinstance(value, Entity):
                        self.add(value)
                    else:
                        k, v = value
                        self[k] = v
        for k, v in kwargs.items():
            self[k] = v

    def __ior__(self, other):
        self.update(other)
        return self

    def __or__(self, other):
        new = type(self)(self, _entities=self._entities.copy())
        new.update(other)
        return new

    def __repr__(self):
        return self._entities.__repr__()

    def to_json_serializable_dict(self):
        return {str(id): entity.to_json() for id, entity in self._entities.items()}

    def to_data_sample(self) -> "DataSample":
        from highlighter.core.data_models.data_sample import DataSample

        if len(self._entities) == 0:
            return DataSample(content=self, content_type=ContentTypeEnum.ENTITIES)
        some_annotations = list(self._entities.values())[0].annotations
        if len(some_annotations) == 0:
            raise ValueError("Cannot convert Entities to DataSample if there are no annotations")
        annotation = some_annotations[0]
        if annotation.data_file_id is None:
            raise ValueError("Cannot convert Entities to DataSample if annotation.data_file_id is None")
        return DataSample(
            content=self,
            content_type=ContentTypeEnum.ENTITIES,
            recorded_at=annotation.occurred_at,
            stream_frame_index=annotation.datum_source.frame_id,
            media_frame_index=annotation.datum_source.frame_id,  # FIXME
        )

    def to_observations_table(self, stream_id: str, data_sample: "DataSample"):
        """
        Convert Entities to an ObservationsTable.

        Creates one row per annotation (entity + annotation pair). For entities with
        global observations but no annotations, creates one row per entity with a
        placeholder annotation.

        Args:
            stream_id: Optional stream identifier to include in the table

        Returns:
            ObservationsTable instance
        """
        from highlighter.agent.observations_table import ObservationsTable

        rows = []

        for entity in self._entities.values():
            # Process each annotation as a separate row
            if len(entity.annotations) > 0:
                for annotation in entity.annotations:
                    # Build attribute dict from annotation observations
                    attributes = {}
                    for obs in annotation.observations:
                        attr_label = (
                            obs.attribute_id.label
                            if hasattr(obs.attribute_id, "label")
                            else str(obs.attribute_id)
                        )
                        attributes[attr_label] = {
                            "value": obs.value,
                            "occurred_at": obs.occurred_at,
                            "confidence": obs.datum_source.confidence,
                        }

                    # Add global observations to attributes
                    for obs in entity.global_observations:
                        attr_label = (
                            obs.attribute_id.label
                            if hasattr(obs.attribute_id, "label")
                            else str(obs.attribute_id)
                        )
                        attributes[attr_label] = {
                            "value": obs.value,
                            "occurred_at": obs.occurred_at,
                            "confidence": obs.datum_source.confidence,
                        }

                    # Get location bounds if location exists
                    location_dict = None
                    if annotation.location is not None:
                        xmin, ymin, xmax, ymax = annotation.location.bounds
                        location_dict = {
                            "wkt": annotation.location.wkt,
                            "xmin": int(xmin),
                            "ymin": int(ymin),
                            "xmax": int(xmax),
                            "ymax": int(ymax),
                        }

                    # Build row data
                    row_data = {
                        "entity": {"id": entity.id},
                        "stream": {"id": stream_id if stream_id else "unknown"},
                        "data_sample": {
                            "recorded_at": data_sample.recorded_at,
                            "content_type": data_sample.content_type,
                            "stream_frame_index": data_sample.stream_frame_index,
                            "media_frame_index": data_sample.media_frame_index,
                        },
                        "annotation": {
                            "id": annotation.id,
                        },
                        "attribute": attributes,
                    }

                    # Add location to annotation if it exists
                    if location_dict is not None:
                        row_data["annotation"]["location"] = location_dict

                    rows.append(row_data)

            # If entity has no annotations but has global observations, create a row
            elif len(entity.global_observations) > 0:
                # Build attribute dict from global observations only
                attributes = {}
                for obs in entity.global_observations:
                    attr_label = (
                        obs.attribute_id.label
                        if hasattr(obs.attribute_id, "label")
                        else str(obs.attribute_id)
                    )
                    attributes[attr_label] = {
                        "value": obs.value,
                        "occurred_at": obs.occurred_at,
                        "confidence": obs.datum_source.confidence,
                    }

                # Build row data without annotation location
                row_data = {
                    "entity": {"id": entity.id},
                    "stream": {"id": stream_id if stream_id else "unknown"},
                    "data_sample": {
                        "recorded_at": data_sample.recorded_at,
                        "content_type": data_sample.content_type,
                        "stream_frame_index": data_sample.stream_frame_index,
                        "media_frame_index": data_sample.media_frame_index,
                    },
                    "annotation": {
                        # ToDo: How do we get an AnnotationId from global observation
                        # the current setup is "Annotation has-many Observations"
                        # so global_observations, simply dont have an Annotation instance to refer to
                        "id": UUID(int=0),  # Placeholder annotation ID
                    },
                    "attribute": attributes,
                }

                rows.append(row_data)

        # If no rows were created (no entities or entities with no observations/annotations),
        # create a minimal row with just data_sample info to allow evaluation of data_sample expressions.
        #
        # Why this is needed:
        # - ObservationsTable.any() evaluates CEL expressions by iterating over rows
        # - Without any rows, expressions that reference data_sample fields (e.g.,
        #   "data_sample.media_frame_index >= 5") would never be evaluated and would return False
        # - RuleTrigger uses these expressions to determine when to start/stop recording
        # - By creating a minimal row with the current data_sample info (but placeholder entity/annotation),
        #   we enable RuleTrigger expressions to work correctly even when no entities are detected yet
        # - This is especially important during early frames where detections may not have occurred
        if len(rows) == 0:
            minimal_row_data = {
                "entity": {"id": UUID(int=0)},  # Placeholder entity ID
                "stream": {"id": stream_id if stream_id else "unknown"},
                "data_sample": {
                    "recorded_at": data_sample.recorded_at,
                    "content_type": data_sample.content_type,
                    "stream_frame_index": data_sample.stream_frame_index,
                    "media_frame_index": data_sample.media_frame_index,
                },
                "annotation": {
                    "id": UUID(int=0),  # Placeholder annotation ID
                },
                "attribute": {},  # No attributes
            }
            rows.append(minimal_row_data)

        return ObservationsTable.from_row_records(rows)
