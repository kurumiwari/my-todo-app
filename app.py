import sqlite3
import streamlit as st

# --- 1. データベースの初期設定 ---
DB_FILE = "todo.db"


def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        # id, task(内容), is_done(0:未完了, 1:完了) のテーブルを作成
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                is_done INTEGER DEFAULT 0
            )
        """
        )
        conn.commit()


init_db()

# --- 2. 画面タイトルとナビゲーション ---
st.title("進化版 ToDo アプリ 🚀")

# サイドバーでページの切り替え
page = st.sidebar.radio("メニュー", ["タスク一覧", "実行済みリスト"])

# --- 3. データの操作用関数 ---
# タスク追加
def add_todo(task_text):
    if task_text:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO todos (task, is_done) VALUES (?, 0)", (task_text,)
            )
            conn.commit()


# タスクの状態更新（完了/未完了）
def update_todo_status(todo_id, is_done):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE todos SET is_done = ? WHERE id = ?",
            (1 if is_done else 0, todo_id),
        )
        conn.commit()


# タスクの完全削除
def delete_todo(todo_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        conn.commit()


# データの取得
def get_todos(is_done):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, task FROM todos WHERE is_done = ?",
            (1 if is_done else 0,),
        )
        return cursor.fetchall()


# --- 4. メイン処理（ページごとの表示） ---

if page == "タスク一覧":
    st.subheader("📝 未完了のタスク")

    # 【要件】Enterで追加できるように
    # st.text_inputの `on_change` または、入力値をそのままトリガーにします。
    # keyを設定し、確定（Enter）されたら即時追加処理に回します。
    new_todo = st.text_input(
        "新しいタスクを入力してEnter:", placeholder="例：リファクタリング"
    )

    # 以前に入力された値を判定してDBに追加
    # Streamlitのセッションを使って重複追加を防ぐ簡易的な判定
    if "last_todo" not in st.session_state:
        st.session_state.last_todo = ""

    if new_todo and new_todo != st.session_state.last_todo:
        add_todo(new_todo)
        st.session_state.last_todo = new_todo
        st.rerun()

    # 一覧表示
    todos = get_todos(is_done=False)
    if not todos:
        st.info("現在タスクはありません。")
    else:
        for todo_id, task in todos:
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                # 【要件】チェックボックスをつけたら実行済みへ移動
                # デフォルトはFalse(未チェック)。チェックされた瞬間DBを更新してリロード
                if st.checkbox(task, key=f"todo_{todo_id}"):
                    update_todo_status(todo_id, is_done=True)
                    st.rerun()
            with col2:
                if st.button("削除", key=f"del_{todo_id}"):
                    delete_todo(todo_id)
                    st.rerun()

elif page == "実行済みリスト":
    st.subheader("✅ 完了したタスク")

    # 一覧表示（is_done=True のものを取得）
    completed_todos = get_todos(is_done=True)

    if not completed_todos:
        st.info("完了したタスクはまだありません。")
    else:
        for todo_id, task in completed_todos:
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                # 打ち消し線を入れて表示
                st.write(f"~~{task}~~")
            with col2:
                # 元に戻すボタン（オプション機能）
                if st.button("戻す", key=f"rev_{todo_id}"):
                    update_todo_status(todo_id, is_done=False)
                    st.rerun()