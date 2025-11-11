"""
ABAC Policy Examples

Demonstrates complex attribute-based access control policies.

Features:
- Subject, resource, action, environment attributes
- Complex policy rules
- Policy builder usage
- Time-based access
- Ownership-based access
"""

import asyncio
from datetime import datetime, time
from covet.security.authz import (
    ABACManager,
    PolicyBuilder,
    PolicyEffect,
    Operator,
)


async def create_basic_policies(abac: ABACManager):
    """Create basic ABAC policies."""
    print("Creating basic policies...")

    # Policy 1: Users can read their own documents
    await abac.create_policy(
        name="read-own-documents",
        effect=PolicyEffect.ALLOW,
        subject={"user_id": "${resource.owner}"},
        resource={"type": "document"},
        action=["read"],
        description="Users can read documents they own",
        priority=10
    )

    # Policy 2: Admins can do anything
    await abac.create_policy(
        name="admin-full-access",
        effect=PolicyEffect.ALLOW,
        subject={"role": "admin"},
        action=["read", "write", "delete"],
        description="Admins have full access",
        priority=100
    )

    # Policy 3: Engineering can access confidential docs
    await abac.create_policy(
        name="engineering-confidential-access",
        effect=PolicyEffect.ALLOW,
        subject={
            "department": "engineering",
            "clearance_level": {Operator.GTE: 3}
        },
        resource={"classification": "confidential"},
        action=["read"],
        description="Engineering with clearance >= 3 can read confidential docs",
        priority=50
    )

    print("Basic policies created!")


async def create_time_based_policies(abac: ABACManager):
    """Create time-based access policies."""
    print("\\nCreating time-based policies...")

    # Policy: Access only during business hours
    policy = (PolicyBuilder("business-hours-only")
        .allow()
        .when_subject(employee_type="contractor")
        .when_environment(
            business_hours=True  # Simplified - in production use time ranges
        )
        .for_actions(["read", "write"])
        .with_description("Contractors can only access during business hours")
        .with_priority(60)
        .build())

    await abac.create_policy(**policy)

    print("Time-based policies created!")


async def create_hierarchical_policies(abac: ABACManager):
    """Create policies with hierarchical conditions."""
    print("\\nCreating hierarchical policies...")

    # Policy: Managers can access reports from their department
    policy = (PolicyBuilder("manager-department-reports")
        .allow()
        .when_subject(
            role="manager",
            department="${resource.department}"
        )
        .when_resource(type="report")
        .for_actions(["read"])
        .with_description("Managers can read reports from their department")
        .with_priority(40)
        .build())

    await abac.create_policy(**policy)

    # Policy: Senior staff can access more resources
    policy = (PolicyBuilder("senior-staff-access")
        .allow()
        .when_subject(
            seniority_level={Operator.GTE: 5},
            department={Operator.IN: ["engineering", "product"]}
        )
        .when_resource(
            confidentiality={Operator.LTE: 2}
        )
        .for_actions(["read", "write"])
        .with_description("Senior staff can access lower confidentiality resources")
        .with_priority(45)
        .build())

    await abac.create_policy(**policy)

    print("Hierarchical policies created!")


async def create_deny_policies(abac: ABACManager):
    """Create explicit deny policies."""
    print("\\nCreating deny policies...")

    # Policy: Deny access to classified documents for interns
    policy = (PolicyBuilder("deny-interns-classified")
        .deny()
        .when_subject(employee_type="intern")
        .when_resource(classification="classified")
        .for_actions(["read", "write", "delete"])
        .with_description("Interns cannot access classified documents")
        .with_priority(90)  # High priority to override other allows
        .build())

    await abac.create_policy(**policy)

    # Policy: Deny deletions outside business hours
    policy = (PolicyBuilder("deny-after-hours-delete")
        .deny()
        .when_environment(business_hours=False)
        .for_actions(["delete"])
        .with_description("No deletions allowed outside business hours")
        .with_priority(85)
        .build())

    await abac.create_policy(**policy)

    print("Deny policies created!")


async def evaluate_policies(abac: ABACManager):
    """Evaluate various policy scenarios."""
    print("\\n" + "="*60)
    print("POLICY EVALUATION SCENARIOS")
    print("="*60)

    # Scenario 1: User accessing their own document
    print("\\n1. User accessing their own document:")
    allowed, reason, policy_id = await abac.evaluate_access(
        subject={"user_id": "user123", "role": "user"},
        resource={"type": "document", "owner": "user123"},
        action="read"
    )
    print(f"   Result: {'ALLOWED' if allowed else 'DENIED'}")
    print(f"   Reason: {reason}")

    # Scenario 2: User accessing someone else's document
    print("\\n2. User accessing someone else's document:")
    allowed, reason, policy_id = await abac.evaluate_access(
        subject={"user_id": "user123", "role": "user"},
        resource={"type": "document", "owner": "user456"},
        action="read"
    )
    print(f"   Result: {'ALLOWED' if allowed else 'DENIED'}")
    print(f"   Reason: {reason}")

    # Scenario 3: Admin accessing any document
    print("\\n3. Admin accessing any document:")
    allowed, reason, policy_id = await abac.evaluate_access(
        subject={"user_id": "admin001", "role": "admin"},
        resource={"type": "document", "owner": "user456"},
        action="delete"
    )
    print(f"   Result: {'ALLOWED' if allowed else 'DENIED'}")
    print(f"   Reason: {reason}")

    # Scenario 4: Engineering accessing confidential document
    print("\\n4. Engineering (clearance 5) accessing confidential document:")
    allowed, reason, policy_id = await abac.evaluate_access(
        subject={
            "user_id": "eng001",
            "role": "engineer",
            "department": "engineering",
            "clearance_level": 5
        },
        resource={
            "type": "document",
            "classification": "confidential",
            "department": "engineering"
        },
        action="read"
    )
    print(f"   Result: {'ALLOWED' if allowed else 'DENIED'}")
    print(f"   Reason: {reason}")

    # Scenario 5: Intern trying to access classified document (should be denied)
    print("\\n5. Intern trying to access classified document:")
    allowed, reason, policy_id = await abac.evaluate_access(
        subject={
            "user_id": "intern001",
            "role": "intern",
            "employee_type": "intern"
        },
        resource={
            "type": "document",
            "classification": "classified"
        },
        action="read"
    )
    print(f"   Result: {'ALLOWED' if allowed else 'DENIED'}")
    print(f"   Reason: {reason}")

    # Scenario 6: Manager accessing department report
    print("\\n6. Manager accessing department report:")
    allowed, reason, policy_id = await abac.evaluate_access(
        subject={
            "user_id": "mgr001",
            "role": "manager",
            "department": "engineering"
        },
        resource={
            "type": "report",
            "department": "engineering",
            "classification": "internal"
        },
        action="read"
    )
    print(f"   Result: {'ALLOWED' if allowed else 'DENIED'}")
    print(f"   Reason: {reason}")

    # Scenario 7: Senior staff accessing low confidentiality resource
    print("\\n7. Senior engineer accessing internal document:")
    allowed, reason, policy_id = await abac.evaluate_access(
        subject={
            "user_id": "senior001",
            "role": "senior_engineer",
            "department": "engineering",
            "seniority_level": 7
        },
        resource={
            "type": "document",
            "confidentiality": 1,
            "department": "engineering"
        },
        action="write"
    )
    print(f"   Result: {'ALLOWED' if allowed else 'DENIED'}")
    print(f"   Reason: {reason}")


async def demonstrate_complex_rules():
    """Demonstrate complex policy rules."""
    print("\\n" + "="*60)
    print("COMPLEX POLICY RULES")
    print("="*60)

    abac = ABACManager(enable_audit=False)

    # Complex policy with multiple conditions
    policy_dict = {
        "name": "complex-access-policy",
        "effect": PolicyEffect.ALLOW,
        "subject": {
            "department": {Operator.IN: ["engineering", "product", "design"]},
            "clearance_level": {Operator.GTE: 2},
            "employment_status": "active"
        },
        "resource": {
            "type": "design_document",
            "status": {Operator.NOT_IN: ["archived", "deleted"]},
            "shared": True
        },
        "action": ["read", "comment"],
        "environment": {
            "vpn_connected": True,
            "ip_range": "10.0.0.0/8"  # Internal network
        },
        "description": "Active employees from eng/product/design with clearance >= 2 can read shared design docs from VPN",
        "priority": 55
    }

    await abac.create_policy(**policy_dict)

    print("\\nComplex policy created with conditions:")
    print("   Subject: department IN [eng, product, design] AND clearance >= 2 AND active")
    print("   Resource: type=design_document AND status NOT IN [archived, deleted] AND shared=true")
    print("   Action: read OR comment")
    print("   Environment: vpn_connected=true AND ip_range=10.0.0.0/8")

    # Test the complex policy
    print("\\n1. Valid user with all conditions met:")
    allowed, reason, _ = await abac.evaluate_access(
        subject={
            "user_id": "user001",
            "department": "engineering",
            "clearance_level": 3,
            "employment_status": "active"
        },
        resource={
            "type": "design_document",
            "status": "published",
            "shared": True
        },
        action="read",
        environment={
            "vpn_connected": True,
            "ip_range": "10.0.0.0/8"
        }
    )
    print(f"   Result: {'ALLOWED' if allowed else 'DENIED'}")
    print(f"   Reason: {reason}")

    print("\\n2. User without VPN (should be denied):")
    allowed, reason, _ = await abac.evaluate_access(
        subject={
            "user_id": "user001",
            "department": "engineering",
            "clearance_level": 3,
            "employment_status": "active"
        },
        resource={
            "type": "design_document",
            "status": "published",
            "shared": True
        },
        action="read",
        environment={
            "vpn_connected": False,
            "ip_range": "203.0.113.0/24"  # External IP
        }
    )
    print(f"   Result: {'ALLOWED' if allowed else 'DENIED'}")
    print(f"   Reason: {reason}")


async def main():
    """Run ABAC policy examples."""
    print("="*60)
    print("ABAC POLICY EXAMPLES")
    print("="*60)

    # Create ABAC manager
    abac = ABACManager(enable_audit=True)

    # Create various policies
    await create_basic_policies(abac)
    await create_time_based_policies(abac)
    await create_hierarchical_policies(abac)
    await create_deny_policies(abac)

    # Evaluate policies
    await evaluate_policies(abac)

    # Complex rules
    await demonstrate_complex_rules()

    print("\\n" + "="*60)
    print("EXAMPLE COMPLETE!")
    print("="*60)


if __name__ == '__main__':
    asyncio.run(main())
