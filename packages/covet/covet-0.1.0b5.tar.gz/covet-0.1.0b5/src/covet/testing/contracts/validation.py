"""
Contract validation utilities.

This module provides comprehensive contract validation capabilities for
testing API contracts against specifications.

Classes:
    ContractRequestValidator: Validates requests against contract specs
    ContractResponseValidator: Validates responses against contract specs
    SchemaValidator: Low-level JSON schema validation

Contract validation ensures that API implementations adhere to their
published contracts, preventing breaking changes and API drift.
"""

from typing import Any, Dict, List, Optional, Union

import jsonschema
from jsonschema import SchemaError, ValidationError


class ContractRequestValidator:
    """
    Validates requests against contract specifications.

    This validator checks that API requests conform to contract specifications,
    including path parameters, query parameters, headers, and request bodies.

    Example:
        >>> validator = ContractRequestValidator()
        >>> contract_spec = {
        ...     'endpoints': {
        ...         'POST /users': {
        ...             'request_schema': {
        ...                 'type': 'object',
        ...                 'required': ['username', 'email'],
        ...                 'properties': {
        ...                     'username': {'type': 'string'},
        ...                     'email': {'type': 'string', 'format': 'email'}
        ...                 }
        ...             }
        ...         }
        ...     }
        ... }
        >>> request = {
        ...     'method': 'POST',
        ...     'path': '/users',
        ...     'body': {'username': 'john', 'email': 'john@example.com'}
        ... }
        >>> result = validator.validate_request(request, contract_spec)
        >>> result['valid']
        True
    """

    def validate_request(
        self, request: Dict[str, Any], contract_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate request against contract specification.

        Validates the request method, path, and body against the contract
        specification. Returns detailed validation results including any
        errors found.

        Args:
            request: Request dictionary containing method, path, and body
            contract_spec: Contract specification with endpoint definitions

        Returns:
            Validation result with 'valid' flag and 'errors' list

        Example:
            >>> validator = ContractRequestValidator()
            >>> request = {
            ...     'method': 'POST',
            ...     'path': '/users',
            ...     'body': {'username': 'john'}
            ... }
            >>> contract = {
            ...     'endpoints': {
            ...         'POST /users': {
            ...             'request_schema': {
            ...                 'type': 'object',
            ...                 'required': ['username', 'email']
            ...             }
            ...         }
            ...     }
            ... }
            >>> result = validator.validate_request(request, contract)
            >>> result['valid']
            False
        """
        method = request.get("method", "GET").upper()
        path = request.get("path", "/")
        body = request.get("body", {})
        headers = request.get("headers", {})

        # Find matching endpoint in contract
        endpoint_key = f"{method} {path}"
        endpoints = contract_spec.get("endpoints", {})
        endpoint_spec = endpoints.get(endpoint_key)

        if not endpoint_spec:
            return {
                "valid": False,
                "errors": [
                    {
                        "field": "endpoint",
                        "message": f"No contract found for {endpoint_key}",
                        "code": "ENDPOINT_NOT_FOUND",
                    }
                ],
            }

        errors = []

        # Validate request body against schema
        request_schema = endpoint_spec.get("request_schema")
        if request_schema:
            schema_errors = self._validate_schema(body, request_schema)
            errors.extend(schema_errors)

        # Validate headers if specified
        required_headers = endpoint_spec.get("required_headers", [])
        for header in required_headers:
            if header not in headers:
                errors.append(
                    {
                        "field": f"headers.{header}",
                        "message": f"Required header '{header}' is missing",
                        "code": "MISSING_HEADER",
                    }
                )

        return {"valid": len(errors) == 0, "errors": errors}

    def _validate_schema(self, data: Any, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Validate data against JSON schema.

        Args:
            data: Data to validate
            schema: JSON schema

        Returns:
            List of validation errors
        """
        errors = []

        try:
            jsonschema.validate(data, schema)
        except ValidationError as e:
            errors.append(
                {
                    "field": ".".join(str(p) for p in e.path) if e.path else "root",
                    "message": e.message,
                    "code": "VALIDATION_ERROR",
                }
            )
        except SchemaError as e:
            errors.append(
                {
                    "field": "schema",
                    "message": f"Invalid schema: {e.message}",
                    "code": "SCHEMA_ERROR",
                }
            )

        return errors


class ContractResponseValidator:
    """
    Validates responses against contract specifications.

    This validator checks that API responses conform to contract specifications,
    including status codes, headers, and response bodies.

    Example:
        >>> validator = ContractResponseValidator()
        >>> contract_spec = {
        ...     'endpoints': {
        ...         'GET /users/123': {
        ...             'response_schema': {
        ...                 'type': 'object',
        ...                 'required': ['id', 'username'],
        ...                 'properties': {
        ...                     'id': {'type': 'string'},
        ...                     'username': {'type': 'string'}
        ...                 }
        ...             },
        ...             'expected_status': 200
        ...         }
        ...     }
        ... }
        >>> response = {
        ...     'method': 'GET',
        ...     'path': '/users/123',
        ...     'status': 200,
        ...     'body': {'id': '123', 'username': 'john'}
        ... }
        >>> result = validator.validate_response(response, contract_spec)
        >>> result['valid']
        True
    """

    def validate_response(
        self, response: Dict[str, Any], contract_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate response against contract specification.

        Validates the response status code, headers, and body against the
        contract specification.

        Args:
            response: Response dictionary containing method, path, status, and body
            contract_spec: Contract specification with endpoint definitions

        Returns:
            Validation result with 'valid' flag and 'errors' list

        Example:
            >>> validator = ContractResponseValidator()
            >>> response = {
            ...     'method': 'GET',
            ...     'path': '/users',
            ...     'status': 200,
            ...     'body': [{'id': '1', 'username': 'john'}]
            ... }
            >>> contract = {
            ...     'endpoints': {
            ...         'GET /users': {
            ...             'response_schema': {'type': 'array'},
            ...             'expected_status': 200
            ...         }
            ...     }
            ... }
            >>> result = validator.validate_response(response, contract)
            >>> result['valid']
            True
        """
        method = response.get("method", "GET").upper()
        path = response.get("path", "/")
        status = response.get("status", 200)
        body = response.get("body", {})
        headers = response.get("headers", {})

        # Find matching endpoint in contract
        endpoint_key = f"{method} {path}"
        endpoints = contract_spec.get("endpoints", {})
        endpoint_spec = endpoints.get(endpoint_key)

        if not endpoint_spec:
            return {
                "valid": False,
                "errors": [
                    {
                        "field": "endpoint",
                        "message": f"No contract found for {endpoint_key}",
                        "code": "ENDPOINT_NOT_FOUND",
                    }
                ],
            }

        errors = []

        # Validate status code
        expected_status = endpoint_spec.get("expected_status")
        if expected_status and status != expected_status:
            errors.append(
                {
                    "field": "status",
                    "message": f"Expected status {expected_status}, got {status}",
                    "code": "STATUS_MISMATCH",
                }
            )

        # Validate response body against schema
        response_schema = endpoint_spec.get("response_schema")
        if response_schema:
            schema_errors = self._validate_schema(body, response_schema)
            errors.extend(schema_errors)

        # Validate response headers if specified
        expected_headers = endpoint_spec.get("expected_headers", {})
        for header, expected_value in expected_headers.items():
            actual_value = headers.get(header)
            if actual_value != expected_value:
                errors.append(
                    {
                        "field": f"headers.{header}",
                        "message": f"Expected header '{header}' to be '{expected_value}', got '{actual_value}'",
                        "code": "HEADER_MISMATCH",
                    }
                )

        return {"valid": len(errors) == 0, "errors": errors}

    def _validate_schema(self, data: Any, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Validate data against JSON schema.

        Args:
            data: Data to validate
            schema: JSON schema

        Returns:
            List of validation errors
        """
        errors = []

        try:
            jsonschema.validate(data, schema)
        except ValidationError as e:
            errors.append(
                {
                    "field": ".".join(str(p) for p in e.path) if e.path else "root",
                    "message": e.message,
                    "code": "VALIDATION_ERROR",
                }
            )
        except SchemaError as e:
            errors.append(
                {
                    "field": "schema",
                    "message": f"Invalid schema: {e.message}",
                    "code": "SCHEMA_ERROR",
                }
            )

        return errors


class SchemaValidator:
    """
    Low-level JSON schema validation.

    Provides direct access to JSON schema validation with detailed error
    reporting and schema validation.

    Example:
        >>> validator = SchemaValidator()
        >>> schema = {
        ...     'type': 'object',
        ...     'required': ['name'],
        ...     'properties': {
        ...         'name': {'type': 'string'},
        ...         'age': {'type': 'integer'}
        ...     }
        ... }
        >>> data = {'name': 'John', 'age': 30}
        >>> result = validator.validate(data, schema)
        >>> result['valid']
        True
    """

    def validate(self, data: Any, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate data against JSON schema.

        Args:
            data: Data to validate
            schema: JSON schema

        Returns:
            Validation result with 'valid' flag and 'errors' list

        Example:
            >>> validator = SchemaValidator()
            >>> schema = {'type': 'string'}
            >>> result = validator.validate('hello', schema)
            >>> result['valid']
            True
            >>> result = validator.validate(123, schema)
            >>> result['valid']
            False
        """
        errors = []

        try:
            jsonschema.validate(data, schema)
            return {"valid": True, "errors": []}
        except ValidationError as e:
            errors.append(
                {
                    "field": ".".join(str(p) for p in e.path) if e.path else "root",
                    "message": e.message,
                    "code": "VALIDATION_ERROR",
                    "validator": e.validator,
                    "schema_path": list(e.schema_path),
                }
            )
        except SchemaError as e:
            errors.append(
                {
                    "field": "schema",
                    "message": f"Invalid schema: {e.message}",
                    "code": "SCHEMA_ERROR",
                }
            )

        return {"valid": False, "errors": errors}

    def validate_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that a schema is a valid JSON schema.

        Args:
            schema: JSON schema to validate

        Returns:
            Validation result with 'valid' flag and 'errors' list

        Example:
            >>> validator = SchemaValidator()
            >>> schema = {'type': 'object', 'properties': {}}
            >>> result = validator.validate_schema(schema)
            >>> result['valid']
            True
        """
        try:
            # Use Draft7Validator to check schema validity
            jsonschema.Draft7Validator.check_schema(schema)
            return {"valid": True, "errors": []}
        except SchemaError as e:
            return {
                "valid": False,
                "errors": [{"field": "schema", "message": str(e), "code": "INVALID_SCHEMA"}],
            }


# Export all validation classes
__all__ = [
    "ContractRequestValidator",
    "ContractResponseValidator",
    "SchemaValidator",
]
