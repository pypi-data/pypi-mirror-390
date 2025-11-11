"""
Multi-Tenant Authorization Example

Demonstrates authorization in multi-tenant SaaS applications.

Features:
- Tenant isolation
- Tenant-scoped roles
- Cross-tenant access controls
- Hierarchical tenant structures
"""

import asyncio
from typing import Dict, List
from covet.security.authz import (
    RBACManager,
    PolicyDecisionPoint,
    DecisionStrategy,
    PermissionScope,
)


async def setup_tenants(rbac: RBACManager):
    """Setup multi-tenant structure."""
    print("Setting up multi-tenant structure...")

    # Create tenant-specific roles
    tenants = {
        "acme_corp": "ACME Corporation",
        "contoso_ltd": "Contoso Limited",
        "fabrikam_inc": "Fabrikam Inc"
    }

    for tenant_id, tenant_name in tenants.items():
        print(f"\\n  Setting up {tenant_name} ({tenant_id})...")

        # Tenant admin role
        await rbac.create_role(
            name=f"tenant_admin_{tenant_id}",
            display_name=f"Tenant Admin - {tenant_name}",
            description=f"Administrator for {tenant_name}",
            scope=PermissionScope.ORGANIZATION,
            priority=90
        )
        await rbac.assign_permission_to_role(
            f"tenant_admin_{tenant_id}",
            f"tenant:{tenant_id}:*"
        )

        # Tenant user role
        await rbac.create_role(
            name=f"tenant_user_{tenant_id}",
            display_name=f"User - {tenant_name}",
            description=f"Regular user for {tenant_name}",
            scope=PermissionScope.ORGANIZATION,
            priority=50
        )
        await rbac.assign_permission_to_role(
            f"tenant_user_{tenant_id}",
            f"tenant:{tenant_id}:read"
        )
        await rbac.assign_permission_to_role(
            f"tenant_user_{tenant_id}",
            f"tenant:{tenant_id}:write:own"
        )

    print("\\nTenant structure created!")


async def assign_users_to_tenants(rbac: RBACManager):
    """Assign users to various tenants."""
    print("\\nAssigning users to tenants...")

    # User 1: Admin of ACME Corp
    await rbac.assign_role_to_user(
        "alice@acme.com",
        "tenant_admin_acme_corp",
        scope=PermissionScope.ORGANIZATION,
        scope_id="acme_corp"
    )

    # User 2: User in ACME Corp
    await rbac.assign_role_to_user(
        "bob@acme.com",
        "tenant_user_acme_corp",
        scope=PermissionScope.ORGANIZATION,
        scope_id="acme_corp"
    )

    # User 3: Admin of Contoso
    await rbac.assign_role_to_user(
        "charlie@contoso.com",
        "tenant_admin_contoso_ltd",
        scope=PermissionScope.ORGANIZATION,
        scope_id="contoso_ltd"
    )

    # User 4: Multi-tenant user (consultant)
    await rbac.assign_role_to_user(
        "consultant@external.com",
        "tenant_user_acme_corp",
        scope=PermissionScope.ORGANIZATION,
        scope_id="acme_corp"
    )
    await rbac.assign_role_to_user(
        "consultant@external.com",
        "tenant_user_contoso_ltd",
        scope=PermissionScope.ORGANIZATION,
        scope_id="contoso_ltd"
    )

    # User 5: Platform admin (super admin across all tenants)
    await rbac.assign_role_to_user(
        "platform_admin@system.com",
        "admin",  # Global admin role
        scope=PermissionScope.GLOBAL
    )

    print("Users assigned!")


async def demonstrate_tenant_isolation(rbac: RBACManager):
    """Demonstrate tenant data isolation."""
    print("\\n" + "="*60)
    print("TENANT ISOLATION EXAMPLES")
    print("="*60)

    # ACME admin in their tenant
    print("\\n1. ACME Admin (alice@acme.com) in ACME tenant:")
    can_admin = await rbac.check_permission(
        "alice@acme.com",
        "tenant:acme_corp:manage",
        PermissionScope.ORGANIZATION,
        "acme_corp"
    )
    print(f"   - Can manage ACME tenant: {can_admin}")

    # ACME admin trying to access Contoso tenant
    print("\\n2. ACME Admin trying to access Contoso tenant:")
    can_admin_contoso = await rbac.check_permission(
        "alice@acme.com",
        "tenant:contoso_ltd:manage",
        PermissionScope.ORGANIZATION,
        "contoso_ltd"
    )
    print(f"   - Can manage Contoso tenant: {can_admin_contoso} (should be False)")

    # Regular user in their tenant
    print("\\n3. ACME User (bob@acme.com) in ACME tenant:")
    can_read = await rbac.check_permission(
        "bob@acme.com",
        "tenant:acme_corp:read",
        PermissionScope.ORGANIZATION,
        "acme_corp"
    )
    can_admin = await rbac.check_permission(
        "bob@acme.com",
        "tenant:acme_corp:manage",
        PermissionScope.ORGANIZATION,
        "acme_corp"
    )
    print(f"   - Can read in ACME tenant: {can_read}")
    print(f"   - Can manage ACME tenant: {can_admin} (should be False)")


async def demonstrate_multi_tenant_user(rbac: RBACManager):
    """Demonstrate user with access to multiple tenants."""
    print("\\n" + "="*60)
    print("MULTI-TENANT USER ACCESS")
    print("="*60)

    consultant_id = "consultant@external.com"

    # Get roles in different tenants
    acme_roles = await rbac.get_user_roles(
        consultant_id,
        PermissionScope.ORGANIZATION,
        "acme_corp"
    )
    contoso_roles = await rbac.get_user_roles(
        consultant_id,
        PermissionScope.ORGANIZATION,
        "contoso_ltd"
    )

    print(f"\\nConsultant ({consultant_id}) roles:")
    print(f"   - ACME Corp: {[r.display_name for r in acme_roles]}")
    print(f"   - Contoso Ltd: {[r.display_name for r in contoso_roles]}")

    # Check permissions in each tenant
    print("\\nPermissions in each tenant:")

    acme_read = await rbac.check_permission(
        consultant_id,
        "tenant:acme_corp:read",
        PermissionScope.ORGANIZATION,
        "acme_corp"
    )
    contoso_read = await rbac.check_permission(
        consultant_id,
        "tenant:contoso_ltd:read",
        PermissionScope.ORGANIZATION,
        "contoso_ltd"
    )

    print(f"   - Can read ACME data: {acme_read}")
    print(f"   - Can read Contoso data: {contoso_read}")


async def demonstrate_platform_admin(rbac: RBACManager):
    """Demonstrate platform-level admin access."""
    print("\\n" + "="*60)
    print("PLATFORM ADMIN ACCESS")
    print("="*60)

    platform_admin = "platform_admin@system.com"

    print(f"\\nPlatform Admin ({platform_admin}) access:")

    # Platform admin should have access to all tenants
    for tenant_id in ["acme_corp", "contoso_ltd", "fabrikam_inc"]:
        can_access = await rbac.check_permission(
            platform_admin,
            f"tenant:{tenant_id}:manage",
            PermissionScope.GLOBAL
        )
        print(f"   - Can manage {tenant_id}: {can_access}")


async def demonstrate_hierarchical_tenants(rbac: RBACManager):
    """Demonstrate hierarchical tenant structure."""
    print("\\n" + "="*60)
    print("HIERARCHICAL TENANT STRUCTURE")
    print("="*60)

    print("\\nSetting up parent-child tenant relationships...")

    # Create parent tenant (enterprise account)
    await rbac.create_role(
        name="enterprise_admin_acme",
        display_name="ACME Enterprise Admin",
        description="Admin for ACME enterprise account",
        scope=PermissionScope.ORGANIZATION,
        priority=95
    )
    await rbac.assign_permission_to_role(
        "enterprise_admin_acme",
        "enterprise:acme:*"
    )

    # Create child tenant roles (departments)
    departments = ["engineering", "sales", "marketing"]
    for dept in departments:
        await rbac.create_role(
            name=f"dept_admin_acme_{dept}",
            display_name=f"ACME {dept.title()} Admin",
            description=f"Admin for ACME {dept} department",
            scope=PermissionScope.PROJECT,
            priority=70,
            parent_role="enterprise_admin_acme"
        )
        await rbac.assign_permission_to_role(
            f"dept_admin_acme_{dept}",
            f"dept:acme:{dept}:*"
        )

    # Assign enterprise admin
    await rbac.assign_role_to_user(
        "enterprise_admin@acme.com",
        "enterprise_admin_acme",
        scope=PermissionScope.ORGANIZATION,
        scope_id="acme_corp"
    )

    # Assign department admin
    await rbac.assign_role_to_user(
        "eng_lead@acme.com",
        "dept_admin_acme_engineering",
        scope=PermissionScope.PROJECT,
        scope_id="acme_corp_engineering"
    )

    print("\\nEnterprise Admin access:")
    enterprise_can_manage = await rbac.check_permission(
        "enterprise_admin@acme.com",
        "enterprise:acme:manage",
        PermissionScope.ORGANIZATION,
        "acme_corp"
    )
    print(f"   - Can manage enterprise account: {enterprise_can_manage}")

    print("\\nDepartment Admin access:")
    dept_can_manage = await rbac.check_permission(
        "eng_lead@acme.com",
        "dept:acme:engineering:manage",
        PermissionScope.PROJECT,
        "acme_corp_engineering"
    )
    print(f"   - Can manage engineering department: {dept_can_manage}")


async def demonstrate_tenant_switching():
    """Demonstrate switching between tenant contexts."""
    print("\\n" + "="*60)
    print("TENANT CONTEXT SWITCHING")
    print("="*60)

    # Using Policy Decision Point for context-aware authorization
    pdp = PolicyDecisionPoint(strategy=DecisionStrategy.RBAC_FIRST)

    consultant_id = "consultant@external.com"

    print(f"\\nConsultant ({consultant_id}) accessing resources:")

    # Access ACME Corp resources
    print("\\n1. Accessing ACME Corp document:")
    acme_decision = await pdp.evaluate(
        user_id=consultant_id,
        resource_type="tenant",
        resource_id="acme_corp",
        action="read",
        scope=PermissionScope.ORGANIZATION,
        scope_id="acme_corp"
    )
    print(f"   - Decision: {'ALLOWED' if acme_decision.allowed else 'DENIED'}")
    print(f"   - Reason: {acme_decision.reason}")
    print(f"   - Time: {acme_decision.evaluation_time_ms:.2f}ms")

    # Access Contoso Ltd resources
    print("\\n2. Accessing Contoso Ltd document:")
    contoso_decision = await pdp.evaluate(
        user_id=consultant_id,
        resource_type="tenant",
        resource_id="contoso_ltd",
        action="read",
        scope=PermissionScope.ORGANIZATION,
        scope_id="contoso_ltd"
    )
    print(f"   - Decision: {'ALLOWED' if contoso_decision.allowed else 'DENIED'}")
    print(f"   - Reason: {contoso_decision.reason}")
    print(f"   - Time: {contoso_decision.evaluation_time_ms:.2f}ms")

    # Try to access Fabrikam (should be denied)
    print("\\n3. Accessing Fabrikam Inc document (no access):")
    fabrikam_decision = await pdp.evaluate(
        user_id=consultant_id,
        resource_type="tenant",
        resource_id="fabrikam_inc",
        action="read",
        scope=PermissionScope.ORGANIZATION,
        scope_id="fabrikam_inc"
    )
    print(f"   - Decision: {'ALLOWED' if fabrikam_decision.allowed else 'DENIED'}")
    print(f"   - Reason: {fabrikam_decision.reason}")


async def main():
    """Run multi-tenant authorization example."""
    print("="*60)
    print("MULTI-TENANT AUTHORIZATION EXAMPLE")
    print("="*60)

    # Setup RBAC manager
    rbac = RBACManager(enable_audit=True)

    # Setup tenants
    await setup_tenants(rbac)

    # Assign users
    await assign_users_to_tenants(rbac)

    # Demonstrate isolation
    await demonstrate_tenant_isolation(rbac)

    # Multi-tenant user
    await demonstrate_multi_tenant_user(rbac)

    # Platform admin
    await demonstrate_platform_admin(rbac)

    # Hierarchical tenants
    await demonstrate_hierarchical_tenants(rbac)

    # Context switching
    await demonstrate_tenant_switching()

    print("\\n" + "="*60)
    print("EXAMPLE COMPLETE!")
    print("="*60)
    print("\\nKey Takeaways:")
    print("  - Tenant isolation through scoped roles")
    print("  - Multi-tenant users with different roles per tenant")
    print("  - Platform admins with global access")
    print("  - Hierarchical tenant structures")
    print("  - Context-aware authorization")


if __name__ == '__main__':
    asyncio.run(main())
