"""
CovetPy Template Engine Examples

Comprehensive examples demonstrating all features of the template engine.
"""

import logging
import os
import tempfile
from pathlib import Path

from covet.templates import (
    CovetTemplateIntegration,
    TemplateEngine,
    TemplateEngineFactory,
    render_string,
)

logger = logging.getLogger(__name__)


def create_example_templates():
    """Create example templates for demonstration."""

    # Create temporary directories
    temp_dir = Path(tempfile.mkdtemp())
    template_dir = temp_dir / "templates"
    static_dir = temp_dir / "static"

    template_dir.mkdir(exist_ok=True)
    static_dir.mkdir(exist_ok=True)

    # Base template with inheritance
    base_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}CovetPy Template Engine{% endblock %}</title>
    <link rel="stylesheet" href="{{ static('css/style.css') }}">
    {% block extra_head %}{% endblock %}
</head>
<body>
    <header>
        <h1>{% block header %}Welcome to CovetPy{% endblock %}</h1>
        <nav>
            <a href="{{ url_for('home') }}">Home</a>
            <a href="{{ url_for('about') }}">About</a>
            <a href="{{ url_for('contact') }}">Contact</a>
        </nav>
    </header>

    <main>
        {% block content %}
        <p>Default content</p>
        {% endblock %}
    </main>

    <footer>
        <p>&copy; {{ now().year }} CovetPy. All rights reserved.</p>
        {% block footer %}{% endblock %}
    </footer>

    {% block scripts %}
    <script src="{{ static('js/app.js') }}"></script>
    {% endblock %}
</body>
</html>"""

    # Child template extending base
    home_template = """{% extends "base.html" %}

{% block title %}Home - CovetPy{% endblock %}

{% block header %}Welcome Home!{% endblock %}

{% block content %}
<div class="hero">
    <h2>Hello, {{ user.name|default('Guest') }}!</h2>
    <p>Today is {{ now()|date('%B %d, %Y') }}</p>
</div>

<section class="features">
    <h3>Template Features</h3>
    <ul>
        {% for feature in features %}
        <li class="{{ loop.index|length > 5|bool ? 'highlight' : 'normal' }}">
            {{ feature.name }} - {{ feature.description|truncate(50) }}
            {% if feature.new %}
            <span class="badge">NEW</span>
            {% endif %}
        </li>
        {% else %}
        <li>No features available</li>
        {% endfor %}
    </ul>
</section>

<section class="stats">
    <h3>Statistics</h3>
    <div class="grid">
        <div class="stat-card">
            <h4>Total Users</h4>
            <p class="number">{{ stats.users|currency('', 0) }}</p>
        </div>
        <div class="stat-card">
            <h4>Active Templates</h4>
            <p class="number">{{ stats.templates }}</p>
        </div>
        <div class="stat-card">
            <h4>Performance</h4>
            <p class="number">{{ stats.render_time|round(2) }}ms</p>
        </div>
    </div>
</section>

{% include "partials/newsletter.html" %}
{% endblock %}

{% block extra_head %}
<meta name="description" content="CovetPy Template Engine demonstration">
<meta name="keywords" content="template, engine, python, covet">
{% endblock %}"""

    # Partial template for inclusion
    newsletter_template = """<section class="newsletter">
    <h3>Stay Updated</h3>
    <form action="{{ url_for('subscribe') }}" method="post">
        <input type="email" name="email" placeholder="Enter your email" required>
        <button type="submit">Subscribe</button>
    </form>
    <p class="privacy">We respect your privacy. Unsubscribe at any time.</p>
</section>"""

    # User profile template with loops and conditionals
    profile_template = """{% extends "base.html" %}

{% block title %}{{ user.name }}'s Profile{% endblock %}

{% block content %}
<div class="profile-header">
    <img src="{{ user.avatar|default(static('images/default-avatar.png')) }}"
         alt="{{ user.name }}'s avatar" class="avatar">
    <div class="info">
        <h2>{{ user.name }}</h2>
        <p class="email">{{ user.email }}</p>
        <p class="joined">Member since {{ user.created_at|age }}</p>

        {% if user.is_premium %}
        <span class="badge premium">Premium User</span>
        {% endif %}
    </div>
</div>

<div class="profile-content">
    <div class="tabs">
        <button class="tab active" data-tab="posts">Posts ({{ user.posts|length }})</button>
        <button class="tab" data-tab="followers">Followers ({{ user.followers|length }})</button>
        <button class="tab" data-tab="following">Following ({{ user.following|length }})</button>
    </div>

    <div class="tab-content active" id="posts">
        {% for post in user.posts|sort('created_at', reverse=True)|slice(0, 10) %}
        <article class="post">
            <h3><a href="{{ url_for('post', id=post.id) }}">{{ post.title }}</a></h3>
            <p class="meta">
                Posted {{ post.created_at|naturaltime }}
                {% if post.edited %}(edited {{ post.updated_at|naturaltime }}){% endif %}
            </p>
            <div class="content">
                {{ post.content|truncate(200)|safe }}
            </div>
            <div class="stats">
                <span class="likes">{{ post.likes|length }} likes</span>
                <span class="comments">{{ post.comments|length }} comments</span>
            </div>
        </article>
        {% else %}
        <p class="empty">No posts yet.</p>
        {% endfor %}
    </div>

    <div class="tab-content" id="followers">
        <div class="user-grid">
            {% for follower in user.followers|batch(3) %}
            <div class="user-row">
                {% for user in follower %}
                <div class="user-card">
                    <img src="{{ user.avatar|default(static('images/default-avatar.png')) }}"
                         alt="{{ user.name }}">
                    <h4>{{ user.name }}</h4>
                    <p>{{ user.bio|default('No bio available')|truncate(50) }}</p>
                </div>
                {% endfor %}
            </div>
            {% endfor %}
        </div>
    </div>
</div>
{% endblock %}"""

    # Data listing template with advanced filters
    data_template = """{% extends "base.html" %}

{% block title %}Data Dashboard{% endblock %}

{% block content %}
<div class="dashboard">
    <h2>Data Dashboard</h2>

    <div class="filters">
        <select name="category">
            <option value="">All Categories</option>
            {% for category in data|map(attribute='category')|unique|sort %}
            <option value="{{ category }}">{{ category|title }}</option>
            {% endfor %}
        </select>

        <input type="search" placeholder="Search..." name="search">
        <button type="button" id="apply-filters">Apply Filters</button>
    </div>

    <div class="summary">
        <div class="metric">
            <h3>Total Records</h3>
            <p class="value">{{ data|length|currency('', 0) }}</p>
        </div>
        <div class="metric">
            <h3>Categories</h3>
            <p class="value">{{ data|map(attribute='category')|unique|length }}</p>
        </div>
        <div class="metric">
            <h3>Average Value</h3>
            <p class="value">{{ data|map(attribute='value')|sum / data|length|round(2) }}</p>
        </div>
        <div class="metric">
            <h3>Last Updated</h3>
            <p class="value">{{ last_updated|naturaltime }}</p>
        </div>
    </div>

    <table class="data-table">
        <thead>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Category</th>
                <th>Value</th>
                <th>Created</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for item in data|sort('created_at', reverse=True) %}
            <tr class="{{ 'highlight' if item.value > average_value else '' }}">
                <td>{{ item.id }}</td>
                <td>
                    <strong>{{ item.name }}</strong>
                    {% if item.description %}
                    <br><small>{{ item.description|truncate(30) }}</small>
                    {% endif %}
                </td>
                <td>
                    <span class="category-tag category-{{ item.category|slugify }}">
                        {{ item.category }}
                    </span>
                </td>
                <td class="value">
                    {{ item.value|currency }}
                    {% if item.change %}
                    <span class="change {{ 'positive' if item.change > 0 else 'negative' }}">
                        {{ item.change|percentage }}
                    </span>
                    {% endif %}
                </td>
                <td>{{ item.created_at|datetime('%m/%d/%Y') }}</td>
                <td>
                    <span class="status status-{{ item.status|slugify }}">
                        {{ item.status|title }}
                    </span>
                </td>
                <td class="actions">
                    <a href="{{ url_for('edit', id=item.id) }}" class="btn btn-sm">Edit</a>
                    <a href="{{ url_for('delete', id=item.id) }}"
                       class="btn btn-sm btn-danger"
                       onclick="return confirm('Are you sure?')">Delete</a>
                </td>
            </tr>
            {% else %}
            <tr>
                <td colspan="7" class="empty">No data available</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    {% if data|length > 20 %}
    <div class="pagination">
        <!-- Pagination would be implemented here -->
        <p>Showing {{ data|length }} records</p>
    </div>
    {% endif %}
</div>
{% endblock %}"""

    # Error page template
    error_template = """{% extends "base.html" %}

{% block title %}Error {{ error_code }}{% endblock %}

{% block content %}
<div class="error-page">
    <div class="error-icon">{{ error_code }}</div>
    <h2>{{ error_message|default('Something went wrong') }}</h2>
    <p>{{ error_description|default('Please try again later or contact support.') }}</p>

    {% if suggestions %}
    <div class="suggestions">
        <h3>You might want to:</h3>
        <ul>
            {% for suggestion in suggestions %}
            <li>{{ suggestion }}</li>
            {% endfor %}
        </ul>
    </div>
    {% endif %}

    <div class="actions">
        <a href="{{ url_for('home') }}" class="btn btn-primary">Go Home</a>
        <button onclick="history.back()" class="btn btn-secondary">Go Back</button>
        {% if contact_support %}
        <a href="{{ url_for('contact') }}" class="btn btn-outline">Contact Support</a>
        {% endif %}
    </div>
</div>
{% endblock %}"""

    # Macro examples template
    macro_template = """{% macro render_form_field(field, label, type='text', required=False, placeholder='') %}
<div class="form-field">
    <label for="{{ field }}">
        {{ label }}
        {% if required %}<span class="required">*</span>{% endif %}
    </label>
    <input type="{{ type }}"
           id="{{ field }}"
           name="{{ field }}"
           placeholder="{{ placeholder }}"
           {% if required %}required{% endif %}>
</div>
{% endmacro %}

{% macro render_alert(message, type='info', dismissible=True) %}
<div class="alert alert-{{ type }}{% if dismissible %} alert-dismissible{% endif %}">
    {{ message }}
    {% if dismissible %}
    <button type="button" class="close" data-dismiss="alert">&times;</button>
    {% endif %}
</div>
{% endmacro %}

{% macro render_card(title, content, footer='', classes='') %}
<div class="card {{ classes }}">
    {% if title %}
    <div class="card-header">
        <h5 class="card-title">{{ title }}</h5>
    </div>
    {% endif %}
    <div class="card-body">
        {{ content }}
    </div>
    {% if footer %}
    <div class="card-footer">
        {{ footer }}
    </div>
    {% endif %}
</div>
{% endmacro %}

<!-- Example usage -->
<form class="contact-form">
    {{ render_form_field('name', 'Full Name', required=True, placeholder='Enter your name') }}
    {{ render_form_field('email', 'Email Address', type='email', required=True) }}
    {{ render_form_field('phone', 'Phone Number', type='tel', placeholder='(555) 123-4567') }}
    {{ render_form_field('message', 'Message', type='textarea', required=True) }}

    <button type="submit" class="btn btn-primary">Send Message</button>
</form>

{{ render_alert('Form submitted successfully!', type='success') }}
{{ render_alert('Please fill in all required fields.', type='warning') }}

{{ render_card('User Profile', user.bio, footer='Member since ' + user.created_at|date) }}"""

    # Write templates to files
    templates = {
        "base.html": base_template,
        "home.html": home_template,
        "profile.html": profile_template,
        "data.html": data_template,
        "error.html": error_template,
        "macros.html": macro_template,
        "partials/newsletter.html": newsletter_template,
    }

    for template_name, content in templates.items():
        template_path = template_dir / template_name
        template_path.parent.mkdir(parents=True, exist_ok=True)
        template_path.write_text(content)

    # Create sample CSS
    css_content = """/* CovetPy Template Engine Demo Styles */
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 0;
    background: #f5f5f5;
}

header {
    background: #2c3e50;
    color: white;
    padding: 1rem 0;
}

header h1 {
    margin: 0;
    text-align: center;
}

nav {
    text-align: center;
    margin-top: 1rem;
}

nav a {
    color: white;
    text-decoration: none;
    margin: 0 1rem;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    transition: background 0.3s;
}

nav a:hover {
    background: rgba(255, 255, 255, 0.1);
}

main {
    max-width: 1200px;
    margin: 2rem auto;
    padding: 0 1rem;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.hero {
    text-align: center;
    padding: 3rem 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 8px;
    margin-bottom: 2rem;
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    margin: 2rem 0;
}

.stat-card, .card {
    padding: 1.5rem;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    border-left: 4px solid #3498db;
}

.number {
    font-size: 2rem;
    font-weight: bold;
    color: #2c3e50;
    margin: 0;
}

.badge {
    background: #e74c3c;
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: bold;
}

.premium {
    background: #f39c12;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
    margin: 2rem 0;
}

.data-table th,
.data-table td {
    padding: 1rem;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

.data-table th {
    background: #f8f9fa;
    font-weight: 600;
}

.data-table tr:hover {
    background: #f8f9fa;
}

.highlight {
    background: #fff3cd !important;
}

.btn {
    display: inline-block;
    padding: 0.5rem 1rem;
    background: #3498db;
    color: white;
    text-decoration: none;
    border-radius: 4px;
    border: none;
    cursor: pointer;
    transition: background 0.3s;
}

.btn:hover {
    background: #2980b9;
}

.btn-danger {
    background: #e74c3c;
}

.btn-danger:hover {
    background: #c0392b;
}

.alert {
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 4px;
    border-left: 4px solid;
}

.alert-success {
    background: #d4edda;
    border-color: #28a745;
    color: #155724;
}

.alert-warning {
    background: #fff3cd;
    border-color: #ffc107;
    color: #856404;
}

.alert-info {
    background: #d1ecf1;
    border-color: #17a2b8;
    color: #0c5460;
}

.form-field {
    margin-bottom: 1rem;
}

.form-field label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
}

.form-field input,
.form-field textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
}

.required {
    color: #e74c3c;
}

footer {
    text-align: center;
    padding: 2rem 0;
    background: #34495e;
    color: white;
    margin-top: 2rem;
}"""

    css_dir = static_dir / "css"
    css_dir.mkdir(exist_ok=True)
    (css_dir / "style.css").write_text(css_content)

    return str(template_dir), str(static_dir)


def demonstrate_basic_usage():
    """Demonstrate basic template engine usage."""
    logger.info("=== Basic Template Engine Usage ===")

    # Simple string template
    template = "Hello, {{ name }}! Today is {{ date|date('%B %d, %Y') }}."
    render_string(template, {"name": "World", "date": "2024-01-15"})
    logger.info("String template: {result}")

    # Template with filters
    template = "{{ message|upper|center(50) }}"
    render_string(template, {"message": "CovetPy Templates"})
    logger.info("Filters: '{result}'")

    # Template with conditionals
    template = """
    {% if user.is_admin %}
    Welcome, Admin {{ user.name }}!
    {% else %}
    Hello, {{ user.name }}
    {% endif %}
    """
    render_string(template, {"user": {"name": "John", "is_admin": True}})
    logger.info("Conditionals: {result.strip()}")


def demonstrate_advanced_features():
    """Demonstrate advanced template features."""
    logger.info("\n=== Advanced Template Features ===")

    template_dir, static_dir = create_example_templates()

    # Create engine with custom configuration
    engine = TemplateEngine(
        template_dirs=[template_dir],
        static_dirs=[static_dir],
        auto_escape=True,
        debug=True,
    )

    # Add custom filter
    def highlight_filter(text, term):
        return text.replace(term, f"<mark>{term}</mark>")

    engine.add_filter("highlight", highlight_filter)

    # Sample data for templates
    context = {
        "user": {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "is_premium": True,
            "created_at": "2023-06-15T10:30:00Z",
            "avatar": None,
            "posts": [
                {
                    "id": 1,
                    "title": "Getting Started with CovetPy",
                    "content": "CovetPy is an amazing framework for building web applications...",
                    "created_at": "2024-01-10T14:30:00Z",
                    "likes": [1, 2, 3, 4, 5],
                    "comments": [1, 2, 3],
                },
                {
                    "id": 2,
                    "title": "Template Engine Deep Dive",
                    "content": "The template engine provides powerful features for rendering dynamic content...",
                    "created_at": "2024-01-08T09:15:00Z",
                    "likes": [1, 2],
                    "comments": [1, 2, 3, 4],
                },
            ],
            "followers": [
                {"name": "Bob Smith", "bio": "Web developer"},
                {"name": "Carol White", "bio": "UI/UX Designer"},
                {"name": "David Brown", "bio": "Full-stack engineer"},
            ],
        },
        "features": [
            {
                "name": "Template Inheritance",
                "description": "Extend and override template blocks",
                "new": False,
            },
            {
                "name": "Auto-escaping",
                "description": "Automatic XSS protection",
                "new": False,
            },
            {
                "name": "Custom Filters",
                "description": "Create your own template filters",
                "new": True,
            },
            {
                "name": "Static Files",
                "description": "Efficient static file serving",
                "new": False,
            },
            {
                "name": "Caching",
                "description": "Built-in template caching",
                "new": False,
            },
        ],
        "stats": {"users": 1250, "templates": 45, "render_time": 2.34},
    }

    # Render home page
    logger.info("Rendering home page...")
    try:
        home_html = engine.render("home.html", context)
        logger.info("Home page rendered successfully ({len(home_html)} characters)")

        # Show snippet
        lines = home_html.split("\n")
        logger.info("Preview (first 10 lines):")
        for i, line in enumerate(lines[:10]):
            logger.info("  {i+1:2}: {line}")

    except Exception:
        logger.error("Error rendering home page: {e}")

    # Render user profile
    logger.info("\nRendering user profile...")
    try:
        engine.render("profile.html", context)
        logger.info("Profile page rendered successfully ({len(profile_html)} characters)")
    except Exception:
        logger.error("Error rendering profile: {e}")


def demonstrate_security_features():
    """Demonstrate security features."""
    logger.info("\n=== Security Features ===")

    # Auto-escaping demonstration
    engine = TemplateEngine(auto_escape=True)

    dangerous_input = "<script>alert('XSS')</script>"

    # Auto-escaped output
    template = "User input: {{ input }}"
    engine.render_string(template, {"input": dangerous_input})
    logger.info("Auto-escaped: {result}")

    # Safe string (no escaping)
    from covet.templates import safe_string

    template = "Safe content: {{ content }}"
    engine.render_string(template, {"content": safe_string("<b>Bold text</b>")})
    logger.info("Safe string: {result}")

    # Manual escaping
    from covet.templates import escape_html

    escape_html(dangerous_input)
    logger.info("Manual escape: {escaped}")


def demonstrate_performance_features():
    """Demonstrate performance features."""
    logger.info("\n=== Performance Features ===")

    import time

    # Create engine with caching
    engine = TemplateEngine(cache_size=1000, cache_ttl=3600)

    template_content = """
    <h1>{{ title }}</h1>
    <ul>
    {% for item in items %}
        <li>{{ item.name }} - {{ item.value|currency }}</li>
    {% endfor %}
    </ul>
    """

    context = {
        "title": "Performance Test",
        "items": [{"name": f"Item {i}", "value": i * 10.5} for i in range(100)],
    }

    # First render (compilation)
    start_time = time.time()
    engine.render_string(template_content, context)
    time.time() - start_time

    # Second render (cached)
    start_time = time.time()
    engine.render_string(template_content, context)
    time.time() - start_time

    logger.info("First render (with compilation): {first_render_time:.4f}s")
    logger.info("Second render (cached): {second_render_time:.4f}s")
    logger.info("Speedup: {first_render_time / second_render_time:.1f}x")
    logger.info("Output length: {len(result1)} characters")


def demonstrate_integration():
    """Demonstrate framework integration."""
    logger.info("\n=== Framework Integration ===")

    # Mock CovetPy app
    class MockApp:
        def __init__(self):
            self.config = {
                "DEBUG": True,
                "TEMPLATE_DIRS": ["templates"],
                "STATIC_DIRS": ["static"],
            }

        def get_template_context(self):
            return {"app_name": "My CovetPy App", "version": "1.0.0"}

    app = MockApp()

    # Initialize template integration
    template_integration = CovetTemplateIntegration()
    template_integration.init_app(app, app.config)

    # Render template with app context
    template = """
    App: {{ app_name }} v{{ version }}
    Config: {{ config.DEBUG }}
    """

    try:
        template_integration.engine.render_string(template, {})
        logger.info("Integration result: {result.strip()}")
    except Exception:
        logger.error("Integration error: {e}")


def run_all_examples():
    """Run all template engine examples."""
    logger.info("CovetPy Template Engine - Comprehensive Examples")
    logger.info("=" * 50)

    demonstrate_basic_usage()
    demonstrate_advanced_features()
    demonstrate_security_features()
    demonstrate_performance_features()
    demonstrate_integration()

    logger.info("\n" + "=" * 50)
    logger.info("All examples completed successfully!")


if __name__ == "__main__":
    run_all_examples()
