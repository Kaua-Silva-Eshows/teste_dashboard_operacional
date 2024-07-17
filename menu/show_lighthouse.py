import streamlit as st
from menu.page import Page
from utils.components import *
from utils.functions import *
import pandas as pd
from datetime import datetime

def buildShowlighthouse(showMonitoring, nextShows, showToCancel):
    st.markdown('## Shows confirmados')
    row1 = st.columns(4)

    tile = row1[0].container(border=True)
    num_line_showMonitoring = len(showMonitoring[showMonitoring['STATUS'] == 'Aceita'])
    tile.write(f"<p style='text-align: center;'>Shows confirmados hoje</br>{num_line_showMonitoring}</p>", unsafe_allow_html=True)

    tile = row1[1].container(border=True)
    num_line_nextShows = len(nextShows)
    tile.write(f"<p style='text-align: center;'>Shows nos próximos 30min.</br>{num_line_nextShows}</p>", unsafe_allow_html=True)

    tile = row1[2].container(border=True)
    today = datetime.now().date()
    num_line_showCancel = len(showToCancel[showToCancel['DATA INÍCIO'] == today.strftime('%d/%m/%Y')])
    tile.write(f"<p style='text-align: center;'>Shows cancelados hoje</br>{num_line_showCancel}</p>", unsafe_allow_html=True)

    tile = row1[3].container(border=True)
    num_line_showMonitoring = len(showMonitoring[showMonitoring['STATUS'] == 'Pendente'])
    tile.write(f"<p style='text-align: center;'>Shows pedente de confirmação</br>{num_line_showMonitoring}</p>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Monitoramento de shows","Shows nos próximos 30min","Shows para cancelar"])
    
    with tab1:
        row2 = st.columns(3)
        with row2[0]:
            status = component_filterMultiselect(showMonitoring, 'STATUS', "Proposta da semana recorrente:")
            showMonitoring = showMonitoring[showMonitoring['STATUS'].isin(status)]
        with row2[1]:
            data=component_filterDataSelect()
            showMonitoring = function_get_today_tomorrow_date(showMonitoring, data)     
        
        component_plotDataframe(showMonitoring, 'Monitoramento de shows hoje e amanhã')
    with tab2:
        component_plotDataframe(nextShows, 'Shows nos próximos 30 minutos')
    
    with tab3:
        row3 = st.columns(3)
        with row3[0]:
            show_time = st.selectbox('Escolha um horário de Show:', ['Almoço','Happy Hour','Jantar'], index=0)
            showToCancel = function_filter_hourly(showToCancel, show_time)
            
        component_plotDataframe(showToCancel, 'Shows para cancelar')
        
        

class Showlighthouse (Page):
    def render(self):
        buildShowlighthouse(self.data['showMonitoring'],self.data['nextShows'],self.data['showToCancel'],)