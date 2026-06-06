import streamlit as st

st.title("今日中にリリースするToDoアプリ 🚀")

# タスクの保存先（セッション状態）
if "todos" not in st.session_state:
    st.session_state.todos = []

# 入力フォーム
new_todo = st.text_input("タスクを入力してください:", placeholder="例：ドキュメントを読む")

if st.button("追加") and new_todo:
    st.session_state.todos.append({"task": new_todo, "done": False})
    st.rerun()

# 一覧表示
st.write("### タスク一覧")
for i, todo in enumerate(st.session_state.todos):
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        # 完了チェックボックス（今回はシンプルに表示だけ、またはチェック連動）
        st.write(f"- {todo['task']}")
    with col2:
        if st.button("削除", key=f"del_{i}"):
            st.session_state.todos.pop(i)
            st.rerun()
