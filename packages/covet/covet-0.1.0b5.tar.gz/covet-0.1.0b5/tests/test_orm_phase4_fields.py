"""
Comprehensive test suite for Phase 4 ORM Fields (Advanced PostgreSQL & Path Fields)

Tests:
- FilePathField (file system path validation)
- TSVectorField (PostgreSQL full-text search)
- GeometryField, PointField, PolygonField, LineStringField (PostGIS)

Coverage:
- Field instantiation and configuration
- Type validation
- Database type mapping
- PostgreSQL-specific features
- Security (path traversal protection)
- Edge cases and error handling
"""

import json
import pytest
import tempfile
import os
from pathlib import Path

from src.covet.database.orm.fields import (
    FilePathField,
    TSVectorField,
    GeometryField,
    PointField,
    PolygonField,
    LineStringField,
)


# =============================================================================
# FilePathField Tests (22 tests)
# =============================================================================


class TestFilePathField:
    """Test FilePathField (file system path selection)."""

    def test_filepath_field_instantiation(self):
        """Test basic FilePath field instantiation."""
        field = FilePathField()
        assert isinstance(field, FilePathField)
        assert field.base_path is None
        assert field.match is None
        assert field.recursive == False
        assert field.allow_files == True
        assert field.allow_folders == False

    def test_filepath_field_instantiation_with_path(self):
        """Test FilePath field with base path."""
        field = FilePathField(path='/tmp')
        assert field.base_path == Path('/tmp')

    def test_filepath_field_instantiation_with_options(self):
        """Test FilePath field with all options."""
        field = FilePathField(
            path='/tmp',
            match=r'.*\.txt$',
            recursive=True,
            allow_files=True,
            allow_folders=True
        )
        assert field.base_path == Path('/tmp')
        assert field.match == r'.*\.txt$'
        assert field.recursive == True
        assert field.allow_files == True
        assert field.allow_folders == True
        assert field.match_re is not None

    def test_filepath_field_invalid_regex(self):
        """Test FilePath field rejects invalid regex."""
        with pytest.raises(ValueError, match="Invalid regex pattern"):
            FilePathField(match='[invalid(')

    def test_filepath_field_validate_no_base_path(self):
        """Test validation without base path (allows any path)."""
        field = FilePathField()
        field.name = 'file_path'

        # Without base_path, validation just passes through
        result = field.validate('/any/path/here.txt')
        assert result == '/any/path/here.txt'

    def test_filepath_field_validate_with_temp_file(self):
        """Test validation with actual file."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp:
            tmp_path = tmp.name

        try:
            tmp_dir = os.path.dirname(tmp_path)
            field = FilePathField(path=tmp_dir, allow_files=True)
            field.name = 'file_path'

            # Should validate successfully
            result = field.validate(tmp_path)
            assert result == tmp_path
        finally:
            os.unlink(tmp_path)

    def test_filepath_field_validate_nonexistent_file(self):
        """Test validation fails for nonexistent file."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            field = FilePathField(path=tmp_dir)
            field.name = 'file_path'

            nonexistent = os.path.join(tmp_dir, 'nonexistent.txt')
            with pytest.raises(ValueError, match="Path does not exist"):
                field.validate(nonexistent)

    def test_filepath_field_validate_path_traversal(self):
        """Test validation prevents path traversal."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            field = FilePathField(path=tmp_dir)
            field.name = 'file_path'

            # Try to access parent directory
            parent_path = os.path.join(tmp_dir, '..', 'etc', 'passwd')
            with pytest.raises(ValueError, match="Path must be within"):
                field.validate(parent_path)

    def test_filepath_field_validate_folder_when_files_only(self):
        """Test validation rejects folders when allow_folders=False."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create subdirectory
            subdir = os.path.join(tmp_dir, 'subdir')
            os.mkdir(subdir)

            field = FilePathField(path=tmp_dir, allow_files=True, allow_folders=False)
            field.name = 'file_path'

            with pytest.raises(ValueError, match="Folders not allowed"):
                field.validate(subdir)

    def test_filepath_field_validate_file_when_folders_only(self):
        """Test validation rejects files when allow_files=False."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        try:
            tmp_dir = os.path.dirname(tmp_path)
            field = FilePathField(path=tmp_dir, allow_files=False, allow_folders=True)
            field.name = 'file_path'

            with pytest.raises(ValueError, match="Files not allowed"):
                field.validate(tmp_path)
        finally:
            os.unlink(tmp_path)

    def test_filepath_field_validate_recursive_false(self):
        """Test validation enforces recursive=False."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create subdirectory with file
            subdir = os.path.join(tmp_dir, 'subdir')
            os.mkdir(subdir)
            subfile = os.path.join(subdir, 'file.txt')
            Path(subfile).touch()

            field = FilePathField(path=tmp_dir, recursive=False)
            field.name = 'file_path'

            with pytest.raises(ValueError, match="recursive=False"):
                field.validate(subfile)

    def test_filepath_field_validate_recursive_true(self):
        """Test validation allows subdirectories when recursive=True."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create subdirectory with file
            subdir = os.path.join(tmp_dir, 'subdir')
            os.mkdir(subdir)
            subfile = os.path.join(subdir, 'file.txt')
            Path(subfile).touch()

            field = FilePathField(path=tmp_dir, recursive=True)
            field.name = 'file_path'

            # Should validate successfully
            result = field.validate(subfile)
            assert result == subfile

    def test_filepath_field_validate_regex_match(self):
        """Test validation enforces regex pattern."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp:
            tmp_path = tmp.name

        try:
            tmp_dir = os.path.dirname(tmp_path)
            field = FilePathField(path=tmp_dir, match=r'.*\.txt$')
            field.name = 'file_path'

            # Should match .txt file
            result = field.validate(tmp_path)
            assert result == tmp_path
        finally:
            os.unlink(tmp_path)

    def test_filepath_field_validate_regex_no_match(self):
        """Test validation rejects files not matching regex."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp_path = tmp.name

        try:
            tmp_dir = os.path.dirname(tmp_path)
            field = FilePathField(path=tmp_dir, match=r'.*\.txt$')
            field.name = 'file_path'

            with pytest.raises(ValueError, match="does not match pattern"):
                field.validate(tmp_path)
        finally:
            os.unlink(tmp_path)

    def test_filepath_field_get_db_type(self):
        """Test database type (inherited from CharField)."""
        field = FilePathField(max_length=500)
        assert 'VARCHAR' in field.get_db_type('postgresql') or 'CHAR' in field.get_db_type('postgresql')


# =============================================================================
# TSVectorField Tests (12 tests)
# =============================================================================


class TestTSVectorField:
    """Test TSVectorField (PostgreSQL full-text search)."""

    def test_tsvector_field_instantiation(self):
        """Test basic TSVector field instantiation."""
        field = TSVectorField()
        assert isinstance(field, TSVectorField)
        assert field.config == 'english'

    def test_tsvector_field_instantiation_with_config(self):
        """Test TSVector field with custom config."""
        field = TSVectorField(config='french')
        assert field.config == 'french'

    def test_tsvector_field_get_db_type_postgresql(self):
        """Test database type for PostgreSQL."""
        field = TSVectorField()
        assert field.get_db_type('postgresql') == 'TSVECTOR'

    def test_tsvector_field_get_db_type_non_postgresql(self):
        """Test database type fails for non-PostgreSQL."""
        field = TSVectorField()

        with pytest.raises(ValueError, match="only supported on PostgreSQL"):
            field.get_db_type('mysql')

        with pytest.raises(ValueError, match="only supported on PostgreSQL"):
            field.get_db_type('sqlite')

    def test_tsvector_field_validate_string(self):
        """Test validation accepts string."""
        field = TSVectorField()
        field.name = 'search_vector'

        result = field.validate("'python':1 'database':2")
        assert result == "'python':1 'database':2"

    def test_tsvector_field_validate_none(self):
        """Test validation accepts None."""
        field = TSVectorField()
        field.name = 'search_vector'

        result = field.validate(None)
        assert result is None

    def test_tsvector_field_validate_invalid_type(self):
        """Test validation rejects non-string types."""
        field = TSVectorField()
        field.name = 'search_vector'

        with pytest.raises(ValueError, match="must be a string"):
            field.validate(12345)

    def test_tsvector_field_to_python(self):
        """Test conversion from database value."""
        field = TSVectorField()
        field.name = 'search_vector'

        result = field.to_python("'python':1")
        assert result == "'python':1"

        assert field.to_python(None) is None

    def test_tsvector_field_to_python_invalid_type(self):
        """Test conversion fails for invalid type from database."""
        field = TSVectorField()
        field.name = 'search_vector'

        with pytest.raises(ValueError, match="Expected string from database"):
            field.to_python(12345)

    def test_tsvector_field_get_db_value_postgresql(self):
        """Test database value for PostgreSQL."""
        field = TSVectorField()
        field.name = 'search_vector'

        result = field.get_db_value("'python':1", 'postgresql')
        assert result == "'python':1"

    def test_tsvector_field_get_db_value_non_postgresql(self):
        """Test database value fails for non-PostgreSQL."""
        field = TSVectorField()
        field.name = 'search_vector'

        with pytest.raises(ValueError, match="only supported on PostgreSQL"):
            field.get_db_value("'python':1", 'mysql')

    def test_tsvector_field_get_db_value_none(self):
        """Test database value for None."""
        field = TSVectorField()
        field.name = 'search_vector'

        result = field.get_db_value(None, 'postgresql')
        assert result is None


# =============================================================================
# GeometryField Tests (10 tests)
# =============================================================================


class TestGeometryField:
    """Test GeometryField (PostGIS base class)."""

    def test_geometry_field_instantiation(self):
        """Test basic Geometry field instantiation."""
        field = GeometryField()
        assert isinstance(field, GeometryField)
        assert field.srid == 4326  # Default WGS84

    def test_geometry_field_instantiation_with_srid(self):
        """Test Geometry field with custom SRID."""
        field = GeometryField(srid=3857)
        assert field.srid == 3857

    def test_geometry_field_get_db_type_postgresql(self):
        """Test database type for PostgreSQL."""
        field = GeometryField()
        assert field.get_db_type('postgresql') == 'GEOMETRY(GEOMETRY, 4326)'

    def test_geometry_field_get_db_type_non_postgresql(self):
        """Test database type fails for non-PostgreSQL."""
        field = GeometryField()

        with pytest.raises(ValueError, match="requires PostgreSQL with PostGIS"):
            field.get_db_type('mysql')

    def test_geometry_field_validate_wkt_string(self):
        """Test validation accepts WKT string."""
        field = GeometryField()
        field.name = 'geom'

        result = field.validate("POINT(0 0)")
        assert result == "POINT(0 0)"

    def test_geometry_field_validate_tuple(self):
        """Test validation accepts coordinate tuple."""
        field = GeometryField()
        field.name = 'geom'

        result = field.validate((0, 0))
        assert result == (0, 0)

    def test_geometry_field_validate_list(self):
        """Test validation accepts coordinate list."""
        field = GeometryField()
        field.name = 'geom'

        result = field.validate([0, 0])
        assert result == [0, 0]

    def test_geometry_field_validate_invalid_type(self):
        """Test validation rejects invalid types."""
        field = GeometryField()
        field.name = 'geom'

        with pytest.raises(ValueError, match="must be WKT string, tuple, or list"):
            field.validate(12345)

    def test_geometry_field_to_python_wkt(self):
        """Test conversion from WKT string."""
        field = GeometryField()
        field.name = 'geom'

        result = field.to_python("POINT(0 0)")
        assert result == "POINT(0 0)"

    def test_geometry_field_to_python_wkb(self):
        """Test conversion from WKB bytes."""
        field = GeometryField()
        field.name = 'geom'

        # WKB format (binary)
        wkb_data = b'\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        result = field.to_python(wkb_data)
        assert result == wkb_data


# =============================================================================
# PointField Tests (8 tests)
# =============================================================================


class TestPointField:
    """Test PointField (PostGIS POINT)."""

    def test_point_field_instantiation(self):
        """Test basic Point field instantiation."""
        field = PointField()
        assert isinstance(field, PointField)
        assert field.geometry_type == "POINT"

    def test_point_field_get_db_type(self):
        """Test database type."""
        field = PointField(srid=4326)
        assert field.get_db_type('postgresql') == 'GEOMETRY(POINT, 4326)'

    def test_point_field_coordinates_to_wkt_2d(self):
        """Test conversion from 2D coordinates to WKT."""
        field = PointField()
        field.name = 'location'

        result = field._coordinates_to_wkt((-122.4194, 37.7749))
        assert result == "POINT(-122.4194 37.7749)"

    def test_point_field_coordinates_to_wkt_3d(self):
        """Test conversion from 3D coordinates to WKT."""
        field = PointField()
        field.name = 'location'

        result = field._coordinates_to_wkt((-122.4194, 37.7749, 10.5))
        assert result == "POINT(-122.4194 37.7749 10.5)"

    def test_point_field_coordinates_to_wkt_invalid_length(self):
        """Test conversion fails for invalid coordinate count."""
        field = PointField()
        field.name = 'location'

        with pytest.raises(ValueError, match="must have 2 or 3 coordinates"):
            field._coordinates_to_wkt((1,))

        with pytest.raises(ValueError, match="must have 2 or 3 coordinates"):
            field._coordinates_to_wkt((1, 2, 3, 4))

    def test_point_field_get_db_value_wkt(self):
        """Test database value for WKT string."""
        field = PointField()
        field.name = 'location'

        result = field.get_db_value("POINT(0 0)", 'postgresql')
        assert result == "POINT(0 0)"

    def test_point_field_get_db_value_tuple(self):
        """Test database value for coordinate tuple."""
        field = PointField()
        field.name = 'location'

        result = field.get_db_value((0, 0), 'postgresql')
        assert result == "POINT(0 0)"

    def test_point_field_get_db_value_non_postgresql(self):
        """Test database value fails for non-PostgreSQL."""
        field = PointField()
        field.name = 'location'

        with pytest.raises(ValueError, match="requires PostgreSQL with PostGIS"):
            field.get_db_value("POINT(0 0)", 'mysql')


# =============================================================================
# PolygonField Tests (6 tests)
# =============================================================================


class TestPolygonField:
    """Test PolygonField (PostGIS POLYGON)."""

    def test_polygon_field_instantiation(self):
        """Test basic Polygon field instantiation."""
        field = PolygonField()
        assert isinstance(field, PolygonField)
        assert field.geometry_type == "POLYGON"

    def test_polygon_field_get_db_type(self):
        """Test database type."""
        field = PolygonField(srid=4326)
        assert field.get_db_type('postgresql') == 'GEOMETRY(POLYGON, 4326)'

    def test_polygon_field_coordinates_to_wkt(self):
        """Test conversion from coordinates to WKT."""
        field = PolygonField()
        field.name = 'boundary'

        coords = [[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]]
        result = field._coordinates_to_wkt(coords)
        assert "POLYGON" in result
        assert "0 0" in result

    def test_polygon_field_get_db_value_wkt(self):
        """Test database value for WKT string."""
        field = PolygonField()
        field.name = 'boundary'

        wkt = "POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))"
        result = field.get_db_value(wkt, 'postgresql')
        assert result == wkt

    def test_polygon_field_get_db_value_coordinates(self):
        """Test database value for coordinates."""
        field = PolygonField()
        field.name = 'boundary'

        coords = [[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]]
        result = field.get_db_value(coords, 'postgresql')
        assert "POLYGON" in result

    def test_polygon_field_coordinates_to_wkt_invalid(self):
        """Test conversion fails for invalid data."""
        field = PolygonField()
        field.name = 'boundary'

        with pytest.raises(ValueError, match="Cannot convert"):
            field._coordinates_to_wkt("invalid")


# =============================================================================
# LineStringField Tests (6 tests)
# =============================================================================


class TestLineStringField:
    """Test LineStringField (PostGIS LINESTRING)."""

    def test_linestring_field_instantiation(self):
        """Test basic LineString field instantiation."""
        field = LineStringField()
        assert isinstance(field, LineStringField)
        assert field.geometry_type == "LINESTRING"

    def test_linestring_field_get_db_type(self):
        """Test database type."""
        field = LineStringField(srid=4326)
        assert field.get_db_type('postgresql') == 'GEOMETRY(LINESTRING, 4326)'

    def test_linestring_field_coordinates_to_wkt(self):
        """Test conversion from coordinates to WKT."""
        field = LineStringField()
        field.name = 'path'

        coords = [(0, 0), (10, 10), (20, 20)]
        result = field._coordinates_to_wkt(coords)
        assert "LINESTRING" in result
        assert "0 0" in result

    def test_linestring_field_get_db_value_wkt(self):
        """Test database value for WKT string."""
        field = LineStringField()
        field.name = 'path'

        wkt = "LINESTRING(0 0, 10 10, 20 20)"
        result = field.get_db_value(wkt, 'postgresql')
        assert result == wkt

    def test_linestring_field_get_db_value_coordinates(self):
        """Test database value for coordinates."""
        field = LineStringField()
        field.name = 'path'

        coords = [(0, 0), (10, 10), (20, 20)]
        result = field.get_db_value(coords, 'postgresql')
        assert "LINESTRING" in result

    def test_linestring_field_coordinates_to_wkt_invalid(self):
        """Test conversion fails for invalid data."""
        field = LineStringField()
        field.name = 'path'

        with pytest.raises(ValueError, match="Cannot convert"):
            field._coordinates_to_wkt("invalid")


# =============================================================================
# Integration Tests (4 tests)
# =============================================================================


class TestPhase4Integration:
    """Integration tests for Phase 4 fields."""

    def test_all_phase4_fields_exported(self):
        """Test all Phase 4 fields are exported in __all__."""
        from src.covet.database.orm import fields

        assert hasattr(fields, 'FilePathField')
        assert hasattr(fields, 'TSVectorField')
        assert hasattr(fields, 'GeometryField')
        assert hasattr(fields, 'PointField')
        assert hasattr(fields, 'PolygonField')
        assert hasattr(fields, 'LineStringField')

        assert 'FilePathField' in fields.__all__
        assert 'TSVectorField' in fields.__all__
        assert 'GeometryField' in fields.__all__
        assert 'PointField' in fields.__all__
        assert 'PolygonField' in fields.__all__
        assert 'LineStringField' in fields.__all__

    def test_phase4_field_instantiation(self):
        """Test all Phase 4 fields can be instantiated."""
        filepath = FilePathField()
        tsvector = TSVectorField()
        geometry = GeometryField()
        point = PointField()
        polygon = PolygonField()
        linestring = LineStringField()

        assert filepath is not None
        assert tsvector is not None
        assert geometry is not None
        assert point is not None
        assert polygon is not None
        assert linestring is not None

    def test_postgresql_only_fields_raise_on_other_dbs(self):
        """Test PostgreSQL-only fields reject other databases."""
        tsvector = TSVectorField()
        point = PointField()

        # TSVectorField
        with pytest.raises(ValueError):
            tsvector.get_db_type('mysql')

        # GeometryField
        with pytest.raises(ValueError):
            point.get_db_type('sqlite')

    def test_filepath_field_inherits_charfield(self):
        """Test FilePathField properly inherits from CharField."""
        from src.covet.database.orm.fields import CharField

        field = FilePathField(max_length=500)
        assert isinstance(field, CharField)
        assert field.max_length == 500
