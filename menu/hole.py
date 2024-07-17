import streamlit as st
from menu.page import Page
from utils.components import *
from utils.functions import *
import pandas as pd
from datetime import datetime, timedelta

def buildHole(holemap):
    
    st.markdown('## Buracos')

    row1 = st.columns(5)
    tile = row1[0].container(border=True)
    today = datetime.now().date()
    num_line_holemap = len(holemap[holemap['DATA INÍCIO'] == today.strftime('%d/%m')])
    tile.write(f"<p style='text-align: center;'>Buracos Hoje</br>{num_line_holemap}</p>", unsafe_allow_html=True)

    tile = row1[1].container(border=True)
    num_line_holemap = len(holemap)
    tile.write(f"<p style='text-align: center;'>Buracos</br>{num_line_holemap}</p>", unsafe_allow_html=True)

    tile = row1[2].container(border=True)
    num_line_holemap = len(holemap[holemap['ID OPORTUNIDADE'].notnull()])
    tile.write(f"<p style='text-align: center;'>Buracos com Oportunidade</br>{num_line_holemap}</p>", unsafe_allow_html=True)

    tile = row1[3].container(border=True)
    num_line_holemap = len(holemap[holemap['ID OPORTUNIDADE'].isnull()])
    tile.write(f"<p style='text-align: center;'>Buracos sem Oportunidade</br>{num_line_holemap}</p>", unsafe_allow_html=True)

    tile = row1[4].container(border=True)
    tile.write(f"<p style='text-align: center;'>Tempo Médio Para Preencher Buracos</br>xxxxxxxx</p>", unsafe_allow_html=True)

    row = st.columns(3)
    with row[0]:
        acconty = component_filterMultiselect(holemap, 'KEY_ACCOUNT', "Nomes")
        filtredAcconty = (holemap[holemap['KEY_ACCOUNT'].isin(acconty)])
    
    tab1, tab2, tab3= st.tabs(["Buracos de Hoje","Buracos de Amanhã","Todos os Buracos"])

    with tab1:
        row2 = st.columns(1)
        today = datetime.now().date()
        with row2[0]:
            component_plotDataframe(filtredAcconty[filtredAcconty['DATA INÍCIO'] == today.strftime('%d/%m')], 'Tabela Buracos Hoje') 
    
    with tab2:
        row3 = st.columns(1)
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        with row3[0]: component_plotDataframe(filtredAcconty[filtredAcconty['DATA INÍCIO'] == tomorrow.strftime('%d/%m')], 'Tabela Buracos Amanhã') 

    with tab3:
        row4 = st.columns(1)
        with row4[0]: component_plotDataframe(filtredAcconty, 'Tabela Buracos') 

class Hole (Page):
    def render(self):
        buildHole(self.data['holeMap'])