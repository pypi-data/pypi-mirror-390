#!/usr/bin/env python3
"""
CovetPy Todo API Example

A complete REST API example showing CRUD operations.
Demonstrates routing, JSON handling, error responses, and data validation.

This example uses in-memory storage for simplicity (no database dependencies).

Run with:
    python examples/todo_api.py

Or with uvicorn:
    pip install uvicorn[standard]
    uvicorn examples.todo_api:app --reload

API Endpoints:
    GET    /todos          - List all todos
    POST   /todos          - Create a new todo
    GET    /todos/{id}     - Get a specific todo
    PUT    /todos/{id}     - Update a todo
    DELETE /todos/{id}     - Delete a todo
"""

import json
import time
from typing import Dict, List, Optional
from covet import CovetPy, Request, Response, CovetError


# In-memory storage (would be a database in real applications)
todos: Dict[int, dict] = {}
next_id = 1


def create_todo(title: str, description: str = "", completed: bool = False) -> dict:
    """Create a new todo item."""
    global next_id
    
    todo = {
        "id": next_id,
        "title": title,
        "description": description,
        "completed": completed,
        "created_at": time.time(),
        "updated_at": time.time()
    }
    
    todos[next_id] = todo
    next_id += 1
    
    return todo


def update_todo(todo_id: int, **updates) -> Optional[dict]:
    """Update an existing todo item."""
    if todo_id not in todos:
        return None
    
    todo = todos[todo_id]
    
    # Update fields
    for key, value in updates.items():
        if key in ["title", "description", "completed"]:
            todo[key] = value
    
    todo["updated_at"] = time.time()
    return todo


def validate_todo_data(data: dict) -> dict:
    """Validate todo data and return cleaned version."""
    if not isinstance(data, dict):
        raise CovetError("Request body must be a JSON object", status_code=400)
    
    # Required field
    if "title" not in data:
        raise CovetError("Title is required", status_code=400)
    
    title = data["title"]
    if not isinstance(title, str) or len(title.strip()) == 0:
        raise CovetError("Title must be a non-empty string", status_code=400)
    
    # Optional fields with defaults
    description = data.get("description", "")
    if not isinstance(description, str):
        description = str(description)
    
    completed = data.get("completed", False)
    if not isinstance(completed, bool):
        completed = bool(completed)
    
    return {
        "title": title.strip(),
        "description": description.strip(),
        "completed": completed
    }


# Create the application
app = CovetPy(debug=True)


# Add some sample todos
create_todo("Learn CovetPy", "Explore the zero-dependency Python web framework")
create_todo("Build an API", "Create a REST API using CovetPy", completed=True)
create_todo("Add middleware", "Implement custom middleware for logging")


@app.get("/")
async def api_info():
    """API information and usage."""
    return {
        "name": "CovetPy Todo API",
        "version": "1.0.0",
        "description": "A simple todo API built with CovetPy",
        "endpoints": {
            "GET /todos": "List all todos",
            "POST /todos": "Create a new todo",
            "GET /todos/{id}": "Get a specific todo",
            "PUT /todos/{id}": "Update a todo", 
            "DELETE /todos/{id}": "Delete a todo"
        },
        "example_todo": {
            "title": "Learn something new",
            "description": "Optional description",
            "completed": False
        }
    }


@app.get("/todos")
async def list_todos():
    """Get all todos."""
    todo_list = list(todos.values())
    return {
        "todos": todo_list,
        "count": len(todo_list),
        "completed": sum(1 for t in todo_list if t["completed"]),
        "pending": sum(1 for t in todo_list if not t["completed"])
    }


@app.post("/todos")
async def create_todo_endpoint(request: Request):
    """Create a new todo."""
    try:
        data = await request.json()
    except Exception:
        raise CovetError("Invalid JSON in request body", status_code=400)
    
    # Validate data
    clean_data = validate_todo_data(data)
    
    # Create todo
    todo = create_todo(**clean_data)
    
    return {
        "message": "Todo created successfully",
        "todo": todo
    }


@app.get("/todos/{todo_id}")
async def get_todo(todo_id: int):
    """Get a specific todo by ID."""
    if todo_id not in todos:
        raise CovetError(f"Todo with ID {todo_id} not found", status_code=404)
    
    return {"todo": todos[todo_id]}


@app.put("/todos/{todo_id}")
async def update_todo_endpoint(todo_id: int, request: Request):
    """Update a specific todo."""
    if todo_id not in todos:
        raise CovetError(f"Todo with ID {todo_id} not found", status_code=404)
    
    try:
        data = await request.json()
    except Exception:
        raise CovetError("Invalid JSON in request body", status_code=400)
    
    # Validate partial data (allow partial updates)
    updates = {}
    if "title" in data:
        if not isinstance(data["title"], str) or len(data["title"].strip()) == 0:
            raise CovetError("Title must be a non-empty string", status_code=400)
        updates["title"] = data["title"].strip()
    
    if "description" in data:
        updates["description"] = str(data["description"]).strip()
    
    if "completed" in data:
        updates["completed"] = bool(data["completed"])
    
    if not updates:
        raise CovetError("No valid fields to update", status_code=400)
    
    # Update todo
    updated_todo = update_todo(todo_id, **updates)
    
    return {
        "message": "Todo updated successfully",
        "todo": updated_todo
    }


@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    """Delete a specific todo."""
    if todo_id not in todos:
        raise CovetError(f"Todo with ID {todo_id} not found", status_code=404)
    
    deleted_todo = todos.pop(todo_id)
    
    return {
        "message": "Todo deleted successfully",
        "deleted_todo": deleted_todo
    }


@app.get("/stats")
async def todo_stats():
    """Get statistics about todos."""
    todo_list = list(todos.values())
    
    if not todo_list:
        return {
            "total": 0,
            "completed": 0,
            "pending": 0,
            "completion_rate": 0.0
        }
    
    completed = sum(1 for t in todo_list if t["completed"])
    pending = len(todo_list) - completed
    completion_rate = (completed / len(todo_list)) * 100
    
    return {
        "total": len(todo_list),
        "completed": completed,
        "pending": pending,
        "completion_rate": round(completion_rate, 2)
    }


if __name__ == "__main__":
    print("=" * 60)
    print("CovetPy Todo API Example")
    print("=" * 60)
    print("A complete REST API demonstrating CRUD operations.")
    print()
    print("Available endpoints:")
    print("  GET    /              - API information")
    print("  GET    /todos         - List all todos")
    print("  POST   /todos         - Create new todo")
    print("  GET    /todos/{id}    - Get specific todo")
    print("  PUT    /todos/{id}    - Update todo")
    print("  DELETE /todos/{id}    - Delete todo")
    print("  GET    /stats         - Todo statistics")
    print()
    print("Example requests:")
    print("  curl http://localhost:8000/todos")
    print("  curl -X POST -H 'Content-Type: application/json' \\")
    print("       -d '{\"title\": \"New task\", \"description\": \"Do something\"}' \\")
    print("       http://localhost:8000/todos")
    print("  curl -X PUT -H 'Content-Type: application/json' \\") 
    print("       -d '{\"completed\": true}' \\")
    print("       http://localhost:8000/todos/1")
    print("  curl -X DELETE http://localhost:8000/todos/1")
    print()
    
    try:
        app.run(host="127.0.0.1", port=8000)
    except Exception as e:
        print(f"Failed to start server: {e}")
        print("\nTo run this example:")
        print("1. Install uvicorn: pip install uvicorn[standard]")
        print("2. Run: python examples/todo_api.py")
        print("3. Or: uvicorn examples.todo_api:app --reload")