import streamlit as st
import requests
    
def logout():
    st.session_state.clear()
