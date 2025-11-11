
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from covet.core.app import create_zero_dependency_app
from covet.routing import create_router
from covet.server import run_server, ServerConfig

app = create_zero_dependency_app(force_zero_dependency=True)
router = create_router()

@router.get("/")
async def home(request):
    return app.json_response({"message": "Hello from CovetPy!"})

@router.get("/api/users")
async def list_users(request):
    return app.json_response({
        "users": [{"id": i, "name": f"User {i}"} for i in range(100)]
    })

@router.get("/api/users/{id}")
async def get_user(request):
    user_id = request.path_params.get("id")
    return app.json_response({
        "id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com"
    })

@router.post("/api/data")
async def process_data(request):
    data = await request.json()
    return app.json_response({
        "processed": True,
        "items": len(data.get("items", [])),
        "count": sum(data.get("items", []))
    })

app._router = router

if __name__ == "__main__":
    config = ServerConfig(
        host="127.0.0.1",
        port=8001,
        workers=1,
        max_connections=10000
    )
    print(f"CovetPy server starting on {config.host}:{config.port}")
    run_server(app, config=config)
