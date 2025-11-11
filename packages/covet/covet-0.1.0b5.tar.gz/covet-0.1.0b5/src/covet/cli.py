"""
Covet CLI - Command-line interface for Covet framework

Provides commands for:
- Running development server
- Database migrations
- Project scaffolding
- Testing utilities
"""

import sys
import argparse
from typing import Optional, List


def print_banner() -> None:
    """Print Covet banner"""
    print("""
 ██████╗ ██████╗ ██╗   ██╗███████╗████████╗
██╔════╝██╔═══██╗██║   ██║██╔════╝╚══██╔══╝
██║     ██║   ██║██║   ██║█████╗     ██║
██║     ██║   ██║╚██╗ ██╔╝██╔══╝     ██║
╚██████╗╚██████╔╝ ╚████╔╝ ███████╗   ██║
 ╚═════╝ ╚═════╝   ╚═══╝  ╚══════╝   ╚═╝

    Modern Python Web Framework v{version}
    """.format(version=get_version()))


def get_version() -> str:
    """Get Covet version"""
    try:
        from covet import __version__
        return __version__
    except ImportError:
        return "unknown"


def cmd_version(args: argparse.Namespace) -> int:
    """Show version information"""
    from covet import __version__, __description__

    print(f"Covet version {__version__}")
    print(f"{__description__}")
    print()
    print("Python: ", sys.version)
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    """Run development server"""
    try:
        import uvicorn
    except ImportError:
        print("Error: uvicorn is required to run the development server")
        print("Install it with: pip install uvicorn")
        return 1

    app_path = args.app or "main:app"
    host = args.host or "127.0.0.1"
    port = args.port or 8000
    reload = args.reload

    print(f"Starting Covet development server...")
    print(f"Application: {app_path}")
    print(f"Listening on: http://{host}:{port}")
    print(f"Reload: {'enabled' if reload else 'disabled'}")
    print()
    print("Press CTRL+C to stop")

    try:
        uvicorn.run(
            app_path,
            host=host,
            port=port,
            reload=reload,
            log_level="info",
        )
        return 0
    except KeyboardInterrupt:
        print("\nServer stopped")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_new(args: argparse.Namespace) -> int:
    """Create new Covet project"""
    project_name = args.name

    print(f"Creating new Covet project: {project_name}")
    print("This feature is coming soon!")
    print()
    print("For now, start with:")
    print("""
from covet import Covet

app = Covet()

@app.route('/')
async def index(request):
    return {'message': 'Hello World'}

if __name__ == '__main__':
    app.run()
    """)
    return 0


def cmd_init_db(args: argparse.Namespace) -> int:
    """Initialize database"""
    print("Initializing database...")
    print("This feature is coming soon!")
    print()
    print("For now, use:")
    print("""
from covet.database import DatabaseManager, SQLiteAdapter

adapter = SQLiteAdapter(database_path='app.db')
db = DatabaseManager(adapter)
await db.connect()
    """)
    return 0


def cmd_migrate(args: argparse.Namespace) -> int:
    """Run database migrations"""
    print("Running migrations...")
    print("This feature is coming soon!")
    return 0


def cmd_test(args: argparse.Namespace) -> int:
    """Run tests"""
    try:
        import pytest
    except ImportError:
        print("Error: pytest is required to run tests")
        print("Install it with: pip install pytest")
        return 1

    print("Running tests...")
    return pytest.main(args.args or [])


def cmd_shell(args: argparse.Namespace) -> int:
    """Start interactive shell"""
    print("Starting interactive Python shell...")
    print("This feature is coming soon!")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="covet",
        description="Covet - Modern Python Web Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {get_version()}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # version command
    version_parser = subparsers.add_parser("version", help="Show version information")
    version_parser.set_defaults(func=cmd_version)

    # run command
    run_parser = subparsers.add_parser("run", help="Run development server")
    run_parser.add_argument(
        "app",
        nargs="?",
        help="Application path (e.g., main:app)",
    )
    run_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)",
    )
    run_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)",
    )
    run_parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload",
    )
    run_parser.set_defaults(func=cmd_run)

    # new command
    new_parser = subparsers.add_parser("new", help="Create new project")
    new_parser.add_argument("name", help="Project name")
    new_parser.set_defaults(func=cmd_new)

    # init-db command
    initdb_parser = subparsers.add_parser("init-db", help="Initialize database")
    initdb_parser.set_defaults(func=cmd_init_db)

    # migrate command
    migrate_parser = subparsers.add_parser("migrate", help="Run database migrations")
    migrate_parser.set_defaults(func=cmd_migrate)

    # test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Arguments to pass to pytest",
    )
    test_parser.set_defaults(func=cmd_test)

    # shell command
    shell_parser = subparsers.add_parser("shell", help="Start interactive shell")
    shell_parser.set_defaults(func=cmd_shell)

    # Parse arguments
    args = parser.parse_args(argv)

    # Show help if no command provided
    if not args.command:
        print_banner()
        parser.print_help()
        return 0

    # Execute command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
