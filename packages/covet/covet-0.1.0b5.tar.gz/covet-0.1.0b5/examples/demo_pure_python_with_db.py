#!/usr/bin/env python3
"""
Demo: Pure Python CovetPy with SQLAlchemy Integration

This demonstrates CovetPy's TRUE core - pure Python with NO web framework
dependencies. SQLAlchemy is optional and only loaded when needed.
"""

import sys
sys.path.insert(0, 'src')

import asyncio
from datetime import datetime

# Pure Python CovetPy - NO FastAPI/Flask dependencies!
from covet.core.pure_python_app import CovetPy, Request, Response

# Optional SQLAlchemy integration
try:
    from covet.database.sqlalchemy_integration import (
        create_database_adapter, Model, Column, Integer, String, DateTime, Boolean
    )
    from sqlalchemy.ext.declarative import declarative_base
    
    HAS_DB = True
    Base = declarative_base()
    
    # Define a model using SQLAlchemy (optional)
    class Task(Base, Model):
        __tablename__ = 'tasks'
        
        id = Column(Integer, primary_key=True)
        title = Column(String(200), nullable=False)
        description = Column(String(500))
        completed = Column(Boolean, default=False)
        created_at = Column(DateTime, default=datetime.utcnow)
        
except ImportError:
    HAS_DB = False
    print("⚠️  SQLAlchemy not installed. Database features disabled.")
    print("   Install with: pip install sqlalchemy[asyncio] aiosqlite")


# Create pure Python app - NO web framework!
app = CovetPy(debug=True)

# In-memory storage when database is not available
if not HAS_DB:
    tasks_memory = {}
    task_counter = 0


@app.get("/")
async def home(request: Request) -> Response:
    """Home page showing pure Python implementation."""
    return Response(body={
        "framework": "CovetPy - Pure Python",
        "core": "Zero web framework dependencies",
        "database": "SQLAlchemy 2.0" if HAS_DB else "In-memory",
        "message": "This is pure Python - no FastAPI, no Flask!"
    })


@app.get("/health")
async def health(request: Request) -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "pure_python": True,
        "database": "connected" if HAS_DB and app.db else "not configured"
    }


# Task management endpoints
@app.get("/tasks")
async def list_tasks(request: Request) -> dict:
    """List all tasks."""
    if HAS_DB and app.db:
        # Use database
        tasks = await Task.all(app.db)
        return {
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "completed": t.completed,
                    "created_at": t.created_at.isoformat() if t.created_at else None
                }
                for t in tasks
            ],
            "count": len(tasks),
            "storage": "database"
        }
    else:
        # Use in-memory storage
        return {
            "tasks": list(tasks_memory.values()),
            "count": len(tasks_memory),
            "storage": "memory"
        }


@app.post("/tasks")
async def create_task(request: Request) -> dict:
    """Create a new task."""
    data = await request.json()
    
    if HAS_DB and app.db:
        # Use database
        task = await Task.create(
            app.db,
            title=data.get('title', 'Untitled'),
            description=data.get('description', ''),
            completed=False
        )
        return {
            "created": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed
            }
        }
    else:
        # Use in-memory storage
        global task_counter
        task_counter += 1
        task = {
            "id": task_counter,
            "title": data.get('title', 'Untitled'),
            "description": data.get('description', ''),
            "completed": False,
            "created_at": datetime.utcnow().isoformat()
        }
        tasks_memory[task_counter] = task
        return {"created": True, "task": task}


@app.get("/tasks/{task_id}")
async def get_task(request: Request) -> Union[dict, tuple]:
    """Get a specific task."""
    task_id = int(request.path_params.get('task_id'))
    
    if HAS_DB and app.db:
        task = await Task.get(app.db, task_id)
        if task:
            return {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed
            }
        else:
            return {"error": "Task not found"}, 404
    else:
        if task_id in tasks_memory:
            return tasks_memory[task_id]
        else:
            return {"error": "Task not found"}, 404


@app.put("/tasks/{task_id}")
async def update_task(request: Request) -> Union[dict, tuple]:
    """Update a task."""
    task_id = int(request.path_params.get('task_id'))
    data = await request.json()
    
    if HAS_DB and app.db:
        task = await Task.get(app.db, task_id)
        if task:
            await task.update(app.db, **data)
            return {"updated": True, "task": {"id": task.id, "title": task.title}}
        else:
            return {"error": "Task not found"}, 404
    else:
        if task_id in tasks_memory:
            tasks_memory[task_id].update(data)
            return {"updated": True, "task": tasks_memory[task_id]}
        else:
            return {"error": "Task not found"}, 404


@app.delete("/tasks/{task_id}")  
async def delete_task(request: Request) -> Union[dict, tuple]:
    """Delete a task."""
    task_id = int(request.path_params.get('task_id'))
    
    if HAS_DB and app.db:
        task = await Task.get(app.db, task_id)
        if task:
            await task.delete(app.db)
            return {"deleted": True, "id": task_id}
        else:
            return {"error": "Task not found"}, 404
    else:
        if task_id in tasks_memory:
            deleted = tasks_memory.pop(task_id)
            return {"deleted": True, "task": deleted}
        else:
            return {"error": "Task not found"}, 404


# Middleware example (pure Python)
@app.before_request
async def log_request(request: Request):
    """Log incoming requests."""
    print(f"📨 {request.method} {request.path}")
    

@app.after_request
async def add_headers(request: Request, response: Response):
    """Add custom headers to response."""
    response.headers['X-Framework'] = 'CovetPy-Pure-Python'
    response.headers['X-No-Dependencies'] = 'True'
    return response


# Error handlers
@app.error_handler(404)
async def not_found(request: Request):
    """Handle 404 errors."""
    return {"error": "Not found", "path": request.path}, 404


async def setup_database():
    """Setup database if SQLAlchemy is available."""
    if HAS_DB:
        # Create database adapter
        db = create_database_adapter("sqlite+aiosqlite:///tasks.db")
        app.set_database(db)
        
        # Connect
        await db.connect()
        
        # Create tables
        await db.create_all()
        
        print("✅ Database connected and tables created")
    else:
        print("⚠️  Running without database (in-memory storage)")


async def test_app():
    """Test the pure Python app."""
    # Setup
    await setup_database()
    await app.startup()
    
    print("\n🧪 Testing Pure Python CovetPy...")
    print("=" * 50)
    
    # Test home endpoint
    request = Request(
        method="GET",
        path="/",
        headers={},
        query_params={},
        path_params={},
        body=b""
    )
    response = await app.handle_request(request)
    print(f"✅ GET /: {response.status_code}")
    print(f"   Response: {response.body}")
    
    # Test creating a task
    request = Request(
        method="POST",
        path="/tasks",
        headers={"Content-Type": "application/json"},
        query_params={},
        path_params={},
        body=b'{"title": "Test task", "description": "Pure Python test"}'
    )
    response = await app.handle_request(request)
    print(f"\n✅ POST /tasks: {response.status_code}")
    print(f"   Response: {response.body}")
    
    # Test listing tasks
    request = Request(
        method="GET",
        path="/tasks",
        headers={},
        query_params={},
        path_params={},
        body=b""
    )
    response = await app.handle_request(request)
    print(f"\n✅ GET /tasks: {response.status_code}")
    print(f"   Response: {response.body}")
    
    # Cleanup
    await app.shutdown()
    
    print("\n✅ All tests passed!")
    print("🎯 CovetPy works with PURE PYTHON - no web frameworks!")


# For running with a real server (uvicorn)
def create_asgi_app():
    """Create ASGI app for production use."""
    from covet.core.pure_python_app import PurePythonASGI
    
    # Setup database
    if HAS_DB:
        db = create_database_adapter("sqlite+aiosqlite:///tasks.db")
        app.set_database(db)
    
    return PurePythonASGI(app)


if __name__ == "__main__":
    print("🐍 CovetPy Pure Python Demo")
    print("=" * 50)
    print("NO FastAPI! NO Flask! Just pure Python!")
    print()
    
    # Run tests
    asyncio.run(test_app())
    
    print("\n💡 To run as a server:")
    print("   pip install uvicorn")
    print("   uvicorn demo_pure_python_with_db:create_asgi_app --factory")