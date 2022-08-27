from distutils.log import error
from typing import final
from xml.dom.xmlbuilder import _DOMBuilderErrorHandlerType
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
import sys
from flask_migrate import Migrate



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres@localhost:5432/todoapp"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Todo(db.Model):
    __tablename__ = "todos"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)


    def __repr__(self) -> str:
        return f'<Todo {self.id} {self.description}>'

class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.relationship('Todo', backref='list', lazy=True)

@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body = {}
    try:
        description = request.get_json()['description']
        todo = Todo(description=description)
        db.session.add(todo)
        db.session.commit()
        body["description"] = todo.description
        
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally: 
        db.session.close()
    if not error:
        return jsonify(body)
    else: 
        abort(400)

# UPDATE
@app.route("/todos/<todo_id>set-completed", methods=['POST'])
def set_completed_todo(todo_id):
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for("index"))

# DELETE
@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()
    except: 
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({ "success" : True })


@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    return render_template('index.html',
    lists=TodoList.query.all(),
    active_list=TodoList.query.get(list_id),
    todos=Todo.query.filter_by(list_id=list_id).order_by('id').all()
    )

# Create List
# @app.route('/lists/create', methods=[POST])
# def create_list():
#     error = False
#     body = {}
#     try:
#         name = request.get_json()['name']
#         todoList = TodoList(name=name)
#         db.session.add(TodoList)
#         db.session.commit()
#         body['id'] = todoList.id
#         bdoy['name'] = todoList.name
#     except:
#         db.session.rollback()
#         error = True
#         print(sys.exc_info)
#     finally: 
#         db.session.close()
#     if error:
#         abort(500)
#     else: 
#         return jsonify(body)
    

@app.route("/") 
def index():
    return redirect(url_for("get_list_todos", list_id=1))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000)




    
