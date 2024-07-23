import streamlit as st
from utils.components import *
from utils.user import logout
from data.get_data import get_data, initialize_data
from menu.show_lighthouse import Showlighthouse
from menu.proposal import Proposal
from menu.hole import Hole
from menu.opportunity import Opportunity

def render():
    # pegando dados da sessão como ID e NOME
    user_id = st.session_state['user_data']["data"]["user_id"]
    user_name = st.session_state['user_data']["data"]['full_name']

    col1, col2, col3 = st.columns([3.5,0.4,0.3])
    if user_id == 39996:
        col1.write(f"## Bom dia, thiaguinho sorridente :)")
    else:
        col1.write(f"## Olá, "+user_name)
    col2.image("./assets/imgs/eshows100x100.png")
    col3.markdown("<p style='padding-top:0.7em'></p>", unsafe_allow_html=True)
    col3.button(label="Logout", on_click=logout)
    
    component_effect_underline()
    st.write('## Acompanhamento Diário')
    st.markdown('<div class="full-width-line-white"></div>', unsafe_allow_html=True)
    st.markdown('<div class="full-width-line-black"></div>', unsafe_allow_html=True)

    data = initialize_data(user_id)
    data = get_data(data)
    tab1, tab2, tab3, tab4 = st.tabs(["Farol Shows","Propostas","Buracos","Oportunidades"])

    with tab1:
        page = Showlighthouse(data)
        page.render()
    with tab2:
        page = Proposal(data)
        page.render()
    with tab3:
        page = Hole(data)
        page.render()
    with tab4:
        page = Opportunity(data)
        page.render()

if __name__ == "__main__":
    if 'loggedIn' not in st.session_state:
        st.switch_page("main.py")
    
    st.set_page_config(page_title="Home | Relatorio Eshows",page_icon="./assets/imgs/eshows-logo100x100.png", layout="wide")

    component_hide_sidebar()
    component_fix_tab_echarts()

    if st.session_state['loggedIn']:
        render()
    else:
        st.switch_page("main.py")

