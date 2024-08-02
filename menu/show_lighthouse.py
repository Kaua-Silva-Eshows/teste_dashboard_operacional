import streamlit as st
from data.queries import show_in_next_thirty_minutes, show_monitoring_today_and_tomorrow, show_to_cancel
from data.transfeeraconnect import get_statement_report
from menu.page import Page
from utils.components import *
from utils.functions import *
import pandas as pd
from datetime import datetime

def buildShowlighthouse(showMonitoring, nextShows, showToCancel, transfeeraStatementReport):
    st.markdown('## Shows confirmados')

    row1 = st.columns(4)
    tile = row1[0].container(border=True)

    today = datetime.today().date()

    showMonitoring['DATA INÍCIO'] = pd.to_datetime(showMonitoring['DATA INÍCIO'],format='%d/%m/%Y', errors='coerce').dt.date
    filtered_df = showMonitoring[showMonitoring['DATA INÍCIO'] == today]
    filtered_df1 = showMonitoring['STATUS'] == 'Aceita'
    filtered_df2 = showMonitoring[filtered_df1 & (showMonitoring['DATA INÍCIO'] == today)]
    filtered_df2['DATA INÍCIO'] = filtered_df2['DATA INÍCIO'].apply(lambda x: x.strftime('%d/%m/%Y') if pd.notnull(x) else '')
 
    
    num_line_showMonitoring = len(filtered_df)
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
    tile.write(f"<p style='text-align: center;'>Shows com Status Pendente</br>{num_line_showMonitoring}</p>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Monitoramento de shows","Shows nos próximos 30min","Shows para cancelar", "Shows Com Status Pendente"])
    with tab1:
        row2 = st.columns(3)
        filtredShowMonitoring = showMonitoring.copy()
        with row2[0]:
            status = component_filterMultiselect(showMonitoring, 'STATUS', "Proposta da semana recorrente:")
            filtredShowMonitoring = filtredShowMonitoring[filtredShowMonitoring['STATUS'].isin(status)]
        with row2[1]:
            confirmation = component_filterMultiselect(showMonitoring, 'CONFIRMAÇÃO', "Confirmação dos SHOWS:")
            filtredShowMonitoring = filtredShowMonitoring[filtredShowMonitoring['CONFIRMAÇÃO'].isin(confirmation)]
        with row2[2]:
            data = component_filterDataSelect()
            filtredShowMonitoring = function_get_today_tomorrow_date(filtredShowMonitoring, data)     
        
        component_plotDataframe(filtredShowMonitoring, 'Monitoramento de shows hoje e amanhã')
        #st.write(transfeeraStatementReport)
    with tab2:
        component_plotDataframe(nextShows, 'Shows nos próximos 30 minutos')
    
    with tab3:
        row3 = st.columns(1)
        with row3[0]: component_plotDataframe(showToCancel, 'Shows para cancelar')

    with tab4:
        showMonitoring['DATA INÍCIO'] = showMonitoring['DATA INÍCIO'].apply(lambda x: x.strftime('%d/%m/%Y') if pd.notnull(x) else '')
        filtredShowMonitoring = showMonitoring.copy()
        row4 = st.columns(2)
        with row4[0]:
            status = component_filterMultiselect(showMonitoring, 'CONFIRMAÇÃO', "Proposta da semana recorrente")
            filtredShowMonitoring = filtredShowMonitoring[filtredShowMonitoring['CONFIRMAÇÃO'].isin(status)]

        with row4[1]:
            show_time = st.selectbox('Escolha um horário de Show:', ['Todos','Almoço','Happy Hour','Jantar'], index=0)
            filtredShowMonitoring = function_filter_hourly(filtredShowMonitoring, show_time)

        component_plotDataframe(filtredShowMonitoring[filtredShowMonitoring['STATUS'] == 'Pendente'], 'Shows Com Status Pendente')
        
        

class Showlighthouse():
    def render(self):
        self.data = {}
        self.data['showMonitoring'] = show_monitoring_today_and_tomorrow()
        self.data['nextShows'] = show_in_next_thirty_minutes()
        self.data['showToCancel'] = show_to_cancel()
        self.data['transfeeraStatementReport'] = get_statement_report()
        
        buildShowlighthouse(self.data['showMonitoring'], self.data['nextShows'], self.data['showToCancel'], self.data['transfeeraStatementReport'])

