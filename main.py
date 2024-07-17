import streamlit as st
from utils.user import login
from utils.components import component_hide_sidebar

def handle_login(userName, userPassoword):
    if"@eshows.com.br" not in userName:
        st.error("Usuário fora do domínio Eshows! Tente com seu email @eshows.")
        return
    
    if user_data := login(userName, userPassoword):
        st.session_state["loggedIn"] = True
        st.session_state["user_data"] = user_data
    else:
        st.session_state["loggedIn"] = False
        st.error("Email ou senha inválidos!")

def show_login_page():
    col1, col2 = st.columns([4,1])
    col1.write("## DashBoard Operacional")
    col2.image("./assets/imgs/eshows-logo.png", width=100)
    userName = st.text_input(label="", value="", placeholder="login")
    userPassword = st.text_input(label="", value="", placeholder="Senha",type="password")
    st.button("login", on_click=handle_login, args=(userName, userPassword))

def main():
    if "loggedIn" not in st.session_state:
        st.session_state["loggedIn"] = False
        st.session_state["user_date"] = None

    if not st.session_state["loggedIn"]:
        show_login_page()
        st.stop()
    else:
        st.switch_page("pages/home.py")

if __name__ == "__main__":
    st.set_page_config(
    page_title="login | Relatorio Eshows",
    page_icon="./assets/imgs/eshows-logo100x100.png",
    layout="centered",
    )

    component_hide_sidebar()
    main()