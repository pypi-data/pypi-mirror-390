"""GraphQL type system."""

class GraphQLType:
    """Base GraphQL type."""
    pass

class GraphQLObjectType(GraphQLType):
    """GraphQL object type."""
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields

__all__ = ["GraphQLType", "GraphQLObjectType", "GraphQLField"]



class ObjectType(GraphQLType):
    """GraphQL object type."""
    pass


# Auto-generated stubs for missing exports

class GraphQLField:
    """Stub class for GraphQLField."""

    def __init__(self, *args, **kwargs):
        pass

