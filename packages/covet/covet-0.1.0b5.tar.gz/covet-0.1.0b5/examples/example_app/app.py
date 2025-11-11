"""
Example Blog API built with CovetPy
Tests framework's actual capabilities
"""
import sys
sys.path.insert(0, '/Users/vipin/Downloads/NeutrinoPy/src')

try:
    from covet.core import Covet, CovetApplication
    print("✅ Core Application imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Application: {e}")
    sys.exit(1)

# Try to create application
try:
    app = CovetApplication()
    print("✅ Application instance created successfully")
except Exception as e:
    print(f"❌ Failed to create Application: {e}")
    sys.exit(1)

# Test if we can run it
if __name__ == "__main__":
    try:
        print("✅ Attempting to start application...")
        # Don't actually start, just verify it's callable
        print(f"✅ Application is callable: {callable(app)}")
    except Exception as e:
        print(f"❌ Application not working: {e}")
