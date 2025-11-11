"""
Real-World Data Migration Examples

Comprehensive examples demonstrating data migration patterns for common scenarios.

Examples:
1. Email normalization backfill
2. Status field migration
3. Data denormalization
4. JSON to structured fields
5. Deduplication
6. Historical data archival

Author: CovetPy Team 21
"""

from covet.database.orm.data_migrations import DataMigration, RunPython, RunSQL
from covet.database.orm.migration_operations import (
    CopyField, TransformField, PopulateField,
    SplitField, MergeFields, ConvertType, RenameValues
)


# Example 1: Email Normalization
class NormalizeUserEmails(DataMigration):
    """
    Normalize all user emails to lowercase and trim whitespace.

    Use case: Ensure consistent email storage before adding unique constraint.
    """

    dependencies = [('users', '0002_add_email_index')]

    def normalize_email(self, rows):
        """Normalize email addresses."""
        for row in rows:
            if row.get('email'):
                row['email'] = row['email'].lower().strip()
        return rows

    operations = [
        RunPython(
            table='users',
            transform=normalize_email,
            batch_size=1000,
            description="Normalize user emails to lowercase"
        )
    ]


# Example 2: Status Field Migration
class MigrateOrderStatus(DataMigration):
    """
    Migrate order status from numeric codes to string values.

    Old format: 0=pending, 1=processing, 2=completed, 3=cancelled
    New format: 'pending', 'in_progress', 'completed', 'cancelled'
    """

    operations = [
        RenameValues(
            table='orders',
            field='status',
            mapping={
                0: 'pending',
                1: 'in_progress',
                2: 'completed',
                3: 'cancelled'
            },
            reverse_mapping={
                'pending': 0,
                'in_progress': 1,
                'completed': 2,
                'cancelled': 3
            },
            description="Convert status codes to strings"
        )
    ]


# Example 3: Data Denormalization
class DenormalizeUserData(DataMigration):
    """
    Add denormalized fields for performance.

    Copy frequently accessed joined data to main table.
    """

    operations = [
        # Copy company name to users table
        RunSQL(
            sql="""
                UPDATE users u
                SET company_name = c.name
                FROM companies c
                WHERE u.company_id = c.id
            """,
            reverse_sql="UPDATE users SET company_name = NULL",
            description="Denormalize company name to users"
        ),

        # Add total order count
        RunSQL(
            sql="""
                UPDATE users u
                SET total_orders = (
                    SELECT COUNT(*) FROM orders o
                    WHERE o.user_id = u.id
                )
            """,
            description="Calculate total orders per user"
        )
    ]


# Example 4: JSON to Structured Fields
class MigrateSettingsToFields(DataMigration):
    """
    Extract JSON settings into individual database fields.

    Move from flexible JSON to typed columns for better querying.
    """

    def extract_settings(self, rows):
        """Extract settings from JSON to fields."""
        import json

        for row in rows:
            if row.get('settings'):
                try:
                    settings = json.loads(row['settings']) if isinstance(row['settings'], str) else row['settings']

                    row['email_notifications'] = settings.get('email_notifications', True)
                    row['theme'] = settings.get('theme', 'light')
                    row['language'] = settings.get('language', 'en')

                except (json.JSONDecodeError, TypeError):
                    # Keep defaults on error
                    row['email_notifications'] = True
                    row['theme'] = 'light'
                    row['language'] = 'en'

        return rows

    operations = [
        RunPython(
            table='user_preferences',
            transform=extract_settings,
            batch_size=500,
            description="Extract JSON settings to typed fields"
        )
    ]


# Example 5: Deduplication
class DeduplicateCustomers(DataMigration):
    """
    Remove duplicate customer records based on email.

    Keep the oldest record, merge related data.
    """

    async def forwards(self, adapter, model_manager=None):
        """Custom deduplication logic."""
        # Find duplicates
        duplicates_query = """
            SELECT email, MIN(id) as keep_id, ARRAY_AGG(id) as all_ids
            FROM customers
            GROUP BY email
            HAVING COUNT(*) > 1
        """

        duplicates = await adapter.fetch_all(duplicates_query)

        for dup in duplicates:
            keep_id = dup['keep_id']
            remove_ids = [id for id in dup['all_ids'] if id != keep_id]

            # Merge orders
            await adapter.execute("""
                UPDATE orders
                SET customer_id = $1
                WHERE customer_id = ANY($2)
            """, [keep_id, remove_ids])

            # Remove duplicates
            await adapter.execute("""
                DELETE FROM customers
                WHERE id = ANY($1)
            """, [remove_ids])


# Example 6: Split Name Fields
class SplitCustomerName(DataMigration):
    """
    Split full_name into first_name and last_name.

    Handle various name formats gracefully.
    """

    def split_name(self, full_name):
        """Split full name into components."""
        if not full_name:
            return [None, None]

        parts = full_name.strip().split(maxsplit=1)

        if len(parts) == 1:
            return [parts[0], None]
        elif len(parts) >= 2:
            return [parts[0], parts[1]]

        return [None, None]

    operations = [
        SplitField(
            table='customers',
            source_field='full_name',
            dest_fields=['first_name', 'last_name'],
            split_func=split_name,
            description="Split full_name into first and last"
        )
    ]


# Example 7: Populate Computed Fields
class PopulateProductMetrics(DataMigration):
    """
    Backfill computed metrics for products.

    Calculate and store frequently accessed aggregate data.
    """

    operations = [
        # Total revenue per product
        RunSQL(sql="""
            UPDATE products p
            SET total_revenue = (
                SELECT COALESCE(SUM(oi.quantity * oi.price), 0)
                FROM order_items oi
                WHERE oi.product_id = p.id
            )
        """),

        # Average rating
        RunSQL(sql="""
            UPDATE products p
            SET avg_rating = (
                SELECT COALESCE(AVG(rating), 0)
                FROM reviews r
                WHERE r.product_id = p.id
            )
        """),

        # Total reviews count
        RunSQL(sql="""
            UPDATE products p
            SET review_count = (
                SELECT COUNT(*)
                FROM reviews r
                WHERE r.product_id = p.id
            )
        """)
    ]


# Example 8: Type Conversion
class ConvertPriceToDecimal(DataMigration):
    """
    Convert price fields from float to proper decimal.

    Prevents rounding errors in financial calculations.
    """

    operations = [
        ConvertType(
            table='products',
            field='price',
            target_type=str,  # Convert to string first for Decimal
            converter=lambda v: f"{float(v):.2f}" if v is not None else "0.00",
            description="Convert price to decimal string"
        )
    ]


# Example 9: Batch Update with Progress
class UpdateLargeTableWithProgress(DataMigration):
    """
    Update large table with progress tracking.

    Useful for very large tables (millions of rows).
    """

    operations = [
        RunPython(
            table='events',
            transform=lambda rows: [
                {**r, 'processed': True, 'processed_at': 'NOW()'}
                for r in rows
            ],
            batch_size=5000,  # Larger batches for better performance
            where_clause='processed = FALSE',
            description="Mark events as processed"
        )
    ]


# Example 10: Complex Multi-Step Migration
class ComplexUserDataMigration(DataMigration):
    """
    Complex multi-step migration with dependencies.

    Demonstrates coordinated changes across multiple tables.
    """

    dependencies = [
        ('users', '0005_add_profile_fields'),
        ('companies', '0003_add_tier_field'),
    ]

    operations = [
        # Step 1: Normalize data
        TransformField(
            table='users',
            field='username',
            transform=lambda v: v.lower().strip() if v else None,
            description="Normalize usernames"
        ),

        # Step 2: Copy backup data
        CopyField(
            table='users',
            source_field='email',
            dest_field='email_backup',
            description="Backup email addresses"
        ),

        # Step 3: Transform emails
        TransformField(
            table='users',
            field='email',
            transform=lambda v: v.lower().strip() if v else None,
            description="Normalize email addresses"
        ),

        # Step 4: Populate defaults
        PopulateField(
            table='users',
            field='email_verified',
            value=False,
            where_clause='email_verified IS NULL',
            description="Set default email_verified"
        ),

        # Step 5: Update related data
        RunSQL(sql="""
            UPDATE user_profiles up
            SET updated_at = NOW()
            FROM users u
            WHERE up.user_id = u.id
                AND u.updated_at > up.updated_at
        """, description="Sync profile timestamps")
    ]


if __name__ == '__main__':
    print("Data Migration Examples")
    print("=" * 60)
    print()
    print("These examples demonstrate common data migration patterns.")
    print("Copy and adapt them for your specific use cases.")
    print()
    print("Available examples:")
    examples = [
        ("NormalizeUserEmails", "Email normalization"),
        ("MigrateOrderStatus", "Status field migration"),
        ("DenormalizeUserData", "Data denormalization"),
        ("MigrateSettingsToFields", "JSON to structured"),
        ("DeduplicateCustomers", "Deduplication"),
        ("SplitCustomerName", "Split name fields"),
        ("PopulateProductMetrics", "Computed fields"),
        ("ConvertPriceToDecimal", "Type conversion"),
        ("UpdateLargeTableWithProgress", "Large table update"),
        ("ComplexUserDataMigration", "Multi-step migration"),
    ]

    for i, (name, desc) in enumerate(examples, 1):
        print(f"{i:2}. {name:30} - {desc}")
