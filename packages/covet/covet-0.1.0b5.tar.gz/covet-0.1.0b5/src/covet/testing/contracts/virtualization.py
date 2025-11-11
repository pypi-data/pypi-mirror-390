"""
Service virtualization for contract testing.

This module provides service virtualization capabilities for contract testing,
allowing creation of virtual services from contract specifications.

Classes:
    ServiceVirtualizer: Creates virtual services from contract specs
    VirtualService: Virtual service instance
    ResponseGenerator: Generates dynamic responses from templates
    StatefulVirtualService: Stateful virtual service with in-memory storage

Service virtualization allows testing of API contracts without requiring
the actual service implementation, enabling parallel development and
comprehensive integration testing.
"""

import json
import re
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4


class ServiceVirtualizer:
    """
    Creates virtual services from contract specifications.

    This class takes contract specifications (typically in JSON/YAML format)
    and creates virtual service instances that can simulate the behavior
    of real services for testing purposes.

    Example:
        >>> virtualizer = ServiceVirtualizer()
        >>> contract = {
        ...     'service_name': 'user-service',
        ...     'base_path': '/api/v1',
        ...     'endpoints': [
        ...         {
        ...             'method': 'GET',
        ...             'path': '/users/{id}',
        ...             'response_template': {'id': '{id}', 'name': 'User {id}'}
        ...         }
        ...     ]
        ... }
        >>> virtual_service = virtualizer.create_virtual_service(contract)
    """

    def create_virtual_service(self, contract: Dict[str, Any]) -> "VirtualService":
        """
        Create a virtual service from contract specification.

        Args:
            contract: Contract specification containing service metadata and endpoints

        Returns:
            VirtualService instance configured according to the contract

        Example:
            >>> contract = {
            ...     'service_name': 'api-service',
            ...     'base_path': '/api',
            ...     'endpoints': []
            ... }
            >>> service = virtualizer.create_virtual_service(contract)
            >>> service.service_name
            'api-service'
        """
        return VirtualService(
            service_name=contract.get("service_name", "unknown"),
            base_path=contract.get("base_path", "/"),
            endpoints=contract.get("endpoints", []),
        )


class VirtualService:
    """
    Virtual service instance.

    Represents a virtualized service that can handle requests according to
    contract specifications. Stores service metadata and endpoint configurations.

    Attributes:
        service_name: Name of the virtualized service
        base_path: Base URL path for all endpoints
        endpoints: List of endpoint configurations

    Example:
        >>> service = VirtualService(
        ...     service_name='user-api',
        ...     base_path='/api/v1',
        ...     endpoints=[
        ...         {'method': 'GET', 'path': '/users', 'response': []}
        ...     ]
        ... )
    """

    def __init__(self, service_name: str, base_path: str, endpoints: List[Dict[str, Any]]):
        """
        Initialize virtual service.

        Args:
            service_name: Name of the service
            base_path: Base URL path
            endpoints: List of endpoint configurations
        """
        self.service_name = service_name
        self.base_path = base_path
        self.endpoints = endpoints
        self._endpoint_map: Dict[str, Dict[str, Any]] = {}
        self._build_endpoint_map()

    def _build_endpoint_map(self) -> None:
        """
        Build internal endpoint mapping for fast lookup.

        Creates a dictionary mapping endpoint keys (method + path) to
        endpoint configurations for efficient request handling.
        """
        for endpoint in self.endpoints:
            method = endpoint.get("method", "GET").upper()
            path = endpoint.get("path", "/")
            key = f"{method} {path}"
            self._endpoint_map[key] = endpoint

    def find_endpoint(self, method: str, path: str) -> Optional[Dict[str, Any]]:
        """
        Find endpoint configuration for given method and path.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: URL path

        Returns:
            Endpoint configuration if found, None otherwise

        Example:
            >>> service = VirtualService('api', '/', [
            ...     {'method': 'GET', 'path': '/users'}
            ... ])
            >>> endpoint = service.find_endpoint('GET', '/users')
            >>> endpoint is not None
            True
        """
        key = f"{method.upper()} {path}"
        return self._endpoint_map.get(key)

    def get_endpoint_count(self) -> int:
        """
        Get total number of endpoints.

        Returns:
            Number of configured endpoints
        """
        return len(self.endpoints)


class ResponseGenerator:
    """
    Generates dynamic responses based on templates.

    This class supports template-based response generation with parameter
    substitution, enabling creation of dynamic responses that vary based
    on request parameters and context.

    Template Syntax:
        - Use {param_name} for parameter substitution
        - Parameters come from request path, query, or body
        - Context provides additional runtime values

    Example:
        >>> generator = ResponseGenerator()
        >>> template = {'id': '{user_id}', 'name': 'User {user_id}'}
        >>> params = {'user_id': '123'}
        >>> response = generator.generate_response(template, params, {})
        >>> response['id']
        '123'
    """

    def generate_response(
        self, template: Dict[str, Any], parameters: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate response from template with parameter substitution.

        Substitutes template placeholders with values from parameters and context.
        Supports nested dictionaries and lists.

        Args:
            template: Response template with placeholders
            parameters: Request parameters to substitute
            context: Additional context values

        Returns:
            Generated response with substituted values

        Example:
            >>> generator = ResponseGenerator()
            >>> template = {
            ...     'id': '{id}',
            ...     'timestamp': '{timestamp}',
            ...     'user': {'name': '{name}'}
            ... }
            >>> params = {'id': '123', 'name': 'John'}
            >>> context = {'timestamp': '2025-10-11T00:00:00'}
            >>> result = generator.generate_response(template, params, context)
            >>> result['id']
            '123'
        """
        # Combine parameters and context
        substitutions = {**parameters, **context}

        # Convert template to JSON string for easy substitution
        template_str = json.dumps(template)

        # Perform substitutions
        for key, value in substitutions.items():
            placeholder = f"{{{key}}}"
            template_str = template_str.replace(placeholder, str(value))

        # Parse back to dictionary
        try:
            result = json.loads(template_str)
        except json.JSONDecodeError:
            # If parsing fails, return original template
            result = template

        return result

    def add_timestamp(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add current timestamp to response.

        Args:
            response: Response dictionary

        Returns:
            Response with timestamp field added
        """
        response["timestamp"] = datetime.utcnow().isoformat()
        return response


class StatefulVirtualService:
    """
    Stateful virtual service with in-memory storage.

    Provides a fully functional virtual service that maintains state across
    requests. Supports standard CRUD operations (Create, Read, Update, Delete)
    with automatic ID generation and resource management.

    This is useful for integration testing where state persistence is needed
    across multiple test requests.

    Attributes:
        service_name: Name of the service
        storage: In-memory storage for resources
        id_counter: Counter for generating sequential IDs

    Example:
        >>> service = StatefulVirtualService('user-service')
        >>> # Create a user
        >>> response = service.handle_request(
        ...     'POST', '/users',
        ...     body={'username': 'john', 'email': 'john@example.com'}
        ... )
        >>> response['status']
        201
        >>> # Get the user
        >>> user_id = response['body']['id']
        >>> response = service.handle_request('GET', f'/users/{user_id}')
        >>> response['status']
        200
    """

    def __init__(self, service_name: str):
        """
        Initialize stateful virtual service.

        Args:
            service_name: Name of the service
        """
        self.service_name = service_name
        self.storage: Dict[str, Any] = {}
        self.id_counter = 1

    def handle_request(
        self, method: str, path: str, body: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle request and return response.

        Processes HTTP requests with CRUD semantics:
        - POST: Create new resource
        - GET: Retrieve resource(s)
        - PUT: Update existing resource
        - DELETE: Delete resource

        Args:
            method: HTTP method
            path: URL path
            body: Optional request body

        Returns:
            Response dictionary with status and body

        Example:
            >>> service = StatefulVirtualService('api')
            >>> # Create resource
            >>> resp = service.handle_request(
            ...     'POST', '/items',
            ...     body={'name': 'Item 1'}
            ... )
            >>> resp['status']
            201
            >>> # Get resource
            >>> item_id = resp['body']['id']
            >>> resp = service.handle_request('GET', f'/items/{item_id}')
            >>> resp['body']['name']
            'Item 1'
        """
        method = method.upper()

        # POST - Create resource
        if method == "POST":
            return self._handle_create(path, body or {})

        # GET - Retrieve resource
        elif method == "GET":
            return self._handle_read(path)

        # PUT - Update resource
        elif method == "PUT":
            return self._handle_update(path, body or {})

        # DELETE - Delete resource
        elif method == "DELETE":
            return self._handle_delete(path)

        # Unsupported method
        return {"status": 405, "body": {"error": "Method not allowed"}}

    def _handle_create(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new resource."""
        resource_id = str(self.id_counter)
        self.id_counter += 1

        resource = {**body, "id": resource_id, "created_at": datetime.utcnow().isoformat()}

        self.storage[resource_id] = resource

        return {"status": 201, "body": resource}

    def _handle_read(self, path: str) -> Dict[str, Any]:
        """Read resource(s)."""
        # Extract ID from path (e.g., /users/123 -> 123)
        match = re.search(r"/(\w+)$", path)

        if match:
            # Single resource
            resource_id = match.group(1)
            if resource_id in self.storage:
                return {"status": 200, "body": self.storage[resource_id]}
            else:
                return {"status": 404, "body": {"error": "Not found"}}
        else:
            # List all resources
            return {"status": 200, "body": list(self.storage.values())}

    def _handle_update(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing resource."""
        match = re.search(r"/(\w+)$", path)

        if not match:
            return {"status": 400, "body": {"error": "Resource ID required"}}

        resource_id = match.group(1)

        if resource_id in self.storage:
            # Update resource (preserve id and created_at)
            resource = self.storage[resource_id]
            resource.update(body)
            resource["updated_at"] = datetime.utcnow().isoformat()

            return {"status": 200, "body": resource}
        else:
            return {"status": 404, "body": {"error": "Not found"}}

    def _handle_delete(self, path: str) -> Dict[str, Any]:
        """Delete resource."""
        match = re.search(r"/(\w+)$", path)

        if not match:
            return {"status": 400, "body": {"error": "Resource ID required"}}

        resource_id = match.group(1)

        if resource_id in self.storage:
            del self.storage[resource_id]
            return {"status": 204, "body": None}
        else:
            return {"status": 404, "body": {"error": "Not found"}}

    def reset(self) -> None:
        """
        Reset service state.

        Clears all stored resources and resets ID counter.
        Useful for test cleanup between test cases.
        """
        self.storage.clear()
        self.id_counter = 1

    def get_resource_count(self) -> int:
        """
        Get total number of stored resources.

        Returns:
            Number of resources in storage
        """
        return len(self.storage)


# Export all virtualization classes
__all__ = [
    "ServiceVirtualizer",
    "VirtualService",
    "ResponseGenerator",
    "StatefulVirtualService",
]
