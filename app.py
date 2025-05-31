from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)
    due_date = db.Column(db.Date)

@app.route("/")
def home():
    # ✅ Sort by due date, nulls (None) last
    todo_list = Todo.query.order_by(Todo.due_date.asc().nullslast()).all()
    return render_template("base.html", todo_list=todo_list)

@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    due_date_str = request.form.get("due_date")

    if not title or title.strip() == "":
        flash("Todo title cannot be empty.", "warning")
        return redirect(url_for("home"))

    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid due date format.", "warning")
            return redirect(url_for("home"))

    new_todo = Todo(title=title.strip(), complete=False, due_date=due_date)
    db.session.add(new_todo)
    db.session.commit()
    flash(f'Todo "{title}" added.', "success")
    return redirect(url_for("home"))

@app.route("/toggle/<int:todo_id>")
def toggle(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.complete = not todo.complete
    db.session.commit()
    flash(f'Todo "{todo.title}" toggled to {"done" if todo.complete else "not done"}.', "info")
    return redirect(url_for("home"))

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    if todo:
        db.session.delete(todo)
        db.session.commit()
        flash(f'Todo "{todo.title}" deleted.', "error")
    else:
        flash("Todo not found.", "error")
    return redirect(url_for("home"))

# -----------------------
# REST API ENDPOINTS
# -----------------------

@app.route("/api/todos", methods=["GET"])
def api_get_todos():
    todos = Todo.query.order_by(Todo.due_date.asc().nullslast()).all()
    return jsonify([
        {
            "id": t.id,
            "title": t.title,
            "complete": t.complete,
            "due_date": t.due_date.strftime("%Y-%m-%d") if t.due_date else None
        } for t in todos
    ]), 200

@app.route("/api/todos/<int:todo_id>", methods=["GET"])
def api_get_single_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    return jsonify({
        "id": todo.id,
        "title": todo.title,
        "complete": todo.complete,
        "due_date": todo.due_date.strftime("%Y-%m-%d") if todo.due_date else None
    }), 200

@app.route("/api/todos", methods=["POST"])
def api_create_todo():
    data = request.get_json()
    title = data.get("title")
    due_date_str = data.get("due_date")

    if not title:
        return jsonify({"error": "Title is required"}), 400

    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid due_date format. Use YYYY-MM-DD"}), 400

    new_todo = Todo(title=title, complete=False, due_date=due_date)
    db.session.add(new_todo)
    db.session.commit()
    return jsonify({"message": "Todo created", "id": new_todo.id}), 201

@app.route("/api/todos/<int:todo_id>", methods=["PUT"])
def api_update_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    data = request.get_json()
    todo.title = data.get("title", todo.title)
    todo.complete = data.get("complete", todo.complete)

    due_date_str = data.get("due_date")
    if due_date_str is not None:
        try:
            todo.due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid due_date format. Use YYYY-MM-DD"}), 400

    db.session.commit()
    return jsonify({"message": "Todo updated"}), 200

@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def api_delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return jsonify({"message": "Todo deleted"}), 200

@app.route("/api/todos/<int:todo_id>/done", methods=["PATCH"])
def api_mark_done(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.complete = True
    db.session.commit()
    return jsonify({"message": f"Todo {todo_id} marked as done"}), 200

@app.route("/api/todos/<int:todo_id>/toggle", methods=["PATCH"])
def api_toggle_done(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.complete = not todo.complete
    db.session.commit()
    return jsonify({"message": f"Todo {todo_id} toggled to {'done' if todo.complete else 'not done'}"}), 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
