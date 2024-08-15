import streamlit as st
from data.queries import show_in_next_one_hour, show_monitoring_today_and_tomorrow, show_to_cancel
from data.transfeeraconnect import get_statement_report
from menu.page import Page
from utils.components import *
from utils.functions import *
import pandas as pd
from datetime import datetime

def buildShowlighthouse(showMonitoring, nextShows, showToCancel): #, transfeeraStatementReport)
    st.markdown('## Shows confirmados')

    row1 = st.columns(5)
    filtredShowMonitoring = showMonitoring.copy()
    
    with row1[0]:
            data = component_filterDataSelect()
            filtredShowMonitoring = function_get_today_tomorrow_date(filtredShowMonitoring, data)

    row2 = st.columns(4)
    filtered_df1 = filtredShowMonitoring['STATUS'] == 'Aceita'
    filtered_df2 = filtredShowMonitoring[filtered_df1]
    
    tile = row2[0].container(border=True)
    num_line_showMonitoring = len(filtered_df2)
    tile.write(f"<p style='text-align: center;'>Shows confirmados</br>{num_line_showMonitoring}</p>", unsafe_allow_html=True)

    tile = row2[1].container(border=True)
    num_line_nextShows = len(nextShows)
    tile.write(f"<p style='text-align: center;'>Shows na Proxima 1 Hora.</br>{num_line_nextShows}</p>", unsafe_allow_html=True)

    tile = row2[2].container(border=True)
    filtredShowCancel = showToCancel.copy()
    filtredShowCancel = function_get_today_tomorrow_date(filtredShowCancel, data)
    num_line_showCancel = len(filtredShowCancel)
    tile.write(f"<p style='text-align: center;'>Shows cancelados</br>{num_line_showCancel}</p>", unsafe_allow_html=True)

    tile = row2[3].container(border=True)
    filtered_df1 = filtredShowMonitoring['STATUS'] == 'Pendente'
    filtered_df2 = filtredShowMonitoring[filtered_df1]
    num_line_showMonitoring = len(filtered_df2)
    tile.write(f"<p style='text-align: center;'>Shows com Status Pendente</br>{num_line_showMonitoring}</p>", unsafe_allow_html=True)


    row3 = st.columns(2)

    tile = row3[0].container(border=True)
    filtered_df1 = filtredShowMonitoring['STATUS'] == 'Checkin Realizado'
    filtered_df2 = filtredShowMonitoring[filtered_df1]
    num_line_showMonitoring = len(filtered_df2)
    tile.write(f"<p style='text-align: center;'>Check-in</br>{num_line_showMonitoring}</p>", unsafe_allow_html=True)

    tile = row3[1].container(border=True)
    filtered_df1 = filtredShowMonitoring['STATUS'] == 'Checkout Realizado'
    filtered_df2 = filtredShowMonitoring[filtered_df1]
    num_line_showMonitoring = len(filtered_df2)
    tile.write(f"<p style='text-align: center;'>Check-out</br>{num_line_showMonitoring}</p>", unsafe_allow_html=True)

    row4 = st.columns(3)
    
    tile = row4[0].container(border=True)
    establishment_shows = filtredShowMonitoring['ESTABELECIMENTO'].nunique()
    tile.write(f"<p style='text-align: center;'>Casas com show</br>{establishment_shows}</p>", unsafe_allow_html=True)

    tile = row4[1].container(border=True)
    artists_shows = filtredShowMonitoring['ARTISTA'].nunique()
    tile.write(f"<p style='text-align: center;'>Artistas com shows</br>{artists_shows}</p>", unsafe_allow_html=True)

    tile = row4[2].container(border=True)
    quanty_0 = len(filtredShowMonitoring[filtredShowMonitoring['NÚMERO DE SHOWS'] == 0])
    quanty_1 = len(filtredShowMonitoring[filtredShowMonitoring['NÚMERO DE SHOWS'] == 1])
    tile.write(f"<p style='text-align: center;'>Artistas com show pela primeira vez</br>{quanty_0 + quanty_1}</p>", unsafe_allow_html=True)

    row = st.columns(1)
    artists_filtred = filtredShowMonitoring.drop(['STATUS', 'CIDADE', 'ENDEREÇO', 'HORÁRIO CHECKIN', 'OBSERVAÇÃO CHECKIN', 'HORÁRIO CHECKOUT',
    'SOLICITAÇÃO DE CANCELAMENTO', 'SINALIZOU PROBLEMA', 'NÚMERO DE SHOWS NA CASA', 'COMISSÃO', 'STATUS MANUAL', 'STATUS ESTABELECIMENTO'], axis=1)
    artists_filtred = artists_filtred[artists_filtred['NÚMERO DE SHOWS'] <= 1]
    artists_filtred = artists_filtred[['ID PROPOSTA', 'ARTISTA', 'ESTABELECIMENTO','DATA INÍCIO','HORÁRIO INÍCIO','HORÁRIO FIM','CELULAR DO ARTISTA','CONFIRMAÇÃO','OBSERVAÇÃO DO ARTISTA','NÚMERO DE SHOWS','VER DETALHES']]

    with row[0]: 
        with st.expander("Visualizar Artistas com shows pela Primeira vez"):
            component_plotDataframe(artists_filtred, 'Tabela De Artistas com shows pela Primeira vez')

    tab1, tab2, tab3, tab4 = st.tabs(["Shows na Proxima 1 Hora","Monitoramento de shows","Shows para cancelar", "Shows Com Status Pendente"])
    
    with tab1:
        component_plotDataframe(nextShows, 'Shows na Proxima 1 Hora')
    
    with tab2:
        row5 = st.columns(3)
        with row5[0]:
            status = component_filterMultiselect(showMonitoring, 'STATUS', "Proposta da semana recorrente:")
            filtredShowMonitoring = filtredShowMonitoring[filtredShowMonitoring['STATUS'].isin(status)]
        with row5[1]:
            confirmation = component_filterMultiselect(showMonitoring, 'CONFIRMAÇÃO', "Confirmação dos SHOWS:")
            filtredShowMonitoring = filtredShowMonitoring[filtredShowMonitoring['CONFIRMAÇÃO'].isin(confirmation)]   
        
        component_plotDataframe(filtredShowMonitoring, 'Monitoramento de shows hoje e amanhã')

        temp = filtredShowMonitoring.groupby('STATUS').size().reset_index(name='QUANTIDADE')
    
        center = st.columns([1.5,2,1.5])
        with center[1]:
            plotPizzaChart(temp['STATUS'], temp['QUANTIDADE'], None)
        
    
    with tab3:
        row6 = st.columns(1)
        with row6[0]: component_plotDataframe(showToCancel, 'Shows para cancelar')

    with tab4:
        filtredShowMonitoring = showMonitoring.copy()
        filtredShowMonitoring = filtredShowMonitoring.drop(['HORÁRIO CHECKIN','OBSERVAÇÃO CHECKIN','HORÁRIO CHECKOUT','SOLICITAÇÃO DE CANCELAMENTO',
        'SINALIZOU PROBLEMA', 'OBSERVAÇÃO DO ARTISTA', 'STATUS MANUAL'], axis=1)

        row7 = st.columns(2)
        with row7[0]:
            status = component_filterMultiselect(showMonitoring, 'CONFIRMAÇÃO', "Proposta da semana recorrente")
            filtredShowMonitoring = filtredShowMonitoring[filtredShowMonitoring['CONFIRMAÇÃO'].isin(status)]

        with row7[1]:
            show_time = st.selectbox('Escolha um horário de Show:', ['Todos','Almoço','Happy Hour','Jantar'], index=0)
            filtredShowMonitoring = function_filter_hourly(filtredShowMonitoring, show_time)

        component_plotDataframe(filtredShowMonitoring[filtredShowMonitoring['STATUS'] == 'Pendente'], 'Shows Com Status Pendente')
        

class Showlighthouse():
    def render(self):
        self.data = {}
        self.data['showMonitoring'] = show_monitoring_today_and_tomorrow()
        self.data['nextShows'] = show_in_next_one_hour()
        self.data['showToCancel'] = show_to_cancel()
        #self.data['transfeeraStatementReport'] = get_statement_report()
        
        buildShowlighthouse(self.data['showMonitoring'], self.data['nextShows'], self.data['showToCancel']) #self.data['transfeeraStatementReport']

