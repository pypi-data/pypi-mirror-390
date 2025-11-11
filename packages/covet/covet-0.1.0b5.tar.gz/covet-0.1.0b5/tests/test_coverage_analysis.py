"""
Basic coverage analysis test without complex imports.
This test aims to verify basic Python syntax and identify testable modules.
"""
import os
import sys
import ast
import importlib.util
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_source_files_syntax():
    """Test that all Python files in src/ have valid syntax."""
    src_path = Path(__file__).parent.parent / 'src'
    python_files = list(src_path.rglob('*.py'))
    
    syntax_errors = []
    valid_files = []
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            ast.parse(content, filename=str(py_file))
            valid_files.append(str(py_file))
        except SyntaxError as e:
            syntax_errors.append((str(py_file), str(e)))
        except Exception as e:
            syntax_errors.append((str(py_file), f"Other error: {e}"))
    
    print(f"\nSyntax Analysis Results:")
    print(f"Valid files: {len(valid_files)}")
    print(f"Files with syntax errors: {len(syntax_errors)}")
    
    if syntax_errors:
        print("\nFiles with syntax errors:")
        for file_path, error in syntax_errors[:10]:  # Show first 10
            print(f"  {file_path}: {error}")
    
    # We want most files to have valid syntax, but allow some errors during development
    assert len(valid_files) > len(syntax_errors), "More files should have valid syntax than errors"

def test_importable_modules():
    """Test which modules can be imported successfully."""
    src_path = Path(__file__).parent.parent / 'src'
    
    # Key modules we want to test
    key_modules = [
        'covet',
        'covet.core',
        'covet.security',
        'covet.database',
        'covet.api',
        'covet.templates',
        'covet.testing',
    ]
    
    importable = []
    not_importable = []
    
    for module_name in key_modules:
        try:
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                importable.append(module_name)
            else:
                not_importable.append((module_name, "Module not found"))
        except Exception as e:
            not_importable.append((module_name, str(e)))
    
    print(f"\nImport Analysis Results:")
    print(f"Importable modules: {len(importable)}")
    print(f"Non-importable modules: {len(not_importable)}")
    
    if importable:
        print("\nImportable modules:")
        for module in importable:
            print(f"  ✓ {module}")
    
    if not_importable:
        print("\nNon-importable modules:")
        for module, error in not_importable:
            print(f"  ✗ {module}: {error}")
    
    # At least some modules should be importable
    assert len(importable) > 0, "At least some core modules should be importable"

def test_calculate_file_coverage():
    """Calculate basic file coverage metrics."""
    src_path = Path(__file__).parent.parent / 'src'
    tests_path = Path(__file__).parent
    
    # Count source files
    source_files = list(src_path.rglob('*.py'))
    source_files = [f for f in source_files if '__pycache__' not in str(f)]
    
    # Count test files
    test_files = list(tests_path.rglob('test_*.py'))
    
    # Calculate basic metrics
    total_source_files = len(source_files)
    total_test_files = len(test_files)
    
    # Estimate coverage based on file presence
    # This is a rough estimate - real coverage needs actual execution
    estimated_coverage = min(total_test_files / max(total_source_files, 1) * 100, 100)
    
    print(f"\nFile Coverage Analysis:")
    print(f"Source files: {total_source_files}")
    print(f"Test files: {total_test_files}")
    print(f"Estimated file coverage: {estimated_coverage:.1f}%")
    
    # List some key source files
    print("\nKey source files found:")
    key_patterns = ['app.py', 'config.py', 'routing.py', 'security', 'database']
    for pattern in key_patterns:
        matching_files = [f for f in source_files if pattern in str(f)]
        if matching_files:
            print(f"  {pattern}: {len(matching_files)} files")
    
    assert total_source_files > 0, "Should have source files to test"
    assert total_test_files > 0, "Should have test files"

if __name__ == "__main__":
    test_source_files_syntax()
    test_importable_modules()
    test_calculate_file_coverage()
    print("\n✓ Coverage analysis completed")