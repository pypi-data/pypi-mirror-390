"""
GraphQL Playground Integration

Provides GraphQL Playground, GraphiQL, and Apollo Sandbox interfaces.
"""

from typing import Optional


class GraphQLPlayground:
    """GraphQL Playground configuration."""

    def __init__(
        self,
        endpoint: str = "/graphql",
        subscriptions_endpoint: Optional[str] = None,
        title: str = "GraphQL Playground",
        version: str = "1.7.25",
    ):
        """
        Initialize playground config.

        Args:
            endpoint: GraphQL endpoint
            subscriptions_endpoint: WebSocket endpoint for subscriptions
            title: Page title
            version: Playground version
        """
        self.endpoint = endpoint
        self.subscriptions_endpoint = subscriptions_endpoint or endpoint
        self.title = title
        self.version = version

    def get_html(self) -> str:
        """Get HTML for GraphQL Playground."""
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{self.title}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/graphql-playground-react@{self.version}/build/static/css/index.css" />
    <link rel="shortcut icon" href="https://cdn.jsdelivr.net/npm/graphql-playground-react@{self.version}/build/favicon.png" />
    <script src="https://cdn.jsdelivr.net/npm/graphql-playground-react@{self.version}/build/static/js/middleware.js"></script>
</head>
<body>
    <div id="root"></div>
    <script>
        window.addEventListener('load', function (event) {{
            GraphQLPlayground.init(document.getElementById('root'), {{
                endpoint: '{self.endpoint}',
                subscriptionEndpoint: '{self.subscriptions_endpoint}',
                settings: {{
                    'editor.theme': 'dark',
                    'editor.cursorShape': 'line',
                    'editor.reuseHeaders': true,
                    'tracing.hideTracingResponse': false,
                    'editor.fontSize': 14,
                }}
            }})
        }})
    </script>
</body>
</html>"""


class GraphiQLPlayground:
    """GraphiQL interface configuration."""

    def __init__(
        self,
        endpoint: str = "/graphql",
        subscriptions_endpoint: Optional[str] = None,
        title: str = "GraphiQL",
        version: str = "2.0.0",
    ):
        """
        Initialize GraphiQL config.

        Args:
            endpoint: GraphQL endpoint
            subscriptions_endpoint: WebSocket endpoint
            title: Page title
            version: GraphiQL version
        """
        self.endpoint = endpoint
        self.subscriptions_endpoint = subscriptions_endpoint
        self.title = title
        self.version = version

    def get_html(self) -> str:
        """Get HTML for GraphiQL."""
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>{self.title}</title>
    <style>
        body {{
            height: 100%;
            margin: 0;
            width: 100%;
            overflow: hidden;
        }}
        #graphiql {{
            height: 100vh;
        }}
    </style>
    <script crossorigin src="https://unpkg.com/react@17/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@17/umd/react-dom.production.min.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/graphiql@{self.version}/graphiql.min.css" />
</head>
<body>
    <div id="graphiql">Loading...</div>
    <script src="https://unpkg.com/graphiql@{self.version}/graphiql.min.js" type="application/javascript"></script>
    <script>
        ReactDOM.render(
            React.createElement(GraphiQL, {{
                fetcher: GraphiQL.createFetcher({{
                    url: '{self.endpoint}',
                    subscriptionUrl: '{self.subscriptions_endpoint or self.endpoint}',
                }}),
                defaultEditorToolsVisibility: true,
            }}),
            document.getElementById('graphiql'),
        );
    </script>
</body>
</html>"""


class ApolloSandbox:
    """Apollo Sandbox configuration."""

    def __init__(
        self,
        endpoint: str = "/graphql",
        title: str = "Apollo Sandbox",
    ):
        """
        Initialize Apollo Sandbox config.

        Args:
            endpoint: GraphQL endpoint
            title: Page title
        """
        self.endpoint = endpoint
        self.title = title

    def get_html(self) -> str:
        """Get HTML for Apollo Sandbox."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{self.title}</title>
    <style>
        body {{
            margin: 0;
            overflow-x: hidden;
            overflow-y: hidden;
        }}
        #embeddedSandbox {{
            height: 100vh;
            width: 100vw;
        }}
    </style>
</head>
<body>
    <div id="embeddedSandbox"></div>
    <script src="https://embeddable-sandbox.cdn.apollographql.com/_latest/embeddable-sandbox.umd.production.min.js"></script>
    <script>
        new window.EmbeddedSandbox({{
            target: "#embeddedSandbox",
            initialEndpoint: "{self.endpoint}",
        }});
    </script>
</body>
</html>"""


def playground_html(
    endpoint: str = "/graphql",
    subscriptions_endpoint: Optional[str] = None,
    title: str = "GraphQL Playground",
    playground_type: str = "graphql-playground",
) -> str:
    """
    Get playground HTML.

    Args:
        endpoint: GraphQL endpoint
        subscriptions_endpoint: WebSocket endpoint
        title: Page title
        playground_type: Type ('graphql-playground', 'graphiql', or 'apollo-sandbox')

    Returns:
        HTML string
    """
    if playground_type == "graphiql":
        playground = GraphiQLPlayground(endpoint, subscriptions_endpoint, title)
    elif playground_type == "apollo-sandbox":
        playground = ApolloSandbox(endpoint, title)
    else:
        playground = GraphQLPlayground(endpoint, subscriptions_endpoint, title)

    return playground.get_html()


__all__ = [
    "GraphQLPlayground",
    "GraphiQLPlayground",
    "ApolloSandbox",
    "playground_html",
]
