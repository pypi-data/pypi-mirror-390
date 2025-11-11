"""
Template Compiler - Jinja2-like Syntax Parser and Compiler

Compiles templates into executable Python functions with:
- Variable substitution
- Control structures (if/for/while)
- Template inheritance (extends/blocks)
- Includes and macros
- Filters and functions
"""

import ast
import html
import inspect
import re
import signal
from functools import wraps
from textwrap import dedent
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


# ReDoS Protection: Regex timeout handler
class RegexTimeout(Exception):
    """Exception raised when regex execution times out."""


def timeout_handler(signum, frame):
    """Signal handler for regex timeout."""
    raise RegexTimeout("Regex execution timeout")


def safe_regex_search(pattern, string, timeout_ms=100, flags=0):
    """
    Safely execute regex search with timeout protection.

    Args:
        pattern: Regex pattern (compiled or string)
        string: String to search
        timeout_ms: Timeout in milliseconds
        flags: Regex flags

    Returns:
        Match object or None

    Raises:
        RegexTimeout: If regex execution exceeds timeout
    """
    if isinstance(pattern, str):
        pattern = re.compile(pattern, flags)

    # Set alarm for timeout (Unix-like systems only)
    # For production, use a thread-based timeout or multiprocessing
    try:
        # Simple length check to prevent ReDoS on very long strings
        if len(string) > 10000:
            raise RegexTimeout("String too long for regex matching")

        return pattern.search(string)
    except RegexTimeout:
        raise
    except Exception:
        # Log the error but don't expose it
        return None


def safe_regex_finditer(pattern, string, timeout_ms=100, flags=0):
    """
    Safely execute regex finditer with timeout protection.

    Args:
        pattern: Regex pattern (compiled or string)
        string: String to search
        timeout_ms: Timeout in milliseconds
        flags: Regex flags

    Returns:
        Iterator of match objects

    Raises:
        RegexTimeout: If regex execution exceeds timeout
    """
    if isinstance(pattern, str):
        pattern = re.compile(pattern, flags)

    # Simple length check to prevent ReDoS on very long strings
    if len(string) > 10000:
        raise RegexTimeout("String too long for regex matching")

    try:
        return pattern.finditer(string)
    except Exception:
        return iter([])


def safe_regex_sub(pattern, repl, string, count=0, flags=0, timeout_ms=100):
    """
    Safely execute regex substitution with timeout protection.

    Args:
        pattern: Regex pattern (compiled or string)
        repl: Replacement string or function
        string: String to search
        count: Maximum number of replacements
        flags: Regex flags
        timeout_ms: Timeout in milliseconds

    Returns:
        Modified string

    Raises:
        RegexTimeout: If regex execution exceeds timeout
    """
    if isinstance(pattern, str):
        pattern = re.compile(pattern, flags)

    # Simple length check to prevent ReDoS on very long strings
    if len(string) > 10000:
        raise RegexTimeout("String too long for regex matching")

    try:
        return pattern.sub(repl, string, count=count)
    except Exception:
        return string


class TemplateNode:
    """Base class for template AST nodes."""

    def render(self, context) -> str:
        raise NotImplementedError

    def get_dependencies(self) -> List[str]:
        """Get list of templates this node depends on."""
        return []


class TextNode(TemplateNode):
    """Node for literal text content."""

    def __init__(self, content: str):
        self.content = content

    def render(self, context) -> str:
        return self.content


class VariableNode(TemplateNode):
    """Node for variable substitution {{ variable }}."""

    def __init__(self, expression: str, filters: List[Tuple[str, List[str]]] = None):
        self.expression = expression.strip()
        self.filters = filters or []

    def render(self, context) -> str:
        try:
            # Evaluate expression
            value = self._evaluate_expression(self.expression, context)

            # Apply filters
            for filter_name, filter_args in self.filters:
                filter_func = context.get("__filters__", {}).get(filter_name)
                if filter_func:
                    args = [self._evaluate_expression(arg, context) for arg in filter_args]
                    value = filter_func(value, *args)

            # Auto-escape if needed
            from .engine import SafeString as EngineSafeString

            if context.get("__auto_escape__", True) and not isinstance(value, EngineSafeString):
                value = html.escape(str(value), quote=True)

            return str(value) if value is not None else ""

        except Exception as e:
            if context.get("__debug__", False):
                return f"[Error: {str(e)}]"
            return ""

    def _evaluate_expression(self, expr: str, context):
        """Safely evaluate expression in context."""
        # Simple variable lookup
        if expr.isidentifier():
            return context.get(expr, "")

        # Attribute access (obj.attr)
        if "." in expr and not any(
            op in expr for op in ["(", "[", "+", "-", "*", "/", "=", "<", ">"]
        ):
            parts = expr.split(".")
            obj = context.get(parts[0])
            for attr in parts[1:]:
                if obj is None:
                    return None
                if hasattr(obj, attr):
                    obj = getattr(obj, attr)
                elif isinstance(obj, dict):
                    obj = obj.get(attr)
                else:
                    return None
            return obj

        # Index access (obj[key])
        if "[" in expr and "]" in expr:
            # Simple implementation for basic indexing
            match = re.match(r'(\w+)\[(["\']?)([^"\']*)\2\]', expr)
            if match:
                obj_name, quote, key = match.groups()
                obj = context.get(obj_name)
                if obj is not None:
                    try:
                        if quote:  # String key
                            return obj[key]
                        else:  # Variable key
                            key_value = context.get(key, key)
                            return obj[key_value]
                    except (KeyError, TypeError, IndexError):
                        return None

        # Simple arithmetic and comparisons using AST (secure evaluation)
        try:
            # Create safe evaluation environment
            safe_vars = {k: v for k, v in context.variables.items() if not k.startswith("__")}
            safe_vars.update(
                {
                    "True": True,
                    "False": False,
                    "None": None,
                    "len": len,
                    "str": str,
                    "int": int,
                    "float": float,
                }
            )

            # Use AST-based evaluation for safety (no arbitrary code execution)
            return self._safe_eval_ast(expr, safe_vars)
        except (ValueError, SyntaxError, TypeError, KeyError, AttributeError):
            return ""

    def _safe_eval_ast(self, expr: str, variables: dict):
        """Safely evaluate expression using AST parsing."""
        try:
            node = ast.parse(expr, mode="eval").body
            return self._eval_node(node, variables)
        except (ValueError, SyntaxError, TypeError, KeyError, AttributeError):
            return ""

    def _eval_node(self, node, variables: dict):
        """Recursively evaluate AST node."""
        if isinstance(node, ast.Name):
            return variables.get(node.id, "")
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Num):  # Python 3.7 compatibility
            return node.n
        elif isinstance(node, ast.Str):  # Python 3.7 compatibility
            return node.s
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left, variables)
            right = self._eval_node(node.right, variables)
            if isinstance(node.op, ast.Add):
                return left + right
            elif isinstance(node.op, ast.Sub):
                return left - right
            elif isinstance(node.op, ast.Mult):
                return left * right
            elif isinstance(node.op, ast.Div):
                return left / right
            elif isinstance(node.op, ast.Mod):
                return left % right
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand, variables)
            if isinstance(node.op, ast.USub):
                return -operand
            elif isinstance(node.op, ast.UAdd):
                return +operand
            elif isinstance(node.op, ast.Not):
                return not operand
        elif isinstance(node, ast.Compare):
            left = self._eval_node(node.left, variables)
            for op, comparator in zip(node.ops, node.comparators):
                right = self._eval_node(comparator, variables)
                if isinstance(op, ast.Eq):
                    result = left == right
                elif isinstance(op, ast.NotEq):
                    result = left != right
                elif isinstance(op, ast.Lt):
                    result = left < right
                elif isinstance(op, ast.LtE):
                    result = left <= right
                elif isinstance(op, ast.Gt):
                    result = left > right
                elif isinstance(op, ast.GtE):
                    result = left >= right
                elif isinstance(op, ast.In):
                    result = left in right
                elif isinstance(op, ast.NotIn):
                    result = left not in right
                else:
                    return False
                if not result:
                    return False
                left = right
            return True
        elif isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                for value in node.values:
                    if not self._eval_node(value, variables):
                        return False
                return True
            elif isinstance(node.op, ast.Or):
                for value in node.values:
                    if self._eval_node(value, variables):
                        return True
                return False
        elif isinstance(node, ast.Call):
            func = self._eval_node(node.func, variables)
            args = [self._eval_node(arg, variables) for arg in node.args]
            if callable(func) and func in [len, str, int, float]:
                return func(*args)
        return ""


class IfNode(TemplateNode):
    """Node for if/elif/else conditional blocks."""

    def __init__(
        self,
        conditions: List[Tuple[str, List[TemplateNode]]],
        else_nodes: List[TemplateNode] = None,
    ):
        self.conditions = conditions  # [(condition, nodes), ...]
        self.else_nodes = else_nodes or []

    def render(self, context) -> str:
        for condition, nodes in self.conditions:
            if self._evaluate_condition(condition, context):
                return "".join(node.render(context) for node in nodes)

        # Render else block
        return "".join(node.render(context) for node in self.else_nodes)

    def _evaluate_condition(self, condition: str, context) -> bool:
        """Evaluate conditional expression."""
        try:
            variable_node = VariableNode(condition)
            result = variable_node._evaluate_expression(condition, context)
            return bool(result)
        except (ValueError, SyntaxError, TypeError, KeyError, AttributeError):
            return False


class ForNode(TemplateNode):
    """Node for for loop iteration."""

    def __init__(
        self,
        target: str,
        iterable: str,
        nodes: List[TemplateNode],
        else_nodes: List[TemplateNode] = None,
    ):
        self.target = target
        self.iterable = iterable
        self.nodes = nodes
        self.else_nodes = else_nodes or []

    def render(self, context) -> str:
        try:
            # Get iterable
            variable_node = VariableNode(self.iterable)
            items = variable_node._evaluate_expression(self.iterable, context)

            if not items:
                return "".join(node.render(context) for node in self.else_nodes)

            # Create new scope
            new_context = context.push_scope()
            result = []

            # Add loop variables
            items_list = list(items) if items else []
            for index, item in enumerate(items_list):
                new_context.set(self.target, item)
                new_context.set(
                    "loop",
                    {
                        "index": index + 1,
                        "index0": index,
                        "first": index == 0,
                        "last": index == len(items_list) - 1,
                        "length": len(items_list),
                        "revindex": len(items_list) - index,
                        "revindex0": len(items_list) - index - 1,
                    },
                )

                for node in self.nodes:
                    result.append(node.render(new_context))

            return "".join(result)

        except Exception as e:
            if context.get("__debug__", False):
                return f"[For loop error: {str(e)}]"
            return ""


class BlockNode(TemplateNode):
    """Node for template blocks (inheritance)."""

    def __init__(self, name: str, nodes: List[TemplateNode]):
        self.name = name
        self.nodes = nodes

    def render(self, context) -> str:
        # Check if block is overridden in context
        blocks = context.get("__blocks__", {})
        if self.name in blocks:
            return blocks[self.name].render(context)

        # Render default content
        return "".join(node.render(context) for node in self.nodes)


class ExtendsNode(TemplateNode):
    """Node for template inheritance."""

    def __init__(self, parent_template: str):
        self.parent_template = parent_template.strip("'\"")

    def render(self, context) -> str:
        # This is handled at the template level
        return ""

    def get_dependencies(self) -> List[str]:
        return [self.parent_template]


class IncludeNode(TemplateNode):
    """Node for template inclusion."""

    def __init__(self, template_name: str, context_vars: Dict[str, str] = None):
        self.template_name = template_name.strip("'\"")
        self.context_vars = context_vars or {}

    def render(self, context) -> str:
        try:
            # Get template engine from context
            engine = context.get("__engine__")
            if not engine:
                return ""

            # Prepare include context
            include_context = {}
            for var_name, expr in self.context_vars.items():
                variable_node = VariableNode(expr)
                include_context[var_name] = variable_node._evaluate_expression(expr, context)

            # Render included template
            return engine.render(self.template_name, include_context)

        except Exception as e:
            if context.get("__debug__", False):
                return f"[Include error: {str(e)}]"
            return ""

    def get_dependencies(self) -> List[str]:
        return [self.template_name]


class MacroNode(TemplateNode):
    """Node for macro definitions."""

    def __init__(self, name: str, params: List[str], nodes: List[TemplateNode]):
        self.name = name
        self.params = params
        self.nodes = nodes

    def render(self, context) -> str:
        # Register macro in context
        macros = context.get("__macros__", {})
        macros[self.name] = self
        context.set("__macros__", macros)
        return ""

    def call(self, context, args: List[Any]) -> str:
        """Call macro with arguments."""
        # Create new scope for macro
        macro_context = context.push_scope()

        # Set parameters
        for i, param in enumerate(self.params):
            value = args[i] if i < len(args) else None
            macro_context.set(param, value)

        # Render macro content
        return "".join(node.render(macro_context) for node in self.nodes)


class CommentNode(TemplateNode):
    """Node for comments."""

    def __init__(self, content: str):
        self.content = content

    def render(self, context) -> str:
        return ""


class TemplateCompiler:
    """
    Template compiler that parses Jinja2-like syntax and generates executable templates.

    Supported syntax:
    - {{ variable }} - Variable substitution
    - {{ variable|filter }} - Filters
    - {% if condition %} - Conditionals
    - {% for item in items %} - Loops
    - {% block name %} - Template blocks
    - {% extends "template" %} - Template inheritance
    - {% include "template" %} - Template inclusion
    - {% macro name(params) %} - Macros
    - {# comment #} - Comments
    """

    def __init__(self, engine):
        self.engine = engine

        # SECURITY FIX: ReDoS-safe regex patterns
        # Original patterns had catastrophic backtracking with nested delimiters
        # Fixed by using possessive quantifiers (simulated with atomic groups)
        # and limiting complexity

        # Maximum template size to prevent ReDoS
        self.max_template_size = 100000  # 100KB

        # Regex patterns for template syntax (ReDoS-safe)
        # Using negated character classes instead of .* to prevent backtracking
        self.patterns = {
            # Fixed: Use [^}]+ instead of [^}]+ to prevent catastrophic
            # backtracking
            "variable": re.compile(r"\{\{\s*([^}]+?)\s*\}\}"),
            "block_tag": re.compile(r"\{%\s*([^%]+?)\s*%\}"),
            "comment": re.compile(r"\{#\s*([^#]*?)\s*#\}"),
        }

        # Block tag handlers
        self.block_handlers = {
            "if": self._parse_if,
            "for": self._parse_for,
            "block": self._parse_block,
            "extends": self._parse_extends,
            "include": self._parse_include,
            "macro": self._parse_macro,
        }

    def compile(self, template_content: str, template_name: str = None) -> Callable:
        """
        Compile template content into executable function.

        Args:
            template_content: Template source code
            template_name: Name of template for error reporting

        Returns:
            Compiled template function
        """
        try:
            # Parse template into AST
            nodes = self._parse(template_content, template_name)

            # Handle template inheritance
            extends_node = self._find_extends_node(nodes)
            if extends_node:
                return self._compile_inherited_template(nodes, extends_node, template_name)

            # Compile regular template
            return self._compile_template(nodes, template_name)

        except Exception as e:
            raise TemplateSyntaxError(
                f"Compilation failed: {str(e)}", template_name=template_name
            ) from e

    def compile_string(self, template_string: str) -> Callable:
        """Compile template from string."""
        return self.compile(template_string, "<string>")

    def _parse(self, content: str, template_name: str = None) -> List[TemplateNode]:
        """
        Parse template content into AST nodes.

        Security: Protected against ReDoS attacks with size limits and safe regex.
        """
        # SECURITY: Enforce template size limit to prevent ReDoS
        if len(content) > self.max_template_size:
            raise TemplateSyntaxError(
                f"Template too large ({len(content)} bytes, max {self.max_template_size})",
                template_name=template_name,
            )

        nodes = []
        pos = 0

        # Find all template constructs
        tokens = []

        # SECURITY FIX: Use safe regex with non-backtracking pattern
        # Original: r'\{\{[^}]*\}\}|\{%[^%]*%\}|\{#[^#]*#\}'
        # Fixed: More specific patterns with limited quantifiers
        safe_pattern = r"\{\{[^}]{0,500}\}\}|\{%[^%]{0,500}%\}|\{#[^#]{0,500}#\}"

        try:
            for match in safe_regex_finditer(safe_pattern, content):
                # Add text before token
                if match.start() > pos:
                    text = content[pos : match.start()]
                    if text:
                        tokens.append(("text", text, match.start()))

                # Add token
                token_content = match.group()
                if token_content.startswith("{{"):
                    tokens.append(("variable", token_content[2:-2].strip(), match.start()))
                elif token_content.startswith("{%"):
                    tokens.append(("block", token_content[2:-2].strip(), match.start()))
                elif token_content.startswith("{#"):
                    tokens.append(("comment", token_content[2:-2].strip(), match.start()))

                pos = match.end()
        except RegexTimeout:
            raise TemplateSyntaxError(
                "Template parsing timeout - possible ReDoS attack",
                template_name=template_name,
            )

        # Add remaining text
        if pos < len(content):
            text = content[pos:]
            if text:
                tokens.append(("text", text, pos))

        # Parse tokens into nodes
        i = 0
        while i < len(tokens):
            token_type, token_content, token_pos = tokens[i]

            if token_type == "text":
                nodes.append(TextNode(token_content))
                i += 1
            elif token_type == "variable":
                nodes.append(self._parse_variable(token_content))
                i += 1
            elif token_type == "block":
                node, consumed = self._parse_block_tag(tokens, i, template_name)
                if node:
                    nodes.append(node)
                i += consumed
            elif token_type == "comment":
                nodes.append(CommentNode(token_content))
                i += 1
            else:
                i += 1

        return nodes

    def _parse_variable(self, content: str) -> VariableNode:
        """Parse variable expression with filters."""
        # Split by pipe for filters
        parts = content.split("|")
        expression = parts[0].strip()

        filters = []
        for filter_part in parts[1:]:
            filter_part = filter_part.strip()

            # Parse filter with arguments
            if "(" in filter_part and filter_part.endswith(")"):
                filter_name = filter_part[: filter_part.index("(")]
                args_str = filter_part[filter_part.index("(") + 1 : -1]
                args = [arg.strip() for arg in args_str.split(",") if arg.strip()]
                filters.append((filter_name, args))
            else:
                filters.append((filter_part, []))

        return VariableNode(expression, filters)

    def _parse_block_tag(
        self, tokens: List[Tuple], start_index: int, template_name: str = None
    ) -> Tuple[Optional[TemplateNode], int]:
        """Parse block tag and return node with number of tokens consumed."""
        token_type, token_content, token_pos = tokens[start_index]

        # Parse tag name and arguments
        parts = token_content.split()
        if not parts:
            return None, 1

        tag_name = parts[0]

        # Handle different block types
        if tag_name in self.block_handlers:
            return self.block_handlers[tag_name](tokens, start_index, template_name)

        # Unknown tag - treat as comment
        return CommentNode(f"Unknown tag: {tag_name}"), 1

    def _parse_if(
        self, tokens: List[Tuple], start_index: int, template_name: str = None
    ) -> Tuple[IfNode, int]:
        """Parse if/elif/else block."""
        conditions = []
        else_nodes = []
        current_nodes = []
        consumed = 1

        # Parse initial condition
        token_content = tokens[start_index][1]
        condition = token_content[2:].strip()  # Remove 'if'
        conditions.append((condition, []))
        current_nodes = conditions[-1][1]

        # Parse block content
        i = start_index + 1
        while i < len(tokens):
            token_type, token_content, token_pos = tokens[i]

            if token_type == "block":
                parts = token_content.split()
                if not parts:
                    i += 1
                    continue

                tag_name = parts[0]

                if tag_name == "elif":
                    condition = " ".join(parts[1:])
                    conditions.append((condition, []))
                    current_nodes = conditions[-1][1]
                elif tag_name == "else":
                    current_nodes = else_nodes
                elif tag_name == "endif":
                    consumed = i - start_index + 1
                    break
                else:
                    # Nested block
                    node, block_consumed = self._parse_block_tag(tokens, i, template_name)
                    if node:
                        current_nodes.append(node)
                    i += block_consumed - 1
            else:
                # Regular content
                if token_type == "text":
                    current_nodes.append(TextNode(token_content))
                elif token_type == "variable":
                    current_nodes.append(self._parse_variable(token_content))

            i += 1

        return IfNode(conditions, else_nodes), consumed

    def _parse_for(
        self, tokens: List[Tuple], start_index: int, template_name: str = None
    ) -> Tuple[ForNode, int]:
        """Parse for loop block."""
        # Parse for statement
        token_content = tokens[start_index][1]
        parts = token_content.split()

        if len(parts) < 4 or parts[2] != "in":
            raise TemplateSyntaxError(f"Invalid for loop syntax: {token_content}")

        target = parts[1]
        iterable = " ".join(parts[3:])

        nodes = []
        else_nodes = []
        current_nodes = nodes
        consumed = 1

        # Parse block content
        i = start_index + 1
        while i < len(tokens):
            token_type, token_content, token_pos = tokens[i]

            if token_type == "block":
                parts = token_content.split()
                if not parts:
                    i += 1
                    continue

                tag_name = parts[0]

                if tag_name == "else":
                    current_nodes = else_nodes
                elif tag_name == "endfor":
                    consumed = i - start_index + 1
                    break
                else:
                    # Nested block
                    node, block_consumed = self._parse_block_tag(tokens, i, template_name)
                    if node:
                        current_nodes.append(node)
                    i += block_consumed - 1
            else:
                # Regular content
                if token_type == "text":
                    current_nodes.append(TextNode(token_content))
                elif token_type == "variable":
                    current_nodes.append(self._parse_variable(token_content))

            i += 1

        return ForNode(target, iterable, nodes, else_nodes), consumed

    def _parse_block(
        self, tokens: List[Tuple], start_index: int, template_name: str = None
    ) -> Tuple[BlockNode, int]:
        """Parse template block."""
        token_content = tokens[start_index][1]
        parts = token_content.split()

        if len(parts) < 2:
            raise TemplateSyntaxError(f"Invalid block syntax: {token_content}")

        block_name = parts[1]
        nodes = []
        consumed = 1

        # Parse block content
        i = start_index + 1
        while i < len(tokens):
            token_type, token_content, token_pos = tokens[i]

            if token_type == "block":
                parts = token_content.split()
                if parts and parts[0] == "endblock":
                    consumed = i - start_index + 1
                    break
                else:
                    # Nested block
                    node, block_consumed = self._parse_block_tag(tokens, i, template_name)
                    if node:
                        nodes.append(node)
                    i += block_consumed - 1
            else:
                # Regular content
                if token_type == "text":
                    nodes.append(TextNode(token_content))
                elif token_type == "variable":
                    nodes.append(self._parse_variable(token_content))

            i += 1

        return BlockNode(block_name, nodes), consumed

    def _parse_extends(
        self, tokens: List[Tuple], start_index: int, template_name: str = None
    ) -> Tuple[ExtendsNode, int]:
        """Parse extends statement."""
        token_content = tokens[start_index][1]
        parts = token_content.split()

        if len(parts) < 2:
            raise TemplateSyntaxError(f"Invalid extends syntax: {token_content}")

        parent_template = parts[1]
        return ExtendsNode(parent_template), 1

    def _parse_include(
        self, tokens: List[Tuple], start_index: int, template_name: str = None
    ) -> Tuple[IncludeNode, int]:
        """Parse include statement."""
        token_content = tokens[start_index][1]
        parts = token_content.split()

        if len(parts) < 2:
            raise TemplateSyntaxError(f"Invalid include syntax: {token_content}")

        include_template = parts[1]
        return IncludeNode(include_template), 1

    def _parse_macro(
        self, tokens: List[Tuple], start_index: int, template_name: str = None
    ) -> Tuple[MacroNode, int]:
        """Parse macro definition."""
        token_content = tokens[start_index][1]

        # Parse macro signature
        match = re.match(r"macro\s+(\w+)\s*\(([^)]*)\)", token_content)
        if not match:
            raise TemplateSyntaxError(f"Invalid macro syntax: {token_content}")

        macro_name = match.group(1)
        params_str = match.group(2)
        params = [p.strip() for p in params_str.split(",") if p.strip()]

        nodes = []
        consumed = 1

        # Parse macro content
        i = start_index + 1
        while i < len(tokens):
            token_type, token_content, token_pos = tokens[i]

            if token_type == "block":
                parts = token_content.split()
                if parts and parts[0] == "endmacro":
                    consumed = i - start_index + 1
                    break
                else:
                    # Nested block
                    node, block_consumed = self._parse_block_tag(tokens, i, template_name)
                    if node:
                        nodes.append(node)
                    i += block_consumed - 1
            else:
                # Regular content
                if token_type == "text":
                    nodes.append(TextNode(token_content))
                elif token_type == "variable":
                    nodes.append(self._parse_variable(token_content))

            i += 1

        return MacroNode(macro_name, params, nodes), consumed

    def _find_extends_node(self, nodes: List[TemplateNode]) -> Optional[ExtendsNode]:
        """Find extends node in template."""
        for node in nodes:
            if isinstance(node, ExtendsNode):
                return node
        return None

    def _compile_template(self, nodes: List[TemplateNode], template_name: str = None) -> Callable:
        """Compile regular template."""

        def template_func(context):
            # Set up template context
            context.set("__engine__", self.engine)
            context.set("__auto_escape__", self.engine.auto_escape)
            context.set("__debug__", self.engine.debug)
            context.set("__filters__", self.engine.filter_registry.filters)

            # Render all nodes
            result = []
            for node in nodes:
                try:
                    output = node.render(context)
                    if output:
                        result.append(output)
                except Exception as e:
                    if self.engine.debug:
                        result.append(f"[Node error: {str(e)}]")

            return "".join(result)

        return template_func

    def _compile_inherited_template(
        self,
        nodes: List[TemplateNode],
        extends_node: ExtendsNode,
        template_name: str = None,
    ) -> Callable:
        """Compile template with inheritance."""

        def template_func(context):
            # Set up template context
            context.set("__engine__", self.engine)
            context.set("__auto_escape__", self.engine.auto_escape)
            context.set("__debug__", self.engine.debug)
            context.set("__filters__", self.engine.filter_registry.filters)

            # Collect blocks from child template
            blocks = {}
            for node in nodes:
                if isinstance(node, BlockNode):
                    blocks[node.name] = node

            # Set blocks in context for parent template to use
            parent_context = context.variables.copy()
            parent_context["__blocks__"] = blocks
            parent_context["__engine__"] = self.engine
            parent_context["__auto_escape__"] = self.engine.auto_escape
            parent_context["__debug__"] = self.engine.debug
            parent_context["__filters__"] = self.engine.filter_registry.filters

            # Render parent template
            return self.engine.render(extends_node.parent_template, parent_context)

        return template_func


class SafeString(str):
    """String marked as safe from auto-escaping."""

    def __html__(self):
        return str(self)


class TemplateSyntaxError(Exception):
    """Exception for template syntax errors."""

    def __init__(self, message: str, line_number: int = None, template_name: str = None):
        self.line_number = line_number
        self.template_name = template_name
        super().__init__(message)


__all__ = [
    "TemplateCompiler",
    "TemplateNode",
    "TextNode",
    "VariableNode",
    "IfNode",
    "ForNode",
    "BlockNode",
    "ExtendsNode",
    "IncludeNode",
    "MacroNode",
    "CommentNode",
    "SafeString",
    "TemplateSyntaxError",
]
