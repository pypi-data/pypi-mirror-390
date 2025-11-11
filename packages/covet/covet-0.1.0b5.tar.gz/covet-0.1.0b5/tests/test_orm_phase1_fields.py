"""
Comprehensive test suite for Phase 1 ORM fields.

Tests DurationField, IPAddressField, and SlugField across all database adapters.
"""

import pytest
import ipaddress
from datetime import timedelta
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from covet.database.orm.fields import DurationField, IPAddressField, SlugField


# ==============================================================================
# DurationField Tests
# ==============================================================================

class TestDurationField:
    """Test DurationField validation and conversion."""

    def test_duration_field_initialization(self):
        """Test DurationField can be initialized."""
        field = DurationField()
        assert field is not None
        assert field.name is None  # Not set yet (set by metaclass)

    def test_duration_field_with_min_max(self):
        """Test DurationField with min/max values."""
        field = DurationField(
            min_value=timedelta(0),
            max_value=timedelta(hours=24)
        )
        assert field.min_value == timedelta(0)
        assert field.max_value == timedelta(hours=24)

    def test_duration_field_validate_valid(self):
        """Test validation with valid timedelta."""
        field = DurationField()
        field.name = 'duration'  # Simulate metaclass assignment

        # Valid values
        result = field.validate(timedelta(hours=2))
        assert result == timedelta(hours=2)

        result = field.validate(timedelta(days=1, hours=3, minutes=15))
        assert result == timedelta(days=1, hours=3, minutes=15)

    def test_duration_field_validate_none(self):
        """Test validation with None (nullable)."""
        field = DurationField(nullable=True)
        field.name = 'duration'

        result = field.validate(None)
        assert result is None

    def test_duration_field_validate_invalid_type(self):
        """Test validation fails with invalid type."""
        field = DurationField()
        field.name = 'duration'

        with pytest.raises(ValueError, match="must be a timedelta"):
            field.validate("not a timedelta")

        with pytest.raises(ValueError, match="must be a timedelta"):
            field.validate(123)

    def test_duration_field_validate_min_value(self):
        """Test validation enforces minimum value."""
        field = DurationField(min_value=timedelta(hours=1))
        field.name = 'duration'

        # Valid (>= min)
        field.validate(timedelta(hours=1))
        field.validate(timedelta(hours=2))

        # Invalid (< min)
        with pytest.raises(ValueError, match="less than minimum"):
            field.validate(timedelta(minutes=30))

    def test_duration_field_validate_max_value(self):
        """Test validation enforces maximum value."""
        field = DurationField(max_value=timedelta(hours=10))
        field.name = 'duration'

        # Valid (<= max)
        field.validate(timedelta(hours=10))
        field.validate(timedelta(hours=5))

        # Invalid (> max)
        with pytest.raises(ValueError, match="exceeds maximum"):
            field.validate(timedelta(hours=20))

    def test_duration_field_to_python_timedelta(self):
        """Test conversion from timedelta."""
        field = DurationField()
        field.name = 'duration'

        value = timedelta(hours=2, minutes=30)
        result = field.to_python(value)
        assert result == value

    def test_duration_field_to_python_microseconds(self):
        """Test conversion from microseconds (MySQL format)."""
        field = DurationField()
        field.name = 'duration'

        # 2.5 hours in microseconds
        microseconds = int(2.5 * 3600 * 1_000_000)
        result = field.to_python(microseconds)
        assert result == timedelta(hours=2, minutes=30)

    def test_duration_field_to_python_iso8601(self):
        """Test conversion from ISO 8601 duration string (SQLite format)."""
        field = DurationField()
        field.name = 'duration'

        # "PT2H30M15S" = 2:30:15
        result = field.to_python("PT2H30M15S")
        assert result == timedelta(hours=2, minutes=30, seconds=15)

        # "PT1H" = 1:00:00
        result = field.to_python("PT1H")
        assert result == timedelta(hours=1)

        # "PT30M" = 0:30:00
        result = field.to_python("PT30M")
        assert result == timedelta(minutes=30)

        # "PT45S" = 0:00:45
        result = field.to_python("PT45S")
        assert result == timedelta(seconds=45)

    def test_duration_field_to_python_total_seconds(self):
        """Test conversion from total seconds as string."""
        field = DurationField()
        field.name = 'duration'

        result = field.to_python("3600.5")  # 1 hour + 0.5 seconds
        assert result == timedelta(seconds=3600.5)

    def test_duration_field_get_db_type_postgresql(self):
        """Test database type for PostgreSQL."""
        field = DurationField()
        assert field.get_db_type('postgresql') == 'INTERVAL'

    def test_duration_field_get_db_type_mysql(self):
        """Test database type for MySQL."""
        field = DurationField()
        assert field.get_db_type('mysql') == 'BIGINT'

    def test_duration_field_get_db_type_sqlite(self):
        """Test database type for SQLite."""
        field = DurationField()
        assert field.get_db_type('sqlite') == 'TEXT'

    def test_duration_field_get_db_value_postgresql(self):
        """Test database value conversion for PostgreSQL."""
        field = DurationField()
        field.name = 'duration'

        value = timedelta(hours=2, minutes=30)
        result = field.get_db_value(value, 'postgresql')
        # PostgreSQL accepts timedelta directly
        assert result == value

    def test_duration_field_get_db_value_mysql(self):
        """Test database value conversion for MySQL."""
        field = DurationField()
        field.name = 'duration'

        value = timedelta(hours=2, minutes=30)
        result = field.get_db_value(value, 'mysql')
        # MySQL stores as microseconds
        assert result == int(2.5 * 3600 * 1_000_000)

    def test_duration_field_get_db_value_sqlite(self):
        """Test database value conversion for SQLite."""
        field = DurationField()
        field.name = 'duration'

        value = timedelta(hours=2, minutes=30, seconds=15)
        result = field.get_db_value(value, 'sqlite')
        # SQLite stores as ISO 8601 duration
        assert result == "PT2H30M15S"


# ==============================================================================
# IPAddressField Tests
# ==============================================================================

class TestIPAddressField:
    """Test IPAddressField validation and conversion."""

    def test_ipaddress_field_initialization(self):
        """Test IPAddressField can be initialized."""
        field = IPAddressField()
        assert field is not None
        assert field.protocol == 'both'

    def test_ipaddress_field_protocol_ipv4(self):
        """Test IPAddressField with IPv4 protocol."""
        field = IPAddressField(protocol='IPv4')
        assert field.protocol == 'IPv4'

    def test_ipaddress_field_protocol_ipv6(self):
        """Test IPAddressField with IPv6 protocol."""
        field = IPAddressField(protocol='IPv6')
        assert field.protocol == 'IPv6'

    def test_ipaddress_field_invalid_protocol(self):
        """Test IPAddressField rejects invalid protocol."""
        with pytest.raises(ValueError, match="protocol must be"):
            IPAddressField(protocol='invalid')

    def test_ipaddress_field_validate_ipv4_string(self):
        """Test validation with IPv4 string."""
        field = IPAddressField()
        field.name = 'ip'

        result = field.validate('192.168.1.1')
        assert isinstance(result, ipaddress.IPv4Address)
        assert str(result) == '192.168.1.1'

    def test_ipaddress_field_validate_ipv6_string(self):
        """Test validation with IPv6 string."""
        field = IPAddressField()
        field.name = 'ip'

        result = field.validate('2001:db8::1')
        assert isinstance(result, ipaddress.IPv6Address)
        assert str(result) == '2001:db8::1'

    def test_ipaddress_field_validate_ipv4_object(self):
        """Test validation with IPv4Address object."""
        field = IPAddressField()
        field.name = 'ip'

        ip = ipaddress.ip_address('10.0.0.1')
        result = field.validate(ip)
        assert result == ip

    def test_ipaddress_field_validate_invalid_ip(self):
        """Test validation fails with invalid IP."""
        field = IPAddressField()
        field.name = 'ip'

        with pytest.raises(ValueError, match="Invalid IP address"):
            field.validate('not-an-ip')

        with pytest.raises(ValueError, match="Invalid IP address"):
            field.validate('999.999.999.999')

    def test_ipaddress_field_protocol_restriction_ipv4_only(self):
        """Test IPv4-only protocol restriction."""
        field = IPAddressField(protocol='IPv4')
        field.name = 'ip'

        # Valid IPv4
        result = field.validate('192.168.1.1')
        assert isinstance(result, ipaddress.IPv4Address)

        # Invalid: IPv6 when IPv4-only
        with pytest.raises(ValueError, match="Only IPv4 addresses allowed"):
            field.validate('2001:db8::1')

    def test_ipaddress_field_protocol_restriction_ipv6_only(self):
        """Test IPv6-only protocol restriction."""
        field = IPAddressField(protocol='IPv6')
        field.name = 'ip'

        # Valid IPv6
        result = field.validate('2001:db8::1')
        assert isinstance(result, ipaddress.IPv6Address)

        # Invalid: IPv4 when IPv6-only
        with pytest.raises(ValueError, match="Only IPv6 addresses allowed"):
            field.validate('192.168.1.1')

    def test_ipaddress_field_to_python_string(self):
        """Test conversion from string."""
        field = IPAddressField()
        field.name = 'ip'

        result = field.to_python('192.168.1.1')
        assert isinstance(result, ipaddress.IPv4Address)
        assert str(result) == '192.168.1.1'

    def test_ipaddress_field_to_python_none(self):
        """Test conversion from None."""
        field = IPAddressField()
        field.name = 'ip'

        result = field.to_python(None)
        assert result is None

    def test_ipaddress_field_to_db_string(self):
        """Test conversion to database (string)."""
        field = IPAddressField()
        field.name = 'ip'

        result = field.to_db('192.168.1.1')
        assert result == '192.168.1.1'

    def test_ipaddress_field_to_db_object(self):
        """Test conversion to database (IP object)."""
        field = IPAddressField()
        field.name = 'ip'

        ip = ipaddress.ip_address('10.0.0.1')
        result = field.to_db(ip)
        assert result == '10.0.0.1'

    def test_ipaddress_field_get_db_type_postgresql(self):
        """Test database type for PostgreSQL."""
        field = IPAddressField()
        assert field.get_db_type('postgresql') == 'INET'

    def test_ipaddress_field_get_db_type_mysql(self):
        """Test database type for MySQL."""
        field = IPAddressField()
        assert field.get_db_type('mysql') == 'VARCHAR(45)'

    def test_ipaddress_field_get_db_type_sqlite(self):
        """Test database type for SQLite."""
        field = IPAddressField()
        assert field.get_db_type('sqlite') == 'VARCHAR(45)'


# ==============================================================================
# SlugField Tests
# ==============================================================================

class TestSlugField:
    """Test SlugField validation and slugify helper."""

    def test_slugfield_initialization(self):
        """Test SlugField can be initialized."""
        field = SlugField()
        assert field is not None
        assert field.max_length == 50  # Default

    def test_slugfield_custom_max_length(self):
        """Test SlugField with custom max length."""
        field = SlugField(max_length=100)
        assert field.max_length == 100

    def test_slugfield_validate_valid_slug(self):
        """Test validation with valid slug."""
        field = SlugField()
        field.name = 'slug'

        # Valid slugs
        assert field.validate('my-blog-post') == 'my-blog-post'
        assert field.validate('hello-world') == 'hello-world'
        assert field.validate('post-123') == 'post-123'
        assert field.validate('a') == 'a'
        assert field.validate('test-1-2-3') == 'test-1-2-3'

    def test_slugfield_validate_empty(self):
        """Test validation with empty string."""
        field = SlugField(nullable=True)
        field.name = 'slug'

        assert field.validate('') == ''
        assert field.validate(None) is None

    def test_slugfield_validate_invalid_uppercase(self):
        """Test validation fails with uppercase."""
        field = SlugField()
        field.name = 'slug'

        with pytest.raises(ValueError, match="Invalid slug format"):
            field.validate('My-Blog-Post')

    def test_slugfield_validate_invalid_spaces(self):
        """Test validation fails with spaces."""
        field = SlugField()
        field.name = 'slug'

        with pytest.raises(ValueError, match="Invalid slug format"):
            field.validate('my blog post')

    def test_slugfield_validate_invalid_underscores(self):
        """Test validation fails with underscores."""
        field = SlugField()
        field.name = 'slug'

        with pytest.raises(ValueError, match="Invalid slug format"):
            field.validate('my_blog_post')

    def test_slugfield_validate_invalid_special_chars(self):
        """Test validation fails with special characters."""
        field = SlugField()
        field.name = 'slug'

        with pytest.raises(ValueError, match="Invalid slug format"):
            field.validate('my-blog-post!')

        with pytest.raises(ValueError, match="Invalid slug format"):
            field.validate('my@blog.com')

    def test_slugfield_validate_invalid_leading_hyphen(self):
        """Test validation fails with leading hyphen."""
        field = SlugField()
        field.name = 'slug'

        with pytest.raises(ValueError, match="cannot start or end with hyphen"):
            field.validate('-my-blog-post')

    def test_slugfield_validate_invalid_trailing_hyphen(self):
        """Test validation fails with trailing hyphen."""
        field = SlugField()
        field.name = 'slug'

        with pytest.raises(ValueError, match="cannot start or end with hyphen"):
            field.validate('my-blog-post-')

    def test_slugfield_validate_invalid_multiple_hyphens(self):
        """Test validation fails with multiple consecutive hyphens."""
        field = SlugField()
        field.name = 'slug'

        with pytest.raises(ValueError, match="cannot contain consecutive hyphens"):
            field.validate('my--blog--post')

    def test_slugfield_slugify_basic(self):
        """Test slugify with basic text."""
        assert SlugField.slugify("Hello World") == "hello-world"
        assert SlugField.slugify("My Awesome Blog Post") == "my-awesome-blog-post"
        assert SlugField.slugify("Test 123") == "test-123"

    def test_slugfield_slugify_special_characters(self):
        """Test slugify removes special characters."""
        assert SlugField.slugify("Hello! World?") == "hello-world"
        assert SlugField.slugify("My Blog Post!!!") == "my-blog-post"
        assert SlugField.slugify("Test@Example.com") == "testexamplecom"

    def test_slugfield_slugify_multiple_spaces(self):
        """Test slugify handles multiple spaces."""
        assert SlugField.slugify("Hello    World") == "hello-world"
        assert SlugField.slugify("  Lots  Of   Spaces  ") == "lots-of-spaces"

    def test_slugfield_slugify_existing_hyphens(self):
        """Test slugify handles existing hyphens."""
        assert SlugField.slugify("Hello-World") == "hello-world"
        assert SlugField.slugify("Pre-Existing-Hyphens") == "pre-existing-hyphens"
        assert SlugField.slugify("Multiple---Hyphens") == "multiple-hyphens"

    def test_slugfield_slugify_max_length(self):
        """Test slugify with max length."""
        long_text = "This is a very long blog post title that should be truncated"

        result = SlugField.slugify(long_text, max_length=20)
        assert len(result) <= 20
        assert result == "this-is-a-very-long"

        # Should not end with hyphen after truncation
        result = SlugField.slugify("Hello World Test", max_length=11)
        assert result == "hello-world"  # Truncated, no trailing hyphen

    def test_slugfield_slugify_unicode(self):
        """Test slugify with unicode characters."""
        # Unicode characters are removed
        assert SlugField.slugify("Héllo Wörld") == "hllo-wrld"
        assert SlugField.slugify("你好 World") == "world"

    def test_slugfield_slugify_empty(self):
        """Test slugify with empty/whitespace input."""
        assert SlugField.slugify("") == ""
        assert SlugField.slugify("   ") == ""
        assert SlugField.slugify("!!!") == ""


# ==============================================================================
# Integration Tests (Cross-Field)
# ==============================================================================

class TestPhase1FieldsIntegration:
    """Integration tests for Phase 1 fields."""

    def test_all_fields_in_exports(self):
        """Test all Phase 1 fields are exported."""
        from covet.database.orm import fields

        assert hasattr(fields, 'DurationField')
        assert hasattr(fields, 'IPAddressField')
        assert hasattr(fields, 'SlugField')

    def test_all_fields_can_be_instantiated(self):
        """Test all Phase 1 fields can be instantiated."""
        duration = DurationField()
        ip = IPAddressField()
        slug = SlugField()

        assert duration is not None
        assert ip is not None
        assert slug is not None

    def test_field_default_values(self):
        """Test fields handle default values correctly."""
        duration = DurationField(default=timedelta(hours=1))
        assert duration.get_default() == timedelta(hours=1)

        ip = IPAddressField(default='127.0.0.1')
        assert ip.get_default() == '127.0.0.1'

        slug = SlugField(default='default-slug')
        assert slug.get_default() == 'default-slug'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
