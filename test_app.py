import pytest
from app import app, db, Todo

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

# Utility function
def create_todo(client, title="Test Todo"):
    return client.post("/api/todos", json={"title": title})

# ---------- REST API Tests ----------

def test_api_create_todo_success(client):
    response = create_todo(client)
    assert response.status_code == 201

def test_api_create_todo_fail(client):
    response = client.post("/api/todos", json={})
    assert response.status_code == 400

def test_api_get_all_todos(client):
    create_todo(client, "Task 1")
    response = client.get("/api/todos")
    assert response.status_code == 200
    assert len(response.get_json()) >= 1

def test_api_get_single_todo(client):
    todo_id = create_todo(client).get_json()["id"]
    response = client.get(f"/api/todos/{todo_id}")
    assert response.status_code == 200

def test_api_get_single_not_found(client):
    response = client.get("/api/todos/999")
    assert response.status_code == 404

def test_api_update_todo(client):
    todo_id = create_todo(client).get_json()["id"]
    response = client.put(f"/api/todos/{todo_id}", json={"title": "Updated", "complete": True})
    assert response.status_code == 200

def test_api_update_todo_not_found(client):
    response = client.put("/api/todos/999", json={"title": "Fail"})
    assert response.status_code == 404

def test_api_delete_todo(client):
    todo_id = create_todo(client).get_json()["id"]
    response = client.delete(f"/api/todos/{todo_id}")
    assert response.status_code == 200

def test_api_delete_todo_not_found(client):
    response = client.delete("/api/todos/999")
    assert response.status_code == 404

def test_api_mark_done(client):
    todo_id = create_todo(client).get_json()["id"]
    response = client.patch(f"/api/todos/{todo_id}/done")
    assert response.status_code == 200

def test_api_mark_done_not_found(client):
    response = client.patch("/api/todos/999/done")
    assert response.status_code == 404

def test_api_toggle_done(client):
    todo_id = create_todo(client).get_json()["id"]
    response = client.patch(f"/api/todos/{todo_id}/toggle")
    assert response.status_code == 200

def test_api_toggle_done_not_found(client):
    response = client.patch("/api/todos/999/toggle")
    assert response.status_code == 404

# ---------- HTML Route Tests ----------

def test_home_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"<html" in response.data.lower()

def test_add_todo_success(client):
    response = client.post("/add", data={"title": "Buy milk"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Buy milk" in response.data

def test_add_todo_empty_title(client):
    response = client.post("/add", data={"title": ""}, follow_redirects=True)
    assert response.status_code == 200
    assert b"cannot be empty" in response.data.lower()

def test_toggle_todo_route(client):
    client.post("/add", data={"title": "Walk dog"}, follow_redirects=True)
    todo = Todo.query.first()
    response = client.get(f"/toggle/{todo.id}", follow_redirects=True)
    assert response.status_code == 200

def test_toggle_todo_not_found(client):
    response = client.get("/toggle/999", follow_redirects=True)
    assert response.status_code == 404

def test_delete_todo_success(client):
    client.post("/add", data={"title": "Read book"}, follow_redirects=True)
    todo = Todo.query.first()
    response = client.get(f"/delete/{todo.id}", follow_redirects=True)
    assert response.status_code == 200
    assert b"deleted" in response.data.lower()

def test_delete_todo_not_found(client):
    response = client.get("/delete/999", follow_redirects=True)
    assert response.status_code == 200
    assert b"not found" in response.data.lower()
