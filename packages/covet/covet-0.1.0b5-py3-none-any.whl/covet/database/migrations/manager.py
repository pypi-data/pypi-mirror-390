"""Migration manager."""

class MigrationManager:
    """Manage database migrations."""
    
    def __init__(self, db):
        self.db = db
        self.migrations = []
    
    def add_migration(self, migration):
        """Add a migration."""
        self.migrations.append(migration)
    
    async def run_migrations(self):
        """Run all pending migrations."""
        for migration in self.migrations:
            await migration.apply(self.db)

__all__ = ["MigrationManager", "MigrationExecutionReport"]



class MigrationPlan:
    """Migration execution plan."""
    def __init__(self):
        self.steps = []


# Auto-generated stubs for missing exports

class MigrationExecutionReport:
    """Stub class for MigrationExecutionReport."""

    def __init__(self, *args, **kwargs):
        pass

