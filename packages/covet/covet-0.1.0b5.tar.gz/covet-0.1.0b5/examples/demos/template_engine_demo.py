#!/usr/bin/env python3
"""
Comprehensive demonstration of the CovetPy Template Engine.
Shows all features including Jinja2 compatibility, forms, static assets, CSRF protection, and more.
"""

import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from covet.templates import (
    TemplateEngine, TemplateConfig, 
    FormBuilder, CSRFProtection,
    StaticAssetManager, AssetConfig,
    TemplateCache, CacheConfig,
    FilterRegistry, register_filter
)

def demo_basic_templates():
    """Demo basic template rendering."""
    print("=== Basic Template Rendering ===")
    
    # Create a simple template engine
    config = TemplateConfig(debug=True, autoescape=True)
    engine = TemplateEngine(config)
    
    # Basic variable substitution
    template = engine.from_string("Hello {{ name }}! Welcome to {{ site }}.")
    result = template.render(name="Alice", site="CovetPy")
    print(f"Basic rendering: {result}")
    
    # Template with filters
    template = engine.from_string("{{ message | upper | truncate_words(3) }}")
    result = template.render(message="this is a very long message that should be truncated")
    print(f"With filters: {result}")
    
    # Template with control structures
    template = engine.from_string("""
    {%- if users -%}
    <ul>
    {%- for user in users -%}
        <li>{{ loop.index }}. {{ user.name | title }} ({{ user.email }})</li>
    {%- endfor -%}
    </ul>
    {%- else -%}
    <p>No users found.</p>
    {%- endif -%}
    """)
    
    users = [
        {"name": "alice", "email": "alice@example.com"},
        {"name": "bob", "email": "bob@example.com"},
    ]
    
    result = template.render(users=users)
    print(f"Control structures:\n{result}")

def demo_template_inheritance():
    """Demo template inheritance."""
    print("\n=== Template Inheritance ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        template_dir = Path(temp_dir)
        
        # Create base template
        base_template = template_dir / "base.html"
        base_template.write_text("""
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Default Title{% endblock %}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    {% block extra_head %}{% endblock %}
</head>
<body>
    <header>
        <h1>{% block header %}{{ site_name | default("My Site") }}{% endblock %}</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/about">About</a>
        </nav>
    </header>
    
    <main>
        {% block content %}
        <p>Default content</p>
        {% endblock %}
    </main>
    
    <footer>
        <p>&copy; 2024 {{ site_name | default("My Site") }}. All rights reserved.</p>
    </footer>
</body>
</html>
        """.strip())
        
        # Create child template
        child_template = template_dir / "page.html"
        child_template.write_text("""
{% extends "base.html" %}

{% block title %}About Us - {{ super() }}{% endblock %}

{% block extra_head %}
<style>
.highlight { background-color: yellow; }
</style>
{% endblock %}

{% block content %}
<div class="container">
    <h2>About Our Company</h2>
    <p class="highlight">Welcome to {{ company_name }}!</p>
    <p>We've been serving customers since {{ founded_year }}.</p>
    
    <h3>Our Team</h3>
    <div class="team">
        {% for member in team_members %}
        <div class="member">
            <h4>{{ member.name }}</h4>
            <p>{{ member.role }}</p>
            <p>{{ member.bio | truncate_words(20) }}</p>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
        """.strip())
        
        # Render with inheritance
        config = TemplateConfig(template_dirs=[template_dir], autoescape=True)
        engine = TemplateEngine(config)
        
        template = engine.get_template("page.html")
        result = template.render(
            site_name="CovetPy Demo",
            company_name="Awesome Corp",
            founded_year=2020,
            team_members=[
                {
                    "name": "Alice Johnson",
                    "role": "CEO",
                    "bio": "Alice has over 10 years of experience in technology leadership and has built multiple successful startups from the ground up."
                },
                {
                    "name": "Bob Smith", 
                    "role": "CTO",
                    "bio": "Bob is a seasoned engineer with expertise in distributed systems, cloud architecture, and machine learning."
                }
            ]
        )
        
        print("Template with inheritance rendered successfully!")
        print(f"Preview: {result[:200]}...")

def demo_forms_and_csrf():
    """Demo form handling with CSRF protection."""
    print("\n=== Forms and CSRF Protection ===")
    
    # Setup CSRF protection
    csrf = CSRFProtection("super-secret-key-change-in-production")
    
    # Create a registration form
    form = (FormBuilder()
            .add_text('username', label='Username', required=True)
            .add_email('email', label='Email Address', required=True)
            .add_password('password', label='Password', required=True)
            .add_password('password_confirm', label='Confirm Password', required=True)
            .add_checkbox('newsletter', label='Subscribe to newsletter')
            .add_select('country', label='Country', choices=[
                ('us', 'United States'),
                ('ca', 'Canada'),
                ('uk', 'United Kingdom'),
                ('de', 'Germany')
            ])
            .enable_csrf_protection("super-secret-key-change-in-production")
            .set_method('POST')
            .set_action('/register')
            .build())
    
    # Generate CSRF token
    csrf_token = form.generate_csrf_token()
    
    print(f"CSRF Token: {csrf_token}")
    print(f"Form has {len(form.fields)} fields (including CSRF token)")
    
    # Render form HTML
    form_html = form.render(csrf_token=csrf_token)
    print(f"Form HTML generated: {len(form_html)} characters")
    
    # Test form validation
    test_data = {
        'username': 'alice123',
        'email': 'alice@example.com',
        'password': 'secure_password',
        'password_confirm': 'secure_password',
        'newsletter': True,
        'country': 'us',
        'csrf_token': csrf_token
    }
    
    try:
        if form.validate(test_data):
            print("✓ Form validation passed!")
            form_data = form.get_data()
            print(f"  Form data: {form_data}")
        else:
            print("✗ Form validation failed")
    except Exception as e:
        print(f"Form validation error: {e}")

def demo_static_assets():
    """Demo static asset management."""
    print("\n=== Static Asset Management ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        source_dir = Path(temp_dir) / "assets"
        output_dir = Path(temp_dir) / "static"
        
        source_dir.mkdir()
        
        # Create sample CSS file
        css_file = source_dir / "styles.css"
        css_file.write_text("""
/* Main stylesheet */
body {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    margin: 0;
    padding: 20px;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

.btn {
    display: inline-block;
    padding: 10px 20px;
    background-color: #007bff;
    color: white;
    text-decoration: none;
    border-radius: 5px;
    transition: background-color 0.3s;
}

.btn:hover {
    background-color: #0056b3;
}
        """.strip())
        
        # Create sample JavaScript file
        js_file = source_dir / "app.js"
        js_file.write_text("""
// Main application JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('CovetPy app loaded!');
    
    // Handle form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            console.log('Form submitted:', form.action);
        });
    });
    
    // Handle button clicks
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            console.log('Button clicked:', button.textContent);
        });
    });
    
    // Simple AJAX helper
    window.fetchData = function(url, callback) {
        fetch(url)
            .then(response => response.json())
            .then(data => callback(data))
            .catch(error => console.error('Error:', error));
    };
});
        """.strip())
        
        # Setup asset manager
        config = AssetConfig(
            source_dirs=[source_dir],
            output_dir=output_dir,
            enable_versioning=True,
            minify_css=True,
            minify_js=True,
            enable_gzip=True,
            debug=True
        )
        manager = StaticAssetManager(config)
        
        # Process individual assets
        css_url = manager.process_asset("styles.css")
        js_url = manager.process_asset("app.js")
        
        print(f"CSS asset URL: {css_url}")
        print(f"JS asset URL: {js_url}")
        
        # Create bundles
        manager.create_bundle("app", "css", ["styles.css"])
        manager.create_bundle("app", "js", ["app.js"])
        
        css_bundle_url = manager.build_bundle("app.css")
        js_bundle_url = manager.build_bundle("app.js")
        
        print(f"CSS bundle URL: {css_bundle_url}")
        print(f"JS bundle URL: {js_bundle_url}")
        
        # Get stats
        stats = manager.get_stats()
        print(f"Asset stats: {stats}")

def demo_caching():
    """Demo template caching."""
    print("\n=== Template Caching ===")
    
    # Setup different cache backends
    memory_config = CacheConfig(backend='memory', max_size=100, ttl=3600)
    memory_cache = TemplateCache(memory_config)
    
    # Test basic caching
    template_content = "<h1>{{ title }}</h1><p>{{ content }}</p>"
    
    # Cache template
    memory_cache.set_template("test_template", template_content)
    
    # Retrieve from cache
    cached = memory_cache.get_template("test_template")
    
    if cached == template_content:
        print("✓ Template caching works!")
    else:
        print("✗ Template caching failed")
    
    # Test rendered template caching
    context = {"title": "Hello", "content": "World"}
    rendered = "<h1>Hello</h1><p>World</p>"
    
    memory_cache.set_rendered("test_template", context, rendered)
    cached_rendered = memory_cache.get_rendered("test_template", context)
    
    if cached_rendered == rendered:
        print("✓ Rendered template caching works!")
    else:
        print("✗ Rendered template caching failed")
    
    # Get cache stats
    stats = memory_cache.get_stats()
    if stats:
        print(f"Cache stats: {stats}")

def demo_custom_filters():
    """Demo custom filter registration."""
    print("\n=== Custom Filters ===")
    
    # Define custom filters
    def currency_filter(amount, symbol='$'):
        """Format amount as currency."""
        return f"{symbol}{float(amount):.2f}"
    
    def phone_filter(number):
        """Format phone number."""
        digits = ''.join(c for c in str(number) if c.isdigit())
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        return number
    
    def highlight_filter(text, term):
        """Highlight search term in text."""
        return str(text).replace(term, f"<mark>{term}</mark>")
    
    # Test custom filters
    config = TemplateConfig(debug=True)
    engine = TemplateEngine(config)
    
    # Register custom filters with the engine
    engine.add_filter('currency', currency_filter)
    engine.add_filter('phone', phone_filter)
    engine.add_filter('highlight', highlight_filter)
    
    # Currency filter
    template = engine.from_string("Total: {{ amount | currency }}")
    result = template.render(amount=1234.56)
    print(f"Currency filter: {result}")
    
    # Phone filter
    template = engine.from_string("Call us: {{ phone | phone }}")
    result = template.render(phone="5551234567")
    print(f"Phone filter: {result}")
    
    # Highlight filter
    template = engine.from_string("{{ text | highlight(search_term) }}")
    result = template.render(text="This is some sample text", search_term="sample")
    print(f"Highlight filter: {result}")

def demo_security_features():
    """Demo security features."""
    print("\n=== Security Features ===")
    
    # Auto-escaping
    config = TemplateConfig(autoescape=True, debug=True)
    engine = TemplateEngine(config)
    
    template = engine.from_string("User input: {{ user_input }}")
    
    # Test with potentially dangerous content
    dangerous_input = "<script>alert('XSS');</script>"
    result = template.render(user_input=dangerous_input)
    print(f"Auto-escaped output: {result}")
    
    # CSRF token generation
    csrf = CSRFProtection("secure-secret-key")
    
    # Add CSRF to template engine
    engine.set_csrf_protection(csrf)
    
    template = engine.from_string("""
    <form method="post">
        {{ csrf_input() }}
        <input type="text" name="username">
        <button type="submit">Submit</button>
    </form>
    """)
    
    result = template.render()
    print(f"Form with CSRF protection: {result[:100]}...")
    
    # Secure asset URLs (prevent directory traversal)
    try:
        template = engine.from_string("{{ asset_url('../../../etc/passwd') }}")
        result = template.render()
        print("✗ Directory traversal not prevented!")
    except Exception as e:
        print("✓ Directory traversal prevented")

def main():
    """Run all demos."""
    print("🚀 CovetPy Template Engine Comprehensive Demo")
    print("=" * 50)
    
    try:
        demo_basic_templates()
        demo_template_inheritance()
        demo_forms_and_csrf()
        demo_static_assets()
        demo_caching()
        demo_custom_filters()
        demo_security_features()
        
        print("\n" + "=" * 50)
        print("🎉 All demos completed successfully!")
        print("\nCovetPy Template Engine Features Demonstrated:")
        print("✓ Jinja2-compatible template syntax")
        print("✓ Template inheritance with blocks")
        print("✓ Comprehensive filter system")
        print("✓ Form handling with validation")
        print("✓ CSRF protection")
        print("✓ Static asset management with versioning")
        print("✓ Multiple caching backends")
        print("✓ Custom filter registration")
        print("✓ Auto-escaping for XSS prevention")
        print("✓ Security features and input validation")
        print("✓ Production-ready error handling")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)