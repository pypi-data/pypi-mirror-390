"""
CovetPy ORM - Django-style Object-Relational Mapping

Enterprise-grade ORM with Active Record pattern, providing intuitive database
operations, comprehensive field types, relationship management, and signal support.

Quick Start:
    from covet.database.orm import Model, CharField, EmailField, ForeignKey

    class User(Model):
        username = CharField(max_length=100, unique=True)
        email = EmailField(unique=True)
        created_at = DateTimeField(auto_now_add=True)

        class Meta:
            db_table = 'users'
            ordering = ['-created_at']

    # Create
    user = await User.objects.create(
        username='alice',
        email='alice@example.com'
    )

    # Read
    user = await User.objects.get(id=1)
    users = await User.objects.filter(is_active=True).all()

    # Update
    user.username = 'alice_updated'
    await user.save()

    # Delete
    await user.delete()

Features:
    - Active Record pattern for intuitive CRUD operations
    - 17+ field types with comprehensive validation
    - Django-compatible QuerySet API with field lookups
    - ForeignKey, OneToOne, and ManyToMany relationships
    - Signal system (pre_save, post_save, pre_delete, etc.)
    - Eager loading (select_related, prefetch_related)
    - Aggregation and annotation support
    - Model Meta options for advanced configuration
    - Automatic table name generation
    - Transaction support
    - Connection pooling and query optimization
"""

# Relationship fields - import from relationships.py module (not relationships/ package)
# Note: There's both relationships.py and relationships/ directory
# Python prioritizes packages, so we import the module using importlib
import importlib

# Field types
from .fields import (
    ArrayField,
    BigIntegerField,
    BinaryField,
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    DecimalField,
    EmailField,
    EnumField,
    Field,
    FloatField,
    IntegerField,
    JSONField,
    SmallIntegerField,
    TextField,
    TimeField,
    URLField,
    UUIDField,
)

# Core Model classes
from .models import (
    Index,
    Model,
    ModelMeta,
    ModelOptions,
    ModelState,
    MultipleObjectsReturned,
    ObjectDoesNotExist,
)

_relationships_module = importlib.import_module(".relationships", package="covet.database.orm")
# Get the actual module file, not the package
if hasattr(_relationships_module, "__path__"):  # It's a package
    # Load the sibling .py file instead
    import importlib.util
    import os

    _rel_py_path = os.path.join(os.path.dirname(__file__), "relationships.py")
    _spec = importlib.util.spec_from_file_location(
        "covet.database.orm._relationships_module", _rel_py_path
    )
    _relationships_module = importlib.util.module_from_spec(_spec)
    # Set up proper module context before execution
    import sys

    sys.modules["covet.database.orm._relationships_module"] = _relationships_module
    _spec.loader.exec_module(_relationships_module)

ForeignKey = _relationships_module.ForeignKey
OneToOneField = _relationships_module.OneToOneField
ManyToManyField = _relationships_module.ManyToManyField
RelatedManager = _relationships_module.RelatedManager
CASCADE = _relationships_module.CASCADE
PROTECT = _relationships_module.PROTECT
RESTRICT = _relationships_module.RESTRICT
SET_NULL = _relationships_module.SET_NULL
SET_DEFAULT = _relationships_module.SET_DEFAULT
DO_NOTHING = _relationships_module.DO_NOTHING
register_model = _relationships_module.register_model
get_model = _relationships_module.get_model
register_reverse_relation = _relationships_module.register_reverse_relation
get_reverse_relations = _relationships_module.get_reverse_relations

# Adapter Registry
from .adapter_registry import (
    AdapterRegistry,
    get_adapter,
    get_adapter_registry,
    register_adapter,
    unregister_adapter,
)

# Batch Operations
from .batch_operations import (
    BatchConfig,
    BatchOperations,
    BatchResult,
    BatchStrategy,
    ConflictResolution,
)

# Explain Analysis
from .explain import (
    ExplainAnalyzer,
    ExplainNode,
    ExplainPlan,
    JoinType,
    ScanType,
)

# Index Advisor
from .index_advisor import (
    IndexAdvisor,
    IndexAnalysis,
    IndexRecommendation,
    IndexType,
    RecommendationPriority,
)

# Managers and QuerySets
from .managers import (
    Avg,
    Count,
    Max,
    Min,
    ModelManager,
    Q,
    QuerySet,
    Sum,
)

# Query Optimization
from .optimizer import (
    JoinOptimizer,
    OptimizationLevel,
    OptimizationResult,
    QueryAnalysis,
    QueryComplexity,
    QueryOptimizer,
    SubqueryOptimizer,
)

# Query Profiler
from .profiler import (
    AlertLevel,
    ProfilerConfig,
    QueryProfile,
    QueryProfiler,
    QueryStatistics,
    QueryType,
)

# Query Cache
from .query_cache import (
    CacheBackend,
    CacheConfig,
    CacheStats,
    InvalidationStrategy,
    QueryCache,
)

# Signals
from .signals import (
    Signal,
    m2m_changed,
    post_delete,
    post_init,
    post_save,
    post_update,
    pre_delete,
    pre_init,
    pre_save,
    pre_update,
    receiver,
)

__version__ = "1.0.0"

__all__ = [
    # Core classes
    "Model",
    "ModelMeta",
    "ModelOptions",
    "ModelState",
    "ObjectDoesNotExist",
    "MultipleObjectsReturned",
    "Index",
    # Fields
    "Field",
    "CharField",
    "TextField",
    "IntegerField",
    "BigIntegerField",
    "SmallIntegerField",
    "FloatField",
    "DecimalField",
    "BooleanField",
    "DateTimeField",
    "DateField",
    "TimeField",
    "JSONField",
    "UUIDField",
    "EmailField",
    "URLField",
    "BinaryField",
    "ArrayField",
    "EnumField",
    # Relationships
    "ForeignKey",
    "OneToOneField",
    "ManyToManyField",
    "RelatedManager",
    "CASCADE",
    "PROTECT",
    "RESTRICT",
    "SET_NULL",
    "SET_DEFAULT",
    "DO_NOTHING",
    "register_model",
    "get_model",
    "register_reverse_relation",
    "get_reverse_relations",
    # Managers
    "ModelManager",
    "QuerySet",
    "Q",
    "Count",
    "Sum",
    "Avg",
    "Max",
    "Min",
    # Signals
    "Signal",
    "receiver",
    "pre_init",
    "post_init",
    "pre_save",
    "post_save",
    "pre_delete",
    "post_delete",
    "pre_update",
    "post_update",
    "m2m_changed",
    # Adapter Registry
    "AdapterRegistry",
    "get_adapter_registry",
    "register_adapter",
    "get_adapter",
    "unregister_adapter",
    # Query Optimization
    "QueryOptimizer",
    "JoinOptimizer",
    "SubqueryOptimizer",
    "QueryAnalysis",
    "OptimizationResult",
    "OptimizationLevel",
    "QueryComplexity",
    # Explain Analysis
    "ExplainAnalyzer",
    "ExplainPlan",
    "ExplainNode",
    "ScanType",
    "JoinType",
    # Index Advisor
    "IndexAdvisor",
    "IndexRecommendation",
    "IndexAnalysis",
    "IndexType",
    "RecommendationPriority",
    # Query Cache
    "QueryCache",
    "CacheConfig",
    "CacheStats",
    "CacheBackend",
    "InvalidationStrategy",
    # Query Profiler
    "QueryProfiler",
    "ProfilerConfig",
    "QueryProfile",
    "QueryStatistics",
    "QueryType",
    "AlertLevel",
    # Batch Operations
    "BatchOperations",
    "BatchConfig",
    "BatchResult",
    "BatchStrategy",
    "ConflictResolution",
]
