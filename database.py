import sqlite3

# ToDo専用のDBファイル
DB_FILE = "todo.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        # todos テーブルだけを作成（user_idは紐付け用に残します）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task TEXT NOT NULL,
                is_done INTEGER DEFAULT 0,
                deadline TEXT
            )
        """)
        conn.commit()

def add_todo(user_id, task_text, deadline_date):
    if task_text:
        deadline_str = deadline_date.strftime("%Y-%m-%d")
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO todos (user_id, task, is_done, deadline) VALUES (?, ?, 0, ?)", 
                           (user_id, task_text, deadline_str))
            conn.commit()

def get_todos(user_id, is_done):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, task, deadline FROM todos WHERE user_id = ? AND is_done = ?", 
                       (user_id, 1 if is_done else 0))
        return cursor.fetchall()

def update_todo_status(todo_id, is_done):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE todos SET is_done = ? WHERE id = ?", (1 if is_done else 0, todo_id))
        conn.commit()

def delete_todo(todo_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        conn.commit()

def update_todo_content(todo_id, new_task_text, new_deadline_date):
    """指定されたタスクの文字内容と期限を上書き更新する"""
    deadline_str = new_deadline_date.strftime("%Y-%m-%d")
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE todos SET task = ?, deadline = ? WHERE id = ?",
            (new_task_text, deadline_str, todo_id)
        )
        conn.commit()