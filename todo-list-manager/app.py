from flask import Flask, render_template, request, redirect, session
import sqlite3
import bcrypt
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DB ----------------
def get_db():
    return sqlite3.connect("tasks.db")

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password BLOB,
        email TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        task TEXT,
        status TEXT,
        due_date TEXT,
        priority TEXT,
        assigned_to INTEGER
    )
    """)

    conn.commit()
    conn.close()

# ---------------- AUTH ----------------
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users VALUES (NULL,?,?,?)",
                       (username, hashed, email))
        conn.commit()
        conn.close()
        return redirect('/login')

    return render_template("signup.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode(), user[2]):
            session['user_id'] = user[0]
            return redirect('/')
        else:
            return "Invalid credentials"

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ---------------- HOME ----------------
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT tasks.*, users.username
    FROM tasks
    LEFT JOIN users ON tasks.assigned_to = users.id
    WHERE tasks.user_id=? OR tasks.assigned_to=?
    """, (session['user_id'], session['user_id']))

    tasks = cursor.fetchall()

    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()

    conn.close()

    today = datetime.today().date()
    updated = []

    for task in tasks:
        due = datetime.strptime(task[4], "%Y-%m-%d").date()

        if due < today:
            alert = "Overdue"
        elif (due - today).days <= 2:
            alert = "Due Soon"
        else:
            alert = "Normal"

        updated.append((task, alert, task[7]))  # username

    return render_template("index.html", tasks=updated, users=users)

# ---------------- ADD ----------------
@app.route('/add', methods=['POST'])
def add():
    task = request.form['task']
    due = request.form['due_date']
    priority = request.form['priority']
    assigned = request.form.get('assigned_to')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO tasks (user_id, task, status, due_date, priority, assigned_to)
    VALUES (?,?,?,?,?,?)
    """, (session['user_id'], task, "Pending", due, priority, assigned))

    conn.commit()
    conn.close()
    return redirect('/')

# ---------------- UPDATE ----------------
@app.route('/update/<int:id>')
def update(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT status FROM tasks WHERE id=?", (id,))
    status = cursor.fetchone()[0]

    new = "Completed" if status == "Pending" else "Pending"
    cursor.execute("UPDATE tasks SET status=? WHERE id=?", (new, id))

    conn.commit()
    conn.close()
    return redirect('/')

# ---------------- DELETE ----------------
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

# ---------------- ADMIN ----------------
@app.route('/admin')
def admin():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT tasks.id, tasks.task, tasks.status, tasks.due_date,
           tasks.priority, users.id, users.username
    FROM tasks
    LEFT JOIN users ON tasks.assigned_to = users.id
    """)

    tasks = cursor.fetchall()
    conn.close()

    return render_template("admin.html", tasks=tasks)

# ---------------- RUN ----------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)