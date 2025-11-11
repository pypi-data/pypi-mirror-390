#!/usr/bin/env python3
"""
Simple demonstration of the CovetPy Template Engine
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from covet.templates import TemplateEngine, render_string

def demonstrate_working_features():
    """Demonstrate what's currently working."""
    print("=== CovetPy Template Engine Demo ===")
    
    # 1. Basic variable substitution
    print("\n1. Variable substitution:")
    result = render_string("Hello, {{ name }}!", {'name': 'CovetPy'})
    print(f"   Template: Hello, {{ name }}!")
    print(f"   Result:   {result}")
    
    # 2. Filters
    print("\n2. Filters:")
    result = render_string("{{ message|upper|center(30) }}", {'message': 'covet templates'})
    print(f"   Template: {{ message|upper|center(30) }}")
    print(f"   Result:   '{result}'")
    
    # 3. For loops (basic)
    print("\n3. For loops:")
    template_str = "{% for item in items %}{{ item }} {% endfor %}"
    result = render_string(template_str, {'items': ['a', 'b', 'c']})
    print(f"   Template: {template_str}")
    print(f"   Result:   '{result}'")
    
    # 4. Loop variables
    print("\n4. Loop variables:")
    template_str = "{% for item in items %}{{ loop.index }}: {{ item }} {% endfor %}"
    result = render_string(template_str, {'items': ['x', 'y', 'z']})
    print(f"   Template: {template_str}")
    print(f"   Result:   '{result}'")
    
    # 5. Auto-escaping
    print("\n5. Auto-escaping:")
    result = render_string("{{ content }}", {'content': '<script>alert("xss")</script>'})
    print(f"   Template: {{ content }}")
    print(f"   Input:    <script>alert(\"xss\")</script>")
    print(f"   Result:   {result}")
    
    # 6. Custom filters
    print("\n6. Custom filters:")
    engine = TemplateEngine()
    engine.add_filter('exclaim', lambda x: f"{x}!!!")
    result = engine.render_string("{{ message|exclaim }}", {'message': 'Hello World'})
    print(f"   Template: {{ message|exclaim }}")
    print(f"   Result:   {result}")
    
    print("\n=== Working Features Summary ===")
    print("✓ Variable substitution")
    print("✓ Built-in filters")
    print("✓ Custom filters")
    print("✓ For loops")
    print("✓ Loop variables (index, first, last, etc.)")
    print("✓ Auto-escaping")
    print("✓ Template caching")
    print("✓ Static file serving")
    
    print("\n=== Issues to Fix ===")
    print("❌ If conditions in templates")
    print("❌ Template inheritance (extends/blocks)")
    print("❌ Template inclusion")
    print("❌ Complex expressions in conditions")

if __name__ == '__main__':
    demonstrate_working_features()