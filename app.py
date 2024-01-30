from flask import Flask, request, jsonify, g
import sqlite3

app = Flask(__name__)
DATABASE = 'tasks.db'

# Function to get a database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, is_completed BOOLEAN)')
    return db

# Function to close the database connection
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Create a new task
@app.route('/v1/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    title = data.get('title')
    is_completed = data.get('is_completed', False)

    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO tasks (title, is_completed) VALUES (?, ?)', (title, is_completed))
    db.commit()

    cursor.execute('SELECT last_insert_rowid()')
    new_task_id = cursor.fetchone()[0]

    return jsonify({'id' : new_task_id}), 201

# List all tasks
@app.route('/v1/tasks', methods=['GET'])
def get_all_tasks():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM tasks')
    tasks = cursor.fetchall()
    
    task_list = [{'id': task[0], 'title': task[1], 'is_completed': bool(task[2])} for task in tasks]

    return jsonify({'tasks': task_list})

# Get a specific task
@app.route('/v1/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    task = cursor.fetchone()

    if task:
        task_info = {'id': task[0], 'title': task[1], 'is_completed': bool(task[2])}
        return jsonify(task_info), 200
    else:
        return jsonify({'error': 'There is no task at that id'}), 404

# Delete a specified task
@app.route('/v1/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    db.commit()

    return '', 204

# Edit the title or completion of a specific task
@app.route('/v1/tasks/<int:task_id>', methods=['PUT'])
def edit_task(task_id):
    data = request.get_json()
    title = data.get('title')
    is_completed = data.get('is_completed')

    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    existing_task = cursor.fetchone()

    if existing_task is None:
        return jsonify({'error': 'There is no task at that id'}), 404

    cursor.execute('UPDATE tasks SET title = ?, is_completed = ? WHERE id = ?', (title, is_completed, task_id))
    db.commit()

    return '', 204

# Extra Credit: Bulk add multiple tasks in one request
@app.route('/v1/tasks/bulk', methods=['POST'])
def bulk_add_tasks():
    data = request.get_json()
    
    tasks = data.get('tasks')
    if not tasks or not isinstance(tasks, list):
        return jsonify({'message': 'Invalid data format for tasks'}), 400

    db = get_db()
    cursor = db.cursor()
    new_task_ids = []

    for task in tasks:
        title = task.get('title')
        is_completed = task.get('is_completed', False)
        cursor.execute('INSERT INTO tasks (title, is_completed) VALUES (?, ?)', (title, is_completed))
        new_task_ids.append({'id': cursor.lastrowid})
    db.commit()
    
    return jsonify({'tasks': new_task_ids}), 201

# Extra Credit: Bulk delete multiple tasks in one request
@app.route('/v1/tasks/bulk', methods=['DELETE'])
def bulk_delete_tasks():
    data = request.get_json()
    
    task_ids = data.get('tasks')
    if not task_ids or not isinstance(task_ids, list):
        return jsonify({'error': 'Invalid data format for task_ids'}), 400

    db = get_db()
    cursor = db.cursor()
    for task_id in task_ids:
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id['id'],))

    db.commit()

    return jsonify({'message': 'Bulk tasks deleted successfully'}), 201

if __name__ == '__main__':
    app.teardown_appcontext(close_db)
    app.run(debug=True, host='localhost', port=5000)
