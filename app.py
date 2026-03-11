import streamlit as st
from rag_pipeline import create_vector_store, get_answer
import base64

# ---------------------- BACKGROUND IMAGE ------------------------
def set_background(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    page_bg = f"""
    <style>
    /* ---- SMALLER SIDEBAR ---- */
    [data-testid="stSidebar"] {{
        min-width: 180px;
        max-width: 180px;
    }}

    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    .chat-bubble-user {{
        background-color: #DCF8C6;
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px 0;
        max-width: 70%;
        float: right;
        clear: both;
    }}

    .chat-bubble-assistant {{
        background-color: #E8E8E8;
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px 0;
        max-width: 70%;
        float: left;
        clear: both;
    }}

    .avatar {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 10px;
    }}
    </style>
    """
    st.markdown(page_bg, unsafe_allow_html=True)

# ---------------------- PAGE CONFIG ------------------------
st.set_page_config(page_title="AI Hospital Assistant", layout="wide")
set_background("Hospital_preview.avif")

# ---------------------- SIDEBAR NAVIGATION ------------------------
st.sidebar.title("🏥 Menu")
menu = st.sidebar.radio(
    "",
    ["User Panel", "Admin Panel"]
)

st.title("🏥 AI Digital Hospital Assistant")
st.markdown("### Providing Secure Medical Support 24/7")

# ---------------------- CHAT HISTORY ------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------------- USER PANEL ------------------------
if menu == "User Panel":
    st.subheader("🧑‍⚕️ User Panel - Ask Medical Questions")

    def submit_question():
        if st.session_state.user_query:
            answer = get_answer(st.session_state.user_query)
            st.session_state.chat_history.append(("You", st.session_state.user_query))
            st.session_state.chat_history.append(("Assistant", answer))
            st.session_state.user_query = ""  # clear input

    # -------- TEXT INPUT --------
    query = st.text_input(
        "Ask your medical question",
        key="user_query",
        on_change=submit_question
    )

    # -------- BUTTONS IN SAME ROW --------
    colA, colB = st.columns([1, 1])

    with colA:
        st.button("🔍 Get Answer", on_click=submit_question, use_container_width=True)

    with colB:
        if st.button("🗑 Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.success("Chat Cleared!")

    st.write("### 💬 Chat")

    # ---------------------- DISPLAY CHAT WITH BUBBLES ------------------------
    for role, message in st.session_state.chat_history:
        if role == "You":
            st.markdown(
                f"""
                <div style='display:flex; justify-content:flex-end;'>
                    <div class="chat-bubble-user">{message}</div>
                    <img src="https://i.imgur.com/8QfZQhW.png" class="avatar"/>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div style='display:flex;'>
                    <img src="https://i.imgur.com/Q7ZV9RN.png" class="avatar"/>
                    <div class="chat-bubble-assistant">{message}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
# ---------------------- ADMIN PANEL ------------------------
elif menu == "Admin Panel":
    st.subheader("🔧 Admin Panel - Manage Knowledge Base")

    uploaded_file = st.file_uploader("Upload PDF", type="pdf")

    if st.button("📚 Create Knowledge Base"):
        if uploaded_file:
            with open("temp.pdf", "wb") as f:
                f.write(uploaded_file.read())
            create_vector_store("temp.pdf")
            st.success("Knowledge Base Created Successfully!")
        else:
            st.warning("Upload a PDF first!")

# ---------------------- FOOTER ------------------------
st.markdown("---")
st.markdown("© 2026 AI Hospital Assistant | Powered by Methodist College of Engineering")