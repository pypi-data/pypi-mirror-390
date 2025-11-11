"""
RBAC-Protected API Example

Demonstrates using RBAC to protect REST API endpoints with roles and permissions.

Features:
- Role-based endpoint protection
- Permission decorators
- Multi-tenant role assignments
- Admin override capabilities
"""

import asyncio
from typing import Dict, Any, List
from covet.security.authz import (
    RBACManager,
    initialize_default_roles,
    require_permission,
    require_role,
    AuthorizationMiddleware,
)


async def setup_rbac_system():
    """Setup RBAC system with roles and permissions."""
    rbac = RBACManager(enable_audit=True)

    # Initialize default roles (admin, user, guest)
    await initialize_default_roles(rbac)

    # Create custom roles
    print("Creating custom roles...")

    # Editor role - can manage content
    await rbac.create_role(
        name="editor",
        display_name="Content Editor",
        description="Can create and edit content",
        priority=60
    )
    await rbac.assign_permission_to_role("editor", "posts:read")
    await rbac.assign_permission_to_role("editor", "posts:write")
    await rbac.assign_permission_to_role("editor", "posts:create")

    # Moderator role - can moderate content
    await rbac.create_role(
        name="moderator",
        display_name="Content Moderator",
        description="Can moderate and delete content",
        priority=70,
        parent_role="editor"  # Inherits editor permissions
    )
    await rbac.assign_permission_to_role("moderator", "posts:delete")
    await rbac.assign_permission_to_role("moderator", "comments:delete")

    # Organization admin role
    await rbac.create_role(
        name="org_admin",
        display_name="Organization Administrator",
        description="Manages organization",
        priority=80
    )
    await rbac.assign_permission_to_role("org_admin", "org:*")

    print("Roles created successfully!")
    return rbac


async def setup_users(rbac: RBACManager):
    """Assign roles to users."""
    print("\\nAssigning roles to users...")

    # User 1: Regular editor
    await rbac.assign_role_to_user(
        user_id="user123",
        role_name="editor",
        granted_by="admin"
    )

    # User 2: Moderator in organization
    await rbac.assign_role_to_user(
        user_id="user456",
        role_name="moderator",
        scope="organization",
        scope_id="org_acme",
        granted_by="admin"
    )

    # User 3: Global admin
    await rbac.assign_role_to_user(
        user_id="admin001",
        role_name="admin",
        granted_by="system"
    )

    # User 4: Organization admin
    await rbac.assign_role_to_user(
        user_id="user789",
        role_name="org_admin",
        scope="organization",
        scope_id="org_acme",
        granted_by="admin"
    )

    print("Users assigned successfully!")


async def check_permissions(rbac: RBACManager):
    """Demonstrate permission checking."""
    print("\\n" + "="*60)
    print("PERMISSION CHECKING EXAMPLES")
    print("="*60)

    # Check editor permissions
    print("\\n1. Editor (user123) permissions:")
    can_read = await rbac.check_permission("user123", "posts:read")
    can_write = await rbac.check_permission("user123", "posts:write")
    can_delete = await rbac.check_permission("user123", "posts:delete")

    print(f"   - Can read posts: {can_read}")
    print(f"   - Can write posts: {can_write}")
    print(f"   - Can delete posts: {can_delete}")

    # Check moderator permissions (inherits from editor)
    print("\\n2. Moderator (user456) permissions:")
    can_read = await rbac.check_permission("user456", "posts:read", "organization", "org_acme")
    can_write = await rbac.check_permission("user456", "posts:write", "organization", "org_acme")
    can_delete = await rbac.check_permission("user456", "posts:delete", "organization", "org_acme")

    print(f"   - Can read posts: {can_read}")
    print(f"   - Can write posts: {can_write}")
    print(f"   - Can delete posts: {can_delete} (via moderator role)")

    # Check admin permissions (wildcard)
    print("\\n3. Admin (admin001) permissions:")
    can_do_anything = await rbac.check_permission("admin001", "posts:delete")
    can_manage_users = await rbac.check_permission("admin001", "users:delete")
    print(f"   - Can delete posts: {can_do_anything}")
    print(f"   - Can manage users: {can_manage_users}")

    # Check organization admin
    print("\\n4. Org Admin (user789) permissions:")
    can_manage_org = await rbac.check_permission(
        "user789", "org:manage", "organization", "org_acme"
    )
    print(f"   - Can manage organization: {can_manage_org}")


# Mock request object for decorator examples
class MockRequest:
    """Mock request for demonstration."""

    def __init__(self, user: Dict[str, Any]):
        self.user = user
        self.scope = {'user': user}


# Example API endpoints using decorators
@require_permission('posts:read')
async def get_posts(request: MockRequest) -> List[Dict[str, Any]]:
    """Get all posts - requires 'posts:read' permission."""
    return [
        {"id": 1, "title": "First Post", "author": "Alice"},
        {"id": 2, "title": "Second Post", "author": "Bob"},
    ]


@require_permission('posts:write')
async def create_post(request: MockRequest, title: str, content: str) -> Dict[str, Any]:
    """Create post - requires 'posts:write' permission."""
    return {
        "id": 3,
        "title": title,
        "content": content,
        "author": request.user['id']
    }


@require_permission('posts:delete')
async def delete_post(request: MockRequest, post_id: int) -> Dict[str, str]:
    """Delete post - requires 'posts:delete' permission."""
    return {"status": "deleted", "post_id": post_id}


@require_role('admin', 'moderator')
async def moderate_content(request: MockRequest, content_id: int) -> Dict[str, str]:
    """Moderate content - requires admin or moderator role."""
    return {
        "status": "moderated",
        "content_id": content_id,
        "moderated_by": request.user['id']
    }


async def demonstrate_decorators(rbac: RBACManager):
    """Demonstrate decorator-based authorization."""
    print("\\n" + "="*60)
    print("DECORATOR-BASED AUTHORIZATION")
    print("="*60)

    # Get user permissions
    editor_perms = await rbac.get_user_permissions("user123")
    moderator_perms = await rbac.get_user_permissions("user456", "organization", "org_acme")
    moderator_roles = await rbac.get_user_roles("user456", "organization", "org_acme")

    # Create mock requests
    editor_request = MockRequest({
        'id': 'user123',
        'permissions': list(editor_perms),
        'roles': ['editor']
    })

    moderator_request = MockRequest({
        'id': 'user456',
        'permissions': list(moderator_perms),
        'roles': [role.name for role in moderator_roles]
    })

    # Test endpoints
    print("\\n1. Editor accessing endpoints:")
    try:
        posts = await get_posts(editor_request)
        print(f"   ✓ GET /posts: Success ({len(posts)} posts)")
    except Exception as e:
        print(f"   ✗ GET /posts: Failed - {e}")

    try:
        post = await create_post(editor_request, "New Post", "Content here")
        print(f"   ✓ POST /posts: Success (created post {post['id']})")
    except Exception as e:
        print(f"   ✗ POST /posts: Failed - {e}")

    try:
        result = await delete_post(editor_request, 1)
        print(f"   ✓ DELETE /posts/1: Success")
    except Exception as e:
        print(f"   ✗ DELETE /posts/1: Failed - {e}")

    print("\\n2. Moderator accessing endpoints:")
    try:
        result = await delete_post(moderator_request, 1)
        print(f"   ✓ DELETE /posts/1: Success")
    except Exception as e:
        print(f"   ✗ DELETE /posts/1: Failed - {e}")

    try:
        result = await moderate_content(moderator_request, 42)
        print(f"   ✓ POST /moderate/42: Success")
    except Exception as e:
        print(f"   ✗ POST /moderate/42: Failed - {e}")


async def demonstrate_multi_tenant(rbac: RBACManager):
    """Demonstrate multi-tenant authorization."""
    print("\\n" + "="*60)
    print("MULTI-TENANT AUTHORIZATION")
    print("="*60)

    # User in multiple organizations
    print("\\n1. Setting up multi-tenant user...")

    # Assign roles in different organizations
    await rbac.assign_role_to_user(
        "user_multi",
        "editor",
        scope="organization",
        scope_id="org_alpha",
        granted_by="admin"
    )

    await rbac.assign_role_to_user(
        "user_multi",
        "moderator",
        scope="organization",
        scope_id="org_beta",
        granted_by="admin"
    )

    print("   User 'user_multi' assigned to:")
    print("   - Editor in org_alpha")
    print("   - Moderator in org_beta")

    # Check permissions in different scopes
    print("\\n2. Checking permissions in different organizations:")

    # In org_alpha (editor)
    can_write_alpha = await rbac.check_permission(
        "user_multi", "posts:write", "organization", "org_alpha"
    )
    can_delete_alpha = await rbac.check_permission(
        "user_multi", "posts:delete", "organization", "org_alpha"
    )

    print(f"   Org Alpha:")
    print(f"   - Can write posts: {can_write_alpha}")
    print(f"   - Can delete posts: {can_delete_alpha}")

    # In org_beta (moderator)
    can_write_beta = await rbac.check_permission(
        "user_multi", "posts:write", "organization", "org_beta"
    )
    can_delete_beta = await rbac.check_permission(
        "user_multi", "posts:delete", "organization", "org_beta"
    )

    print(f"   Org Beta:")
    print(f"   - Can write posts: {can_write_beta}")
    print(f"   - Can delete posts: {can_delete_beta}")


async def show_cache_performance(rbac: RBACManager):
    """Demonstrate cache performance."""
    print("\\n" + "="*60)
    print("CACHE PERFORMANCE")
    print("="*60)

    import time

    # First check (uncached)
    start = time.time()
    for _ in range(1000):
        await rbac.check_permission("user123", "posts:read")
    elapsed1 = (time.time() - start) * 1000

    # Second check (cached)
    start = time.time()
    for _ in range(1000):
        await rbac.check_permission("user123", "posts:read")
    elapsed2 = (time.time() - start) * 1000

    print(f"\\n1000 permission checks:")
    print(f"   - First run: {elapsed1:.2f}ms")
    print(f"   - Second run (cached): {elapsed2:.2f}ms")
    print(f"   - Speedup: {elapsed1/elapsed2:.1f}x")

    # Show cache stats
    cache_stats = rbac.get_cache_stats()
    print(f"\\nCache Statistics:")
    print(f"   {cache_stats}")


async def main():
    """Run RBAC API example."""
    print("="*60)
    print("RBAC-PROTECTED API EXAMPLE")
    print("="*60)

    # Setup RBAC system
    rbac = await setup_rbac_system()

    # Setup users
    await setup_users(rbac)

    # Check permissions
    await check_permissions(rbac)

    # Demonstrate decorators
    await demonstrate_decorators(rbac)

    # Multi-tenant authorization
    await demonstrate_multi_tenant(rbac)

    # Cache performance
    await show_cache_performance(rbac)

    print("\\n" + "="*60)
    print("EXAMPLE COMPLETE!")
    print("="*60)


if __name__ == '__main__':
    asyncio.run(main())
