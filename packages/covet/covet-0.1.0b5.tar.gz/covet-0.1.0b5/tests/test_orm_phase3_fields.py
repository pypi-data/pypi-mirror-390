"""
Comprehensive test suite for Phase 3 ORM Fields (PostgreSQL-specific)

Tests:
- HStoreField (key-value store)
- InetField (network addresses with CIDR)
- CidrField (network ranges)

Coverage:
- Field instantiation and configuration
- Type validation
- Value conversion (to_python, get_db_value)
- Database type mapping across all adapters
- PostgreSQL-specific features
- Edge cases and error handling
"""

import json
import pytest
from decimal import Decimal

from src.covet.database.orm.fields import (
    HStoreField,
    InetField,
    CidrField,
)


# =============================================================================
# HStoreField Tests (18 tests)
# =============================================================================


class TestHStoreField:
    """Test HStoreField (PostgreSQL key-value store)."""

    def test_hstore_field_instantiation(self):
        """Test basic HStore field instantiation."""
        field = HStoreField()
        assert isinstance(field, HStoreField)

    def test_hstore_field_validate_valid_dict(self):
        """Test validation accepts valid dict with string keys/values."""
        field = HStoreField()
        field.name = 'attributes'

        value = {'color': 'red', 'size': 'large', 'material': 'cotton'}
        result = field.validate(value)
        assert result == value

    def test_hstore_field_validate_null_values(self):
        """Test validation accepts None values."""
        field = HStoreField()
        field.name = 'attributes'

        value = {'color': 'red', 'size': None}
        result = field.validate(value)
        assert result == value

    def test_hstore_field_validate_empty_dict(self):
        """Test validation accepts empty dict."""
        field = HStoreField()
        field.name = 'attributes'

        result = field.validate({})
        assert result == {}

    def test_hstore_field_validate_none(self):
        """Test validation accepts None."""
        field = HStoreField()
        field.name = 'attributes'

        result = field.validate(None)
        assert result is None

    def test_hstore_field_validate_invalid_type(self):
        """Test validation rejects non-dict types."""
        field = HStoreField()
        field.name = 'attributes'

        with pytest.raises(ValueError, match="must be a dictionary"):
            field.validate("not a dict")

        with pytest.raises(ValueError, match="must be a dictionary"):
            field.validate([1, 2, 3])

    def test_hstore_field_validate_non_string_keys(self):
        """Test validation rejects non-string keys."""
        field = HStoreField()
        field.name = 'attributes'

        with pytest.raises(ValueError, match="All keys must be strings"):
            field.validate({123: 'value'})

        with pytest.raises(ValueError, match="All keys must be strings"):
            field.validate({('a', 'b'): 'value'})

    def test_hstore_field_validate_non_string_values(self):
        """Test validation rejects non-string values (except None)."""
        field = HStoreField()
        field.name = 'attributes'

        with pytest.raises(ValueError, match="All values must be strings or None"):
            field.validate({'color': 123})

        with pytest.raises(ValueError, match="All values must be strings or None"):
            field.validate({'color': ['red', 'blue']})

    def test_hstore_field_to_python_from_dict(self):
        """Test conversion from dict (PostgreSQL HSTORE)."""
        field = HStoreField()
        field.name = 'attributes'

        value = {'color': 'red', 'size': 'large'}
        result = field.to_python(value)
        assert result == value

    def test_hstore_field_to_python_from_json(self):
        """Test conversion from JSON string (SQLite, MySQL fallback)."""
        field = HStoreField()
        field.name = 'attributes'

        json_str = '{"color": "red", "size": "large"}'
        result = field.to_python(json_str)
        assert result == {'color': 'red', 'size': 'large'}

    def test_hstore_field_to_python_invalid_json(self):
        """Test conversion fails with invalid JSON."""
        field = HStoreField()
        field.name = 'attributes'

        with pytest.raises(ValueError, match="Cannot parse JSON to dict"):
            field.to_python('{invalid json}')

    def test_hstore_field_to_python_none(self):
        """Test conversion returns None for None."""
        field = HStoreField()
        field.name = 'attributes'

        assert field.to_python(None) is None

    def test_hstore_field_get_db_type_postgresql(self):
        """Test database type for PostgreSQL."""
        field = HStoreField()
        assert field.get_db_type('postgresql') == 'HSTORE'

    def test_hstore_field_get_db_type_mysql(self):
        """Test database type for MySQL."""
        field = HStoreField()
        assert field.get_db_type('mysql') == 'JSON'

    def test_hstore_field_get_db_type_sqlite(self):
        """Test database type for SQLite."""
        field = HStoreField()
        assert field.get_db_type('sqlite') == 'TEXT'

    def test_hstore_field_get_db_type_mongodb(self):
        """Test database type for MongoDB."""
        field = HStoreField()
        assert field.get_db_type('mongodb') == 'Object'

    def test_hstore_field_get_db_value_postgresql(self):
        """Test database value for PostgreSQL (dict)."""
        field = HStoreField()
        field.name = 'attributes'

        value = {'color': 'red', 'size': 'large'}
        result = field.get_db_value(value, 'postgresql')
        assert result == value

    def test_hstore_field_get_db_value_sqlite(self):
        """Test database value for SQLite (JSON string)."""
        field = HStoreField()
        field.name = 'attributes'

        value = {'color': 'red', 'size': 'large'}
        result = field.get_db_value(value, 'sqlite')
        assert isinstance(result, str)
        assert json.loads(result) == value


# =============================================================================
# InetField Tests (16 tests)
# =============================================================================


class TestInetField:
    """Test InetField (network addresses with optional CIDR)."""

    def test_inet_field_instantiation(self):
        """Test basic INET field instantiation."""
        field = InetField()
        assert isinstance(field, InetField)

    def test_inet_field_instantiation_with_protocol(self):
        """Test INET field with protocol restriction."""
        field_ipv4 = InetField(protocol='IPv4')
        assert field_ipv4.protocol == 'IPv4'

        field_ipv6 = InetField(protocol='IPv6')
        assert field_ipv6.protocol == 'IPv6'

    def test_inet_field_instantiation_invalid_protocol(self):
        """Test INET field rejects invalid protocol."""
        with pytest.raises(ValueError, match="protocol must be"):
            InetField(protocol='IPv5')

    def test_inet_field_validate_ipv4_address(self):
        """Test validation accepts IPv4 address."""
        field = InetField()
        field.name = 'ip_address'

        result = field.validate('192.168.1.100')
        assert result == '192.168.1.100'

    def test_inet_field_validate_ipv4_with_cidr(self):
        """Test validation accepts IPv4 with CIDR."""
        field = InetField()
        field.name = 'ip_address'

        result = field.validate('192.168.1.100/24')
        assert result == '192.168.1.100/24'

    def test_inet_field_validate_ipv6_address(self):
        """Test validation accepts IPv6 address."""
        field = InetField()
        field.name = 'ip_address'

        result = field.validate('2001:db8::1')
        assert result == '2001:db8::1'

    def test_inet_field_validate_ipv6_with_cidr(self):
        """Test validation accepts IPv6 with CIDR."""
        field = InetField()
        field.name = 'ip_address'

        result = field.validate('2001:db8::/32')
        assert result == '2001:db8::/32'

    def test_inet_field_validate_protocol_restriction_ipv4(self):
        """Test IPv4-only field rejects IPv6."""
        field = InetField(protocol='IPv4')
        field.name = 'ip_address'

        # IPv4 should pass
        field.validate('192.168.1.1')

        # IPv6 should fail
        with pytest.raises(ValueError, match="Only IPv4 addresses allowed"):
            field.validate('2001:db8::1')

    def test_inet_field_validate_protocol_restriction_ipv6(self):
        """Test IPv6-only field rejects IPv4."""
        field = InetField(protocol='IPv6')
        field.name = 'ip_address'

        # IPv6 should pass
        field.validate('2001:db8::1')

        # IPv4 should fail
        with pytest.raises(ValueError, match="Only IPv6 addresses allowed"):
            field.validate('192.168.1.1')

    def test_inet_field_validate_invalid_address(self):
        """Test validation rejects invalid addresses."""
        field = InetField()
        field.name = 'ip_address'

        with pytest.raises(ValueError, match="Invalid network address"):
            field.validate('999.999.999.999')

        with pytest.raises(ValueError, match="Invalid network address"):
            field.validate('not an ip')

    def test_inet_field_validate_none(self):
        """Test validation accepts None."""
        field = InetField()
        field.name = 'ip_address'

        result = field.validate(None)
        assert result is None

    def test_inet_field_validate_invalid_type(self):
        """Test validation rejects non-string types."""
        field = InetField()
        field.name = 'ip_address'

        with pytest.raises(ValueError, match="must be a string"):
            field.validate(12345)

    def test_inet_field_get_db_type_postgresql(self):
        """Test database type for PostgreSQL."""
        field = InetField()
        assert field.get_db_type('postgresql') == 'INET'

    def test_inet_field_get_db_type_mysql(self):
        """Test database type for MySQL."""
        field = InetField()
        assert field.get_db_type('mysql') == 'VARCHAR(45)'

    def test_inet_field_to_python(self):
        """Test conversion from database value."""
        field = InetField()
        field.name = 'ip_address'

        assert field.to_python('192.168.1.1') == '192.168.1.1'
        assert field.to_python(None) is None

    def test_inet_field_get_db_value(self):
        """Test conversion to database value."""
        field = InetField()
        field.name = 'ip_address'

        assert field.get_db_value('192.168.1.1', 'postgresql') == '192.168.1.1'
        assert field.get_db_value(None, 'postgresql') is None


# =============================================================================
# CidrField Tests (16 tests)
# =============================================================================


class TestCidrField:
    """Test CidrField (network ranges with strict validation)."""

    def test_cidr_field_instantiation(self):
        """Test basic CIDR field instantiation."""
        field = CidrField()
        assert isinstance(field, CidrField)

    def test_cidr_field_instantiation_with_protocol(self):
        """Test CIDR field with protocol restriction."""
        field_ipv4 = CidrField(protocol='IPv4')
        assert field_ipv4.protocol == 'IPv4'

        field_ipv6 = CidrField(protocol='IPv6')
        assert field_ipv6.protocol == 'IPv6'

    def test_cidr_field_validate_ipv4_network(self):
        """Test validation accepts valid IPv4 network."""
        field = CidrField()
        field.name = 'subnet'

        result = field.validate('192.168.1.0/24')
        assert result == '192.168.1.0/24'

    def test_cidr_field_validate_ipv6_network(self):
        """Test validation accepts valid IPv6 network."""
        field = CidrField()
        field.name = 'subnet'

        result = field.validate('2001:db8::/32')
        assert result == '2001:db8::/32'

    def test_cidr_field_validate_host_bits_set(self):
        """Test validation rejects networks with host bits set."""
        field = CidrField()
        field.name = 'subnet'

        # Host bits are non-zero, should fail
        with pytest.raises(ValueError, match="host bits must be zero"):
            field.validate('192.168.1.100/24')

        # Error message should suggest correct network
        try:
            field.validate('192.168.1.100/24')
        except ValueError as e:
            assert '192.168.1.0/24' in str(e)

    def test_cidr_field_validate_protocol_restriction_ipv4(self):
        """Test IPv4-only field rejects IPv6."""
        field = CidrField(protocol='IPv4')
        field.name = 'subnet'

        # IPv4 should pass
        field.validate('192.168.1.0/24')

        # IPv6 should fail
        with pytest.raises(ValueError, match="Only IPv4 networks allowed"):
            field.validate('2001:db8::/32')

    def test_cidr_field_validate_protocol_restriction_ipv6(self):
        """Test IPv6-only field rejects IPv4."""
        field = CidrField(protocol='IPv6')
        field.name = 'subnet'

        # IPv6 should pass
        field.validate('2001:db8::/32')

        # IPv4 should fail
        with pytest.raises(ValueError, match="Only IPv6 networks allowed"):
            field.validate('192.168.1.0/24')

    def test_cidr_field_validate_invalid_cidr(self):
        """Test validation rejects invalid CIDR notation."""
        field = CidrField()
        field.name = 'subnet'

        with pytest.raises(ValueError, match="Invalid CIDR notation"):
            field.validate('999.999.999.999/24')

        with pytest.raises(ValueError, match="Invalid CIDR notation"):
            field.validate('not a cidr')

    def test_cidr_field_validate_none(self):
        """Test validation accepts None."""
        field = CidrField()
        field.name = 'subnet'

        result = field.validate(None)
        assert result is None

    def test_cidr_field_validate_invalid_type(self):
        """Test validation rejects non-string types."""
        field = CidrField()
        field.name = 'subnet'

        with pytest.raises(ValueError, match="must be a string"):
            field.validate(12345)

    def test_cidr_field_get_db_type_postgresql(self):
        """Test database type for PostgreSQL."""
        field = CidrField()
        assert field.get_db_type('postgresql') == 'CIDR'

    def test_cidr_field_get_db_type_mysql(self):
        """Test database type for MySQL."""
        field = CidrField()
        assert field.get_db_type('mysql') == 'VARCHAR(45)'

    def test_cidr_field_get_db_type_sqlite(self):
        """Test database type for SQLite."""
        field = CidrField()
        assert field.get_db_type('sqlite') == 'VARCHAR(45)'

    def test_cidr_field_to_python(self):
        """Test conversion from database value."""
        field = CidrField()
        field.name = 'subnet'

        assert field.to_python('192.168.1.0/24') == '192.168.1.0/24'
        assert field.to_python(None) is None

    def test_cidr_field_get_db_value(self):
        """Test conversion to database value."""
        field = CidrField()
        field.name = 'subnet'

        assert field.get_db_value('192.168.1.0/24', 'postgresql') == '192.168.1.0/24'
        assert field.get_db_value(None, 'postgresql') is None

    def test_cidr_field_various_prefix_lengths(self):
        """Test CIDR accepts various valid prefix lengths."""
        field = CidrField()
        field.name = 'subnet'

        # Valid prefix lengths
        valid_networks = [
            '10.0.0.0/8',
            '172.16.0.0/12',
            '192.168.0.0/16',
            '192.168.1.0/24',
            '192.168.1.128/25',
            '2001:db8::/32',
            '2001:db8:abcd::/48',
        ]

        for network in valid_networks:
            result = field.validate(network)
            assert result == network


# =============================================================================
# Integration Tests (4 tests)
# =============================================================================


class TestPhase3Integration:
    """Integration tests for Phase 3 fields."""

    def test_all_phase3_fields_exported(self):
        """Test all Phase 3 fields are exported in __all__."""
        from src.covet.database.orm import fields

        assert hasattr(fields, 'HStoreField')
        assert hasattr(fields, 'InetField')
        assert hasattr(fields, 'CidrField')

        assert 'HStoreField' in fields.__all__
        assert 'InetField' in fields.__all__
        assert 'CidrField' in fields.__all__

    def test_phase3_field_instantiation(self):
        """Test all Phase 3 fields can be instantiated."""
        hstore = HStoreField()
        inet = InetField()
        cidr = CidrField()

        assert hstore is not None
        assert inet is not None
        assert cidr is not None

    def test_phase3_fields_with_nullable(self):
        """Test Phase 3 fields work with nullable=False."""
        hstore = HStoreField(nullable=False)
        inet = InetField(nullable=False)
        cidr = CidrField(nullable=False)

        assert hstore.nullable == False
        assert inet.nullable == False
        assert cidr.nullable == False

    def test_phase3_fields_with_default(self):
        """Test Phase 3 fields work with default values."""
        hstore = HStoreField(default={})
        inet = InetField(default='0.0.0.0')
        cidr = CidrField(default='0.0.0.0/0')

        assert hstore.default == {}
        assert inet.default == '0.0.0.0'
        assert cidr.default == '0.0.0.0/0'
