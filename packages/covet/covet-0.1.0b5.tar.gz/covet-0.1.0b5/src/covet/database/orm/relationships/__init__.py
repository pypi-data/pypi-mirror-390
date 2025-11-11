"""
ORM Relationships Package

Comprehensive relationship system for CovetPy ORM:
- ForeignKey and OneToOneField relationships
- ManyToMany with through model support
- Generic Foreign Keys (polymorphic relationships)
- Polymorphic inheritance (STI, MTI, Abstract)
- Self-referential relationships (trees)
- Advanced cascading
- Reverse relation optimization

Example:
    from covet.database.orm.relationships import (
        ForeignKey,
        OneToOneField,
        ManyToManyField,
        GenericForeignKey,
        GenericRelation,
        ContentType,
        TreeNode,
        CASCADE,
        PROTECT
    )
"""

# This package contains advanced relationship features for CovetPy ORM
# Basic relationships (ForeignKey, OneToOneField, etc.) are in ../relationships.py
# The parent covet.database.orm module will load them from the .py file directly.
# This package provides extended features like:
# - ManyToMany with through models
# - Generic Foreign Keys (polymorphic relationships)
# - Polymorphic inheritance
# - Self-referential relationships (trees)
# - Advanced cascading

import importlib.util
import os

# Import basic relationship classes from sibling relationships.py file
import sys

# Load the sibling relationships.py module
_rel_py_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "relationships.py")
_spec = importlib.util.spec_from_file_location(
    "covet.database.orm._relationships_base", _rel_py_path
)
_relationships_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_relationships_base)

# Import basic relationship classes
ForeignKey = _relationships_base.ForeignKey
OneToOneField = _relationships_base.OneToOneField
RelatedManager = _relationships_base.RelatedManager
register_model = _relationships_base.register_model
get_model = _relationships_base.get_model
register_reverse_relation = _relationships_base.register_reverse_relation
get_reverse_relations = _relationships_base.get_reverse_relations

# Cascade behaviors
from .cascades import (
    CASCADE,
    DO_NOTHING,
    PROTECT,
    RESTRICT,
    SET,
    SET_DEFAULT,
    SET_NULL,
    BulkCascadeHandler,
    CascadeHandler,
    CustomCascadeHandler,
    ProtectedError,
    RestrictedError,
)

# Generic Foreign Keys
from .generic_foreign_key import (
    ContentType,
    GenericForeignKey,
    GenericForeignKeyDescriptor,
    GenericPrefetch,
    GenericRelation,
    GenericRelationDescriptor,
    GenericRelationManager,
)

# Many-to-Many relationships
from .many_to_many import (
    ManyToManyDescriptor,
    ManyToManyField,
    ManyToManyManager,
    ReverseManyToManyManager,
)

# Polymorphic models
from .polymorphic import (
    AbstractBaseClass,
    MultiTableInheritance,
    PolymorphicModelMixin,
    PolymorphicQuerySet,
    ProxyModel,
    SingleTableInheritance,
    setup_polymorphic_model,
)

# Reverse relations
from .reverse_relations import (
    PrefetchOptimizer,
    RelatedNameResolver,
    RelatedObjectDescriptor,
    ReverseRelationDescriptor,
    ReverseRelationManager,
)

# Self-referential relationships
from .self_referential import (
    NestedSetNode,
    PathMaterialization,
    TreeNode,
)

__all__ = [
    # Basic Relationships (from relationships.py)
    "ForeignKey",
    "OneToOneField",
    "RelatedManager",
    "register_model",
    "get_model",
    "register_reverse_relation",
    "get_reverse_relations",
    # Many-to-Many
    "ManyToManyField",
    "ManyToManyManager",
    "ManyToManyDescriptor",
    "ReverseManyToManyManager",
    # Generic Foreign Keys
    "ContentType",
    "GenericForeignKey",
    "GenericRelation",
    "GenericPrefetch",
    "GenericForeignKeyDescriptor",
    "GenericRelationDescriptor",
    "GenericRelationManager",
    # Polymorphic
    "PolymorphicModelMixin",
    "SingleTableInheritance",
    "MultiTableInheritance",
    "AbstractBaseClass",
    "ProxyModel",
    "setup_polymorphic_model",
    "PolymorphicQuerySet",
    # Reverse Relations
    "ReverseRelationDescriptor",
    "ReverseRelationManager",
    "PrefetchOptimizer",
    "RelatedNameResolver",
    "RelatedObjectDescriptor",
    # Self-Referential
    "TreeNode",
    "NestedSetNode",
    "PathMaterialization",
    # Cascades
    "CascadeHandler",
    "CustomCascadeHandler",
    "BulkCascadeHandler",
    "ProtectedError",
    "RestrictedError",
    "CASCADE",
    "PROTECT",
    "RESTRICT",
    "SET_NULL",
    "SET_DEFAULT",
    "DO_NOTHING",
    "SET",
]


# Version info
__version__ = "1.0.0"
__author__ = "CovetPy Team"
__description__ = "Production-ready ORM relationship system"
