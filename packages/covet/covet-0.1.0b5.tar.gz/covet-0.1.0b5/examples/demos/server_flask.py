
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "Hello from Flask!"})

@app.route("/api/users")
def list_users():
    return jsonify({"users": [{"id": i, "name": f"User {i}"} for i in range(100)]})

@app.route("/api/users/<int:user_id>")
def get_user(user_id):
    return jsonify({
        "id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com"
    })

@app.route("/api/data", methods=["POST"])
def process_data():
    data = request.get_json()
    return jsonify({
        "processed": True,
        "items": len(data.get("items", [])),
        "count": sum(data.get("items", []))
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8003, debug=False)
