"""
CovetPy Schema Evolution

Handles API schema evolution with backward compatibility:
- Field addition (backward compatible)
- Field deprecation (graceful removal)
- Field renaming (aliasing)
- Response transformation between versions
- Request transformation between versions

NO MOCK DATA - Real schema transformation and validation.
"""

import logging
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union

from covet.api.versioning.version_manager import APIVersion

try:
    from pydantic import BaseModel, Field

    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    BaseModel = object

logger = logging.getLogger(__name__)


class FieldChange(str, Enum):
    """Types of field changes."""

    ADDED = "added"  # New field added
    REMOVED = "removed"  # Field removed
    RENAMED = "renamed"  # Field renamed
    TYPE_CHANGED = "type_changed"  # Field type changed
    DEPRECATED = "deprecated"  # Field deprecated but still works
    REQUIRED_CHANGED = "required_changed"  # Required/optional changed


@dataclass
class FieldTransformation:
    """
    Defines how to transform a field between versions.

    Attributes:
        source_field: Source field name (None if adding)
        target_field: Target field name (None if removing)
        change_type: Type of change
        transformer: Function to transform value
        default_value: Default value for new fields
        deprecation_message: Message if field is deprecated
        metadata: Additional metadata
    """

    change_type: FieldChange
    source_field: Optional[str] = None
    target_field: Optional[str] = None
    transformer: Optional[Callable[[Any], Any]] = None
    default_value: Any = None
    deprecation_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def apply(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply transformation to data.

        Args:
            data: Input data dictionary

        Returns:
            Transformed data dictionary
        """
        result = data.copy()

        if self.change_type == FieldChange.ADDED:
            # Add new field with default value
            if self.target_field and self.target_field not in result:
                result[self.target_field] = self.default_value

        elif self.change_type == FieldChange.REMOVED:
            # Remove field
            if self.source_field and self.source_field in result:
                del result[self.source_field]

        elif self.change_type == FieldChange.RENAMED:
            # Rename field
            if self.source_field and self.source_field in result:
                value = result[self.source_field]
                if self.transformer:
                    value = self.transformer(value)
                if self.target_field:
                    result[self.target_field] = value
                del result[self.source_field]

        elif self.change_type == FieldChange.TYPE_CHANGED:
            # Transform field value
            if self.source_field and self.source_field in result and self.transformer:
                result[self.source_field] = self.transformer(result[self.source_field])

        elif self.change_type == FieldChange.DEPRECATED:
            # Field still works but may be transformed
            if self.source_field and self.source_field in result:
                value = result[self.source_field]
                if self.transformer:
                    value = self.transformer(value)
                if self.target_field and self.target_field != self.source_field:
                    result[self.target_field] = value

        return result


@dataclass
class SchemaVersion:
    """
    Schema definition for specific API version.

    Attributes:
        version: API version
        schema_class: Pydantic model class (if available)
        fields: Field definitions
        transformations: Transformations from previous version
        metadata: Additional metadata
    """

    version: APIVersion
    schema_class: Optional[Type[BaseModel]] = None
    fields: Dict[str, Any] = field(default_factory=dict)
    transformations: List[FieldTransformation] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_field_names(self) -> Set[str]:
        """Get all field names in schema."""
        if self.schema_class and HAS_PYDANTIC:
            return set(self.schema_class.__fields__.keys())
        return set(self.fields.keys())

    def has_field(self, field_name: str) -> bool:
        """Check if schema has field."""
        return field_name in self.get_field_names()


class SchemaEvolutionManager:
    """
    Manage schema evolution across API versions.

    Tracks schema changes, provides transformation functions,
    and ensures backward compatibility.

    NO MOCK DATA - Real schema transformation logic.
    """

    def __init__(self):
        """Initialize schema evolution manager."""
        # Schema registry: version -> SchemaVersion
        self.schemas: Dict[APIVersion, SchemaVersion] = {}

        # Transformation cache: (from_version, to_version) -> List[FieldTransformation]
        self.transformation_cache: Dict[
            Tuple[APIVersion, APIVersion], List[FieldTransformation]
        ] = {}

    def register_schema(
        self,
        version: APIVersion,
        schema_class: Optional[Type[BaseModel]] = None,
        fields: Optional[Dict[str, Any]] = None,
        **metadata,
    ) -> SchemaVersion:
        """
        Register schema for version.

        Args:
            version: API version
            schema_class: Pydantic model class
            fields: Field definitions (if not using Pydantic)
            **metadata: Additional metadata

        Returns:
            Created SchemaVersion
        """
        schema_version = SchemaVersion(
            version=version, schema_class=schema_class, fields=fields or {}, metadata=metadata
        )

        self.schemas[version] = schema_version

        logger.info(f"Registered schema for version {version}")

        return schema_version

    def add_field(
        self,
        version: APIVersion,
        field_name: str,
        default_value: Any = None,
        required: bool = False,
        description: Optional[str] = None,
    ) -> FieldTransformation:
        """
        Add new field in version (backward compatible).

        Args:
            version: API version where field was added
            field_name: Name of new field
            default_value: Default value for field
            required: Whether field is required
            description: Field description

        Returns:
            Created transformation
        """
        if version not in self.schemas:
            raise ValueError(f"Schema for version {version} not registered")

        transformation = FieldTransformation(
            change_type=FieldChange.ADDED,
            target_field=field_name,
            default_value=default_value,
            metadata={"required": required, "description": description},
        )

        self.schemas[version].transformations.append(transformation)
        self._invalidate_cache(version)

        logger.debug(f"Added field '{field_name}' in version {version}")

        return transformation

    def remove_field(
        self, version: APIVersion, field_name: str, deprecation_message: Optional[str] = None
    ) -> FieldTransformation:
        """
        Remove field in version (breaking change).

        Args:
            version: API version where field was removed
            field_name: Name of removed field
            deprecation_message: Deprecation message

        Returns:
            Created transformation
        """
        if version not in self.schemas:
            raise ValueError(f"Schema for version {version} not registered")

        transformation = FieldTransformation(
            change_type=FieldChange.REMOVED,
            source_field=field_name,
            deprecation_message=deprecation_message,
        )

        self.schemas[version].transformations.append(transformation)
        self._invalidate_cache(version)

        logger.warning(f"Removed field '{field_name}' in version {version}")

        return transformation

    def rename_field(
        self,
        version: APIVersion,
        old_name: str,
        new_name: str,
        transformer: Optional[Callable[[Any], Any]] = None,
        keep_old_name: bool = False,
    ) -> FieldTransformation:
        """
        Rename field in version.

        Args:
            version: API version where field was renamed
            old_name: Old field name
            new_name: New field name
            transformer: Optional value transformer
            keep_old_name: Keep old name as alias (backward compatible)

        Returns:
            Created transformation
        """
        if version not in self.schemas:
            raise ValueError(f"Schema for version {version} not registered")

        transformation = FieldTransformation(
            change_type=FieldChange.RENAMED if not keep_old_name else FieldChange.DEPRECATED,
            source_field=old_name,
            target_field=new_name,
            transformer=transformer,
            metadata={"keep_old_name": keep_old_name},
        )

        self.schemas[version].transformations.append(transformation)
        self._invalidate_cache(version)

        logger.debug(
            f"Renamed field '{old_name}' -> '{new_name}' in version {version} "
            f"(keep_old={keep_old_name})"
        )

        return transformation

    def change_field_type(
        self,
        version: APIVersion,
        field_name: str,
        transformer: Callable[[Any], Any],
        old_type: Optional[str] = None,
        new_type: Optional[str] = None,
    ) -> FieldTransformation:
        """
        Change field type with transformer (breaking change).

        Args:
            version: API version where type changed
            field_name: Field name
            transformer: Function to convert old type to new type
            old_type: Old type name (for documentation)
            new_type: New type name (for documentation)

        Returns:
            Created transformation
        """
        if version not in self.schemas:
            raise ValueError(f"Schema for version {version} not registered")

        transformation = FieldTransformation(
            change_type=FieldChange.TYPE_CHANGED,
            source_field=field_name,
            target_field=field_name,
            transformer=transformer,
            metadata={"old_type": old_type, "new_type": new_type},
        )

        self.schemas[version].transformations.append(transformation)
        self._invalidate_cache(version)

        logger.warning(
            f"Changed field '{field_name}' type from {old_type} to {new_type} "
            f"in version {version}"
        )

        return transformation

    def deprecate_field(
        self,
        version: APIVersion,
        field_name: str,
        replacement: Optional[str] = None,
        message: Optional[str] = None,
    ) -> FieldTransformation:
        """
        Mark field as deprecated (still works).

        Args:
            version: API version where field was deprecated
            field_name: Deprecated field name
            replacement: Replacement field name
            message: Deprecation message

        Returns:
            Created transformation
        """
        if version not in self.schemas:
            raise ValueError(f"Schema for version {version} not registered")

        if message is None:
            message = f"Field '{field_name}' is deprecated."
            if replacement:
                message += f" Use '{replacement}' instead."

        transformation = FieldTransformation(
            change_type=FieldChange.DEPRECATED,
            source_field=field_name,
            target_field=replacement,
            deprecation_message=message,
        )

        self.schemas[version].transformations.append(transformation)
        self._invalidate_cache(version)

        logger.info(f"Deprecated field '{field_name}' in version {version}")

        return transformation

    def get_transformations(
        self, from_version: APIVersion, to_version: APIVersion
    ) -> List[FieldTransformation]:
        """
        Get transformations needed to convert from one version to another.

        Args:
            from_version: Source version
            to_version: Target version

        Returns:
            List of transformations to apply
        """
        # Check cache
        cache_key = (from_version, to_version)
        if cache_key in self.transformation_cache:
            return self.transformation_cache[cache_key]

        # Same version - no transformation needed
        if from_version == to_version:
            return []

        # Get all versions between from and to
        all_versions = sorted(self.schemas.keys())

        try:
            from_idx = all_versions.index(from_version)
            to_idx = all_versions.index(to_version)
        except ValueError as e:
            raise ValueError(f"Unknown version: {e}")

        # Determine direction
        if from_idx < to_idx:
            # Forward migration
            versions_to_process = all_versions[from_idx + 1 : to_idx + 1]
        else:
            # Backward migration (reverse transformations)
            versions_to_process = all_versions[to_idx:from_idx]
            versions_to_process.reverse()

        # Collect transformations
        transformations = []
        for version in versions_to_process:
            if version in self.schemas:
                transformations.extend(self.schemas[version].transformations)

        # Cache result
        self.transformation_cache[cache_key] = transformations

        return transformations

    def transform_data(
        self, data: Dict[str, Any], from_version: APIVersion, to_version: APIVersion
    ) -> Dict[str, Any]:
        """
        Transform data from one version to another.

        Args:
            data: Input data
            from_version: Source version
            to_version: Target version

        Returns:
            Transformed data
        """
        if from_version == to_version:
            return data

        # Get transformations
        transformations = self.get_transformations(from_version, to_version)

        # Apply transformations sequentially
        result = deepcopy(data)
        for transformation in transformations:
            result = transformation.apply(result)

        logger.debug(
            f"Transformed data from {from_version} to {to_version} "
            f"({len(transformations)} transformations)"
        )

        return result

    def transform_request(
        self, request_data: Dict[str, Any], client_version: APIVersion, server_version: APIVersion
    ) -> Dict[str, Any]:
        """
        Transform request data from client version to server version.

        Args:
            request_data: Request data from client
            client_version: Client API version
            server_version: Server API version

        Returns:
            Transformed request data
        """
        return self.transform_data(request_data, client_version, server_version)

    def transform_response(
        self, response_data: Dict[str, Any], server_version: APIVersion, client_version: APIVersion
    ) -> Dict[str, Any]:
        """
        Transform response data from server version to client version.

        Args:
            response_data: Response data from server
            server_version: Server API version
            client_version: Client API version

        Returns:
            Transformed response data
        """
        return self.transform_data(response_data, server_version, client_version)

    def get_schema_diff(self, version1: APIVersion, version2: APIVersion) -> Dict[str, List[str]]:
        """
        Get schema differences between two versions.

        Args:
            version1: First version
            version2: Second version

        Returns:
            Dictionary with added, removed, and changed fields
        """
        if version1 not in self.schemas or version2 not in self.schemas:
            raise ValueError("Both versions must be registered")

        schema1 = self.schemas[version1]
        schema2 = self.schemas[version2]

        fields1 = schema1.get_field_names()
        fields2 = schema2.get_field_names()

        return {
            "added": sorted(fields2 - fields1),
            "removed": sorted(fields1 - fields2),
            "common": sorted(fields1 & fields2),
        }

    def validate_backward_compatibility(
        self, old_version: APIVersion, new_version: APIVersion
    ) -> List[str]:
        """
        Validate backward compatibility between versions.

        Args:
            old_version: Older version
            new_version: Newer version

        Returns:
            List of breaking changes (empty if fully compatible)
        """
        if old_version >= new_version:
            raise ValueError("old_version must be less than new_version")

        breaking_changes = []

        # Get transformations
        transformations = self.get_transformations(old_version, new_version)

        for trans in transformations:
            if trans.change_type == FieldChange.REMOVED:
                breaking_changes.append(f"Field '{trans.source_field}' removed")
            elif trans.change_type == FieldChange.TYPE_CHANGED:
                breaking_changes.append(f"Field '{trans.source_field}' type changed")
            elif trans.change_type == FieldChange.REQUIRED_CHANGED:
                if trans.metadata.get("now_required"):
                    breaking_changes.append(f"Field '{trans.source_field}' is now required")

        return breaking_changes

    def _invalidate_cache(self, version: APIVersion) -> None:
        """Invalidate transformation cache involving version."""
        keys_to_remove = [key for key in self.transformation_cache.keys() if version in key]
        for key in keys_to_remove:
            del self.transformation_cache[key]

    def get_deprecation_warnings(self, version: APIVersion, data: Dict[str, Any]) -> List[str]:
        """
        Get field deprecation warnings for data.

        Args:
            version: API version
            data: Data to check

        Returns:
            List of deprecation warnings
        """
        warnings = []

        if version not in self.schemas:
            return warnings

        schema = self.schemas[version]

        for transformation in schema.transformations:
            if transformation.change_type == FieldChange.DEPRECATED:
                if transformation.source_field and transformation.source_field in data:
                    message = transformation.deprecation_message or (
                        f"Field '{transformation.source_field}' is deprecated."
                    )
                    if transformation.target_field:
                        message += f" Use '{transformation.target_field}' instead."
                    warnings.append(message)

        return warnings


__all__ = [
    "FieldChange",
    "FieldTransformation",
    "SchemaVersion",
    "SchemaEvolutionManager",
]
