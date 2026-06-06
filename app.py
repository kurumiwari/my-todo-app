import streamlit as st
from datetime import date
import database as db
import auth

# 【修正】両方のデータベースを初期化する
db.init_db()
auth.init_auth_db()

# ログイン状態のセッション管理
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = ""

# 画面表示の制御
if not st.session_state.logged_in:
    st.title("🔑 ToDoアプリ ログイン")
    auth_mode = st.radio("モード選択", ["ログイン", "新規ユーザー登録"])
    username = st.text_input("ユーザー名")
    password = st.text_input("パスワード", type="password")
    
    if auth_mode == "ログイン":
        if st.button("ログイン"):
            user_id = auth.login_user(username, password)
            if user_id:
                st.session_state.logged_in = True
                st.session_state.user_id = user_id
                st.session_state.username = username
                st.success("ログイン成功！")
                st.rerun()
            else:
                st.error("ユーザー名またはパスワードが違います。")
                
    elif auth_mode == "新規ユーザー登録":
        if st.button("アカウント作成"):
            if username and password:
                if auth.create_user(username, password):
                    st.success("アカウントが作成されました！")
                else:
                    st.error("そのユーザー名は既に使われています。")

else:
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

        col_input, col_date = st.columns([0.7, 0.3])
        with col_input:
            new_todo = st.text_input("新しいタスクを入力してEnter:", placeholder="例：期日までに提出する")
        with col_date:
            todo_date = st.date_input("期限", value=date.today())
        
        if "last_todo" not in st.session_state:
            st.session_state.last_todo = ""

        if new_todo and new_todo != st.session_state.last_todo:
            db.add_todo(user_id, new_todo, todo_date)
            st.session_state.last_todo = new_todo
            st.rerun()

        todos = db.get_todos(user_id, is_done=False)
        if not todos:
            st.info("現在タスクはありません。")
        else:
            today_str = date.today().strftime("%Y-%m-%d")
            
            for todo_id, task, deadline in todos:
                is_overdue = deadline < today_str if deadline else False
                
                # --- 【要件】期限を過ぎていたらアイコン（絵文字）と赤文字にする ---
                if is_overdue:
                    icon = "⚠️ "
                    text_style = "color: #ff4b4b; font-weight: bold;"  # Streamlitの標準アクセント赤
                else:
                    icon = ""
                    text_style = "color: #212529;"
                
                # 複雑なHTMLの囲みはやめて、Streamlitの標準コンテナ（枠線付き）に戻す
                with st.container(border=True):
                    col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
                    
                    with col1:
                        display_text = f"{icon}{task} (期限: {deadline})" if deadline else f"{icon}{task}"
                        
                        col_cb, col_txt = st.columns([0.1, 0.9])
                        with col_cb:
                            is_checked = st.checkbox("", key=f"todo_{todo_id}")
                        with col_txt:
                            # テキスト部分だけ安全に色と絵文字を適用
                            st.markdown(f'<p style="{text_style} margin: 0; padding-top: 3px;">{display_text}</p>', unsafe_allow_html=True)
                            
                        if is_checked:
                            db.update_todo_status(todo_id, is_done=True)
                            st.rerun()
                            
                    with col2:
                        if st.button("編集", key=f"edit_trigger_{todo_id}"):
                            st.session_state.editing_todo = (todo_id, task, deadline)
                            st.rerun()
                    with col3:
                        if st.button("削除", key=f"del_{todo_id}"):
                            db.delete_todo(todo_id)
                            if st.session_state.editing_todo and st.session_state.editing_todo[0] == todo_id:
                                st.session_state.editing_todo = None
                            st.rerun()
            
            
    elif page == "実行済みリスト":
        st.subheader("✅ 完了したタスク")
        completed_todos = db.get_todos(user_id, is_done=True)

        if not completed_todos:
            st.info("完了したタスクはまだありません。")
        else:
            for todo_id, task, deadline in completed_todos:
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    display_text = f"~~{task}~~ (期限: {deadline})" if deadline else f"~~{task}~~"
                    st.write(display_text)
                with col2:
                    if st.button("戻す", key=f"rev_{todo_id}"):
                        db.update_todo_status(todo_id, is_done=False)
                        st.rerun()
