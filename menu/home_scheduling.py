import streamlit as st
from menu.page import Page
from utils.components import *
from utils.functions import *

def buildHomeScheduling(showMonitoring, artistFavoriteBlocked):
    showMonitoring = function_get_today_data(showMonitoring.copy())
    st.markdown('## Agendamento de casas')
    
    tab1, tab2 = st.tabs(["Mapa de propostas","Pendências"])
    with tab1:
        row1 = st.columns(3)
        tile = row1[0].container(border=True)
        today_shows = showMonitoring['ESTABELECIMENTO'].nunique()
        tile.write(f"<p style='text-align: center;'>Casas com show hoje</br>{today_shows}</p>", unsafe_allow_html=True)

        tile = row1[1].container(border=True)
        today_artists_shows = showMonitoring['ARTISTA'].nunique()
        tile.write(f"<p style='text-align: center;'>Artistas com shows hoje</br>{today_artists_shows}</p>", unsafe_allow_html=True)

        tile = row1[2].container(border=True)
        quanty_0 = len(showMonitoring[showMonitoring['NÚMERO DE SHOWS'] == 0])
        quanty_1 = len(showMonitoring[showMonitoring['NÚMERO DE SHOWS'] == 1])
        tile.write(f"<p style='text-align: center;'>Artistas com show pela primeira vez</br>{quanty_0 + quanty_1}</p>", unsafe_allow_html=True)

        component_plotDataframe(showMonitoring, 'Mapa de propostas')
    
    artistFavoriteBlocked_formated, marked, unmarked = function_calculate_artistFavoriteBlocked(artistFavoriteBlocked)
    with tab2:
        row1 = st.columns(3)
        tile = row1[0].container(border=True)
        pendating = len(showMonitoring[showMonitoring['STATUS']=='Pendente'])
        tile.write(f"<p style='text-align: center;'>Propostas com pedência</br>{pendating}</p>", unsafe_allow_html=True)

        tile = row1[1].container(border=True)
        tile.write(f"<p style='text-align: center;'>Pendências de favoritos e bloqueados marcados</br>{marked}</p>", unsafe_allow_html=True)

        tile = row1[2].container(border=True)
        tile.write(f"<p style='text-align: center;'>Pedências de favoritos e boloqueados desmarcados</br>{unmarked}</p>", unsafe_allow_html=True)
        
        row2 = st.columns(2)
        with row2[0]:
            filter_select = component_filterMultiselect(showMonitoring, 'CONFIRMAÇÃO',"")
            filtredAcconty = (showMonitoring[showMonitoring['CONFIRMAÇÃO'].isin(filter_select)])
        component_plotDataframe(filtredAcconty[filtredAcconty['STATUS']=='Pendente'], 'Mapa de pendências de shows')
        
        component_plotDataframe(artistFavoriteBlocked_formated, 'Mapa de pendências de favoritos e bloqueados')

class HomeScheduling (Page):
    def render(self):
        buildHomeScheduling(self.data['showMonitoring'], self.data['artistFavoriteBlocked'])