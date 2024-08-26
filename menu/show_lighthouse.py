from io import StringIO
import streamlit as st
from data.queries import *
from data.transfeeraconnect import get_statement_report
from menu.page import Page
from utils.components import *
from utils.functions import *
import pandas as pd
from datetime import date, datetime

def buildShowlighthouse(showMonitoring, nextShows, showToCancel, churnCompanies, newCompanies, housesImplementationStabilization): #, transfeeraStatementReport)
    st.markdown('## Shows confirmados')

    row1 = st.columns(5)
    filtredShowMonitoring = showMonitoring.copy()
    
    with row1[0]:
        data = component_filterDataSelect(key='selectbox_1')
        filtredShowMonitoring = function_get_today_tomorrow_date(filtredShowMonitoring, data)

    row2 = st.columns(3)
    filtered_df1 = filtredShowMonitoring['CONFIRMAÇÃO'] == 'Positiva'
    filtered_df2 = filtredShowMonitoring[filtered_df1]
    
    tile = row2[0].container(border=True)
    num_line_showMonitoring = len(filtered_df2)
    num_line_filtredShowMonitoring = len(filtredShowMonitoring)
    tile.write(f"<p style='text-align: center;'>Shows confirmados / Total de Shows</br>{ num_line_showMonitoring }/{ num_line_filtredShowMonitoring }</p>", unsafe_allow_html=True)

    tile = row2[1].container(border=True)
    filtredShowCancel = showToCancel.copy()
    filtredShowCancel = function_get_today_tomorrow_date(filtredShowCancel, data)
    num_line_showCancel = len(filtredShowCancel)
    tile.write(f"<p style='text-align: center;'>Shows cancelados</br>{num_line_showCancel}</p>", unsafe_allow_html=True)

    tile = row2[2].container(border=True)
    filtered_df1 = filtredShowMonitoring['STATUS'] == 'Pendente'
    filtered_df2 = filtredShowMonitoring[filtered_df1]
    num_line_showMonitoring = len(filtered_df2)
    tile.write(f"<p style='text-align: center;'>Shows com Status Pendente</br>{num_line_showMonitoring}</p>", unsafe_allow_html=True)


    row3 = st.columns(3)

    tile = row3[0].container(border=True)
    num_line_nextShows = len(nextShows)
    tile.write(f"<p style='text-align: center;'>Shows na Proxima 1 Hora.</br>{num_line_nextShows}</p>", unsafe_allow_html=True)

    tile = row3[1].container(border=True)
    filtered_df1 = filtredShowMonitoring['STATUS'] == 'Checkin Realizado'
    filtered_df2 = filtredShowMonitoring[filtered_df1]
    num_line_showMonitoring = len(filtered_df2)
    tile.write(f"<p style='text-align: center;'>Check-in</br>{num_line_showMonitoring}</p>", unsafe_allow_html=True)

    tile = row3[2].container(border=True)
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

    row5 = st.columns(1)
    artists_filtred = filtredShowMonitoring.drop(['STATUS', 'CIDADE', 'ENDEREÇO', 'HORÁRIO CHECKIN', 'OBSERVAÇÃO CHECKIN', 'HORÁRIO CHECKOUT',
    'SOLICITAÇÃO DE CANCELAMENTO', 'SINALIZOU PROBLEMA', 'NÚMERO DE SHOWS NA CASA', 'COMISSÃO', 'STATUS MANUAL', 'STATUS ESTABELECIMENTO'], axis=1)
    artists_filtred = artists_filtred[artists_filtred['NÚMERO DE SHOWS'] <= 1]
    artists_filtred = artists_filtred[['ID PROPOSTA', 'ARTISTA', 'ESTABELECIMENTO','DATA INÍCIO','HORÁRIO INÍCIO','HORÁRIO FIM','CELULAR DO ARTISTA','CONFIRMAÇÃO','OBSERVAÇÃO DO ARTISTA','NÚMERO DE SHOWS','VER DETALHES']]

    with row5[0]: 
        with st.expander("Visualizar Casas em Implantação e Estabilização"):
            component_plotDataframe(housesImplementationStabilization, 'Tabela de Casas em Implantação e Estabilização')
            function_copy_dataframe_as_tsv(housesImplementationStabilization)

    row6 = st.columns(1)

    with row6[0]: 
        with st.expander("Visualizar Artistas com shows pela Primeira vez"):
            component_plotDataframe(artists_filtred, 'Tabela De Artistas com shows pela Primeira vez')
            function_copy_dataframe_as_tsv(artists_filtred)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Shows na Proxima 1 Hora","Monitoramento de shows","Solicitação de Cancelamento de Show", "Shows Com Status Pendente","Relação Diaria das Casas"])
    
    with tab1:
        component_plotDataframe(nextShows, 'Shows na Proxima 1 Hora')
        function_copy_dataframe_as_tsv(nextShows)

    with tab2:
        row7 = st.columns(3)
        with row7[0]:
            status = component_filterMultiselect(showMonitoring, 'STATUS', "Proposta da semana recorrente:")
            filtredShowMonitoring = filtredShowMonitoring[filtredShowMonitoring['STATUS'].isin(status)]
        with row7[1]:
            confirmation = component_filterMultiselect(showMonitoring, 'CONFIRMAÇÃO', "Confirmação dos SHOWS:")
            filtredShowMonitoring = filtredShowMonitoring[filtredShowMonitoring['CONFIRMAÇÃO'].isin(confirmation)]   
        
        component_plotDataframe(filtredShowMonitoring, 'Monitoramento de shows hoje e amanhã')
        function_copy_dataframe_as_tsv(filtredShowMonitoring)

        temp = filtredShowMonitoring.groupby('STATUS').size().reset_index(name='QUANTIDADE')
    
        center = st.columns([1.5,2,1.5])
        with center[1]:
            plotPizzaChart(temp['STATUS'], temp['QUANTIDADE'], None)
        
    
    with tab3:
        row8 = st.columns(1)
        filtredshowToCancel = showToCancel.copy()
        filtredshowToCancel = function_get_today_tomorrow_date(filtredshowToCancel, data)
        with row8[0]: component_plotDataframe(filtredshowToCancel, 'Solicitação de Cancelamento de Show')
        function_copy_dataframe_as_tsv(filtredshowToCancel)

    with tab4:
        filtredShowMonitoring = filtredShowMonitoring.drop(['HORÁRIO CHECKIN','OBSERVAÇÃO CHECKIN','HORÁRIO CHECKOUT','SOLICITAÇÃO DE CANCELAMENTO',
        'SINALIZOU PROBLEMA', 'OBSERVAÇÃO DO ARTISTA', 'STATUS MANUAL'], axis=1)

        row9 = st.columns(2)
        with row9[0]:
            status = component_filterMultiselect(showMonitoring, 'CONFIRMAÇÃO', "Proposta da semana recorrente")
            filtredShowMonitoring = filtredShowMonitoring[filtredShowMonitoring['CONFIRMAÇÃO'].isin(status)]

        with row9[1]:
            show_time = st.selectbox('Escolha um horário de Show:', ['Todos','Almoço','Happy Hour','Jantar'], index=0)
            filtredShowMonitoring = function_filter_hourly(filtredShowMonitoring, show_time)

        component_plotDataframe(filtredShowMonitoring[filtredShowMonitoring['STATUS'] == 'Pendente'], 'Shows Com Status Pendente')
        function_copy_dataframe_as_tsv(filtredShowMonitoring[filtredShowMonitoring['STATUS'] == 'Pendente'])
    
    with tab5:
        row10 = st.columns(3)
        
        with row10 [1]:
            global day
            day = st.date_input('Escolha uma data', value=datetime.today().date(), format='DD/MM/YYYY') 

        row11 = st.columns(2)
        with row11[0]:

            churn_companies_data = churn_companies(day.strftime('%Y-%m-%d'))
            component_plotDataframe(churn_companies_data, 'Chrun do Dia')
        
        with row11[1]:
            new_companies_data = new_companies(day.strftime('%Y-%m-%d'))
            component_plotDataframe(new_companies_data, 'Casa Nova')


class Showlighthouse():
     
    def render(self):
        self.data = {}
        self.data['showMonitoring'] = show_monitoring_today_and_tomorrow()
        self.data['nextShows'] = show_in_next_one_hour()
        self.data['showToCancel'] = show_to_cancel()
        day = datetime.today().date().strftime('%Y-%m-%d')
        self.data['churnCompanies'] = churn_companies(day)
        self.data['newCompanies'] = new_companies(day)
        self.data['housesImplementationStabilization'] = houses_implementation_stabilization()
        #self.data['transfeeraStatementReport'] = get_statement_report()
        
        buildShowlighthouse(self.data['showMonitoring'],
                            self.data['nextShows'], 
                            self.data['showToCancel'], 
                            self.data['churnCompanies'], 
                            self.data['newCompanies'], 
                            self.data['housesImplementationStabilization']) 
                            #self.data['transfeeraStatementReport']

