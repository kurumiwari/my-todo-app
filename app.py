import sqlite3
import streamlit as st
import hashlib

DB_FILE = "todo.db"

# --- 1. データベース初期設定（ユーザーテーブルの追加） ---
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        # ユーザー管理テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        # タスク管理テーブル（user_id カラムを追加して紐付け）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task TEXT NOT NULL,
                is_done INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        conn.commit()

init_db()

# --- 2. パスワードのハッシュ化（セキュリティ用） ---
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- 3. ユーザー認証用関数 ---
def create_user(username, password):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?,?)", (username, make_hash(password)))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # 既に同じユーザー名が存在する場合

def login_user(username, password):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, make_hash(password)))
        user = cursor.fetchone()
        return user[0] if user else None

# --- 4. タスク操作用関数（user_id でフィルタリング） ---
def add_todo(user_id, task_text):
    if task_text:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO todos (user_id, task, is_done) VALUES (?, ?, 0)", (user_id, task_text))
            conn.commit()

def get_todos(user_id, is_done):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, task FROM todos WHERE user_id = ? AND is_done = ?", (user_id, 1 if is_done else 0))
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


# --- 5. ログイン状態のセッション管理 ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = ""

# --- 6. 画面表示の制御 ---
if not st.session_state.logged_in:
    # --- 【ログイン・サインアップ画面】 ---
    st.title("🔑 ToDoアプリ ログイン")
    
    auth_mode = st.radio("モード選択", ["ログイン", "新規ユーザー登録"])
    
    username = st.text_input("ユーザー名")
    password = st.text_input("パスワード", type="password")
    
    if auth_mode == "ログイン":
        if st.button("ログイン"):
            user_id = login_user(username, password)
            if user_id:
                st.session_state.logged_in = True
                st.session_state.user_id = user_id
                st.session_state.username = username
                st.success(f"ログイン成功！ こんにちは {username} さん")
                st.rerun()
            else:
                st.error("ユーザー名またはパスワードが違います。")
                
    elif auth_mode == "新規ユーザー登録":
        if st.button("アカウント作成"):
            if username and password:
                if create_user(username, password):
                    st.success("アカウントが作成されました！ログインモードに切り替えて進んでください。")
                else:
                    st.error("そのユーザー名は既に使われています。")
            else:
                st.error("ユーザー名とパスワードを入力してください。")

else:
    # --- 【ログイン後のToDoアプリ画面】 ---
    # サイドバーにログアウトボタンを設置
    st.sidebar.write(f"👤 ログイン中: {st.session_state.username}")
    if st.sidebar.button("ログアウト"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = ""
        st.rerun()

    st.title("進化版 ToDo アプリ 🚀")
    page = st.sidebar.radio("メニュー", ["タスク一覧", "実行済みリスト"])

    user_id = st.session_state.user_id

    if page == "タスク一覧":
        st.subheader("📝 未完了のタスク")

        # Enterでタスク追加
        new_todo = st.text_input("新しいタスクを入力してEnter:", placeholder="例：パスワードの管理")
        
        if "last_todo" not in st.session_state:
            st.session_state.last_todo = ""

        if new_todo and new_todo != st.session_state.last_todo:
            add_todo(user_id, new_todo)  # ログイン中のuser_idを紐付ける
            st.session_state.last_todo = new_todo
            st.rerun()

        # 一覧表示（自分のタスクのみ）
        todos = get_todos(user_id, is_done=False)
        if not todos:
            st.info("現在タスクはありません。")
        else:
            for todo_id, task in todos:
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    if st.checkbox(task, key=f"todo_{todo_id}"):
                        update_todo_status(todo_id, is_done=True)
                        st.rerun()
                with col2:
                    if st.button("削除", key=f"del_{todo_id}"):
                        delete_todo(todo_id)
                        st.rerun()

    elif page == "実行済みリスト":
        st.subheader("✅ 完了したタスク")
        completed_todos = get_todos(user_id, is_done=True)

        if not completed_todos:
            st.info("完了したタスクはまだありません。")
        else:
            for todo_id, task in completed_todos:
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    st.write(f"~~{task}~~")
                with col2:
                    if st.button("戻す", key=f"rev_{todo_id}"):
                        update_todo_status(todo_id, is_done=False)
                        st.rerun()