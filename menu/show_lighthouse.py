from io import StringIO
import streamlit as st
from data.queries import *
from data.transfeeraconnect import get_statement_report
from menu.page import Page
from utils.components import *
from utils.functions import *
import pandas as pd
from datetime import date, datetime
from st_aggrid import AgGrid

def buildShowlighthouse(showMonitoring, nextShows, showToCancel, churnCompanies, newCompanies, housesImplementationStabilization): #, transfeeraStatementReport)
    st.markdown('## Shows confirmados')

    row1 = st.columns(6)
    
    with row1[2]:
        global day_ShowMonitoring1, day_ShowMonitoring2
        day_ShowMonitoring1 = st.date_input('Data Inicio:', value=datetime.today().date(), format='DD/MM/YYYY', key='day_ShowMonitoring1') 
    with row1[3]:
        day_ShowMonitoring2 = st.date_input('Data Final:', value=datetime.today().date(), format='DD/MM/YYYY', key='day_ShowMonitoring2') 

    row2 = st.columns(3)
    showMonitoring = show_monitoring_today_and_tomorrow(day_ShowMonitoring1, day_ShowMonitoring2)
    filtredShowMonitoring = showMonitoring.copy()

    filtered_df1 = filtredShowMonitoring['CONFIRMAÇÃO'] == 'Positiva'
    filtered_df2 = filtredShowMonitoring[filtered_df1]
    tile = row2[0].container(border=True)
    num_line_showMonitoring = len(filtered_df2)
    num_line_filtredShowMonitoring = len(filtredShowMonitoring)
    tile.write(f"<p style='text-align: center;'>Shows confirmados / Total de Shows</br>{ num_line_showMonitoring }/{ num_line_filtredShowMonitoring }</p>", unsafe_allow_html=True)

    tile = row2[1].container(border=True)
    showToCancel = show_to_cancel(day_ShowMonitoring1, day_ShowMonitoring2)
    filtredShowCancel = showToCancel.copy()
    num_line_showCancel = len(filtredShowCancel)
    tile.write(f"<p style='text-align: center;'>Shows cancelados</br>{num_line_showCancel}</p>", unsafe_allow_html=True)

    tile = row2[2].container(border=True)
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

    row5 = st.columns(1)
    artists_filtred = filtredShowMonitoring.drop(['STATUS', 'CIDADE', 'ENDEREÇO', 'HORÁRIO CHECKIN', 'OBSERVAÇÃO CHECKIN', 'HORÁRIO CHECKOUT',
    'SOLICITAÇÃO DE CANCELAMENTO', 'SINALIZOU PROBLEMA', 'NÚMERO DE SHOWS NA CASA', 'COMISSÃO', 'STATUS MANUAL', 'STATUS ESTABELECIMENTO'], axis=1)
    artists_filtred = artists_filtred[artists_filtred['NÚMERO DE SHOWS'] <= 1]
    artists_filtred = artists_filtred[['ID PROPOSTA', 'ARTISTA', 'ESTABELECIMENTO','DATA INÍCIO','HORÁRIO INÍCIO','HORÁRIO FIM','CELULAR DO ARTISTA','CONFIRMAÇÃO','VER DETALHES']]

    with row5[0]: 
        with st.expander("Visualizar Casas em Implantação e Estabilização"):
            filtered_copy = component_plotDataframe(housesImplementationStabilization, 'Tabela de Casas em Implantação e Estabilização')
            function_copy_dataframe_as_tsv(filtered_copy)
            function_box_lenDf(len_df=len(housesImplementationStabilization),df=housesImplementationStabilization,y='-100', x='500', box_id='box1')

    row6 = st.columns(1)

    with row6[0]: 
        with st.expander("Visualizar Artistas com shows pela Primeira vez"):
            filtered_copy = component_plotDataframe(artists_filtred, 'Tabela De Artistas com shows pela Primeira vez')
            function_copy_dataframe_as_tsv(filtered_copy)
            function_box_lenDf(len_df=len(artists_filtred),df=artists_filtred,y='-100', x='500',box_id='box1')

    tab1, tab2, tab3, tab4, tab5= st.tabs(["Shows na Proxima 1 Hora","Monitoramento de shows","Solicitação de Cancelamento de Show", "Shows Com Status Pendente","Recorrência das Casas"])
    
    with tab1:
        
        row3 = st.columns(5)
        tile = row3[2].container(border=True)
        num_line_nextShows = len(nextShows)
        tile.write(f"<p style='text-align: center;'>Shows na Proxima 1 Hora.</br>{num_line_nextShows}</p>", unsafe_allow_html=True)

        filtered_copy = component_plotDataframe(nextShows, 'Shows na Proxima 1 Hora')
        function_copy_dataframe_as_tsv(filtered_copy)
        function_box_lenDf(len_df=len(nextShows),df=nextShows,y='-100', x='500', box_id='box1')

    with tab2:
        # row7 = st.columns(2)
        # with row7[0]:
        #     status = component_filterMultiselect(showMonitoring, 'STATUS', "Proposta da semana recorrente:")
        #     filtredShowMonitoring = filtredShowMonitoring[filtredShowMonitoring['STATUS'].isin(status)]
            
        # with row7[1]:
        #     confirmation = component_filterMultiselect(showMonitoring, 'CONFIRMAÇÃO', "Confirmação dos SHOWS:")
        #     filtredShowMonitoring = filtredShowMonitoring[filtredShowMonitoring['CONFIRMAÇÃO'].isin(confirmation)]   

        filtered_copy = component_plotDataframe(filtredShowMonitoring, 'Monitoramento de shows')
        function_copy_dataframe_as_tsv(filtered_copy)
        function_box_lenDf(len_df=len(filtredShowMonitoring),df=filtredShowMonitoring,y='-100', x='500', box_id='box1')

        temp = filtredShowMonitoring.groupby('STATUS').size().reset_index(name='QUANTIDADE')
    
        center = st.columns([1.5,2,1.5])
        with center[1]:
            plotPizzaChart(temp['STATUS'], temp['QUANTIDADE'], None)
        
    
    with tab3:
        row8 = st.columns(1)
        filtredShowCancel = filtredShowCancel[['DATA INÍCIO', 'HORÁRIO INÍCIO', 'ÚLTIMA ATUALIZAÇÃO', 'ESTABELECIMENTO', 'ARTISTA', 'FORMAÇÃO', 'MOTIVO',
                                                   'DESCRIÇÃO DO CANCELAMENTO','STATUS ESTABALECIMENTO', 'VER DETALHES' ]]
        
        with row8[0]: 
            filtered_copy = component_plotDataframe(filtredShowCancel, 'Solicitação de Cancelamento de Show')
        function_copy_dataframe_as_tsv(filtered_copy)
        function_box_lenDf(len_df=len(filtredShowCancel),df=filtredShowCancel,y='-100', x='500', box_id='box1')

    with tab4:
        row9 = st.columns(2)
        filtredShowMonitoring = filtredShowMonitoring.drop(['HORÁRIO CHECKIN','OBSERVAÇÃO CHECKIN','HORÁRIO CHECKOUT','SOLICITAÇÃO DE CANCELAMENTO',
        'SINALIZOU PROBLEMA', 'OBSERVAÇÃO DO ARTISTA', 'STATUS MANUAL'], axis=1)

        with row9[0]:
            show_time = st.selectbox('Escolha um horário de Show:', ['Todos','Almoço','Happy Hour','Jantar'], index=0)
            filtredShowMonitoring = function_filter_hourly(filtredShowMonitoring, show_time)

        filtered_copy = component_plotDataframe(filtredShowMonitoring[filtredShowMonitoring['STATUS'] == 'Pendente'], 'Shows Com Status Pendente')
        function_copy_dataframe_as_tsv(filtered_copy[filtered_copy['STATUS'] == 'Pendente'])
        function_box_lenDf(len_df=len((filtredShowMonitoring[filtredShowMonitoring['STATUS'] == 'Pendente'])),df=(filtredShowMonitoring[filtredShowMonitoring['STATUS'] == 'Pendente']),y='-100', x='500', box_id='box1')
    
    with tab5:
        row10 = st.columns(3)
        
        with row10 [1]:
            global day_churn_new
            day_churn_new = st.date_input('Escolha uma data', value=datetime.today().date(), format='DD/MM/YYYY') 

        row11 = st.columns(2)
        with row11[0]:

            churn_companies_data = churn_companies(day_churn_new.strftime('%Y-%m-%d'))
            filtered_copy = component_plotDataframe(churn_companies_data, "Sem Recorrência")
            function_copy_dataframe_as_tsv(filtered_copy)
            function_box_lenDf(len_df=len(churn_companies_data),df=churn_companies_data,y='-130', x='440', box_id='box2')
        
        with row11[1]:
            new_companies_data = new_companies(day_churn_new.strftime('%Y-%m-%d'))
            filtered_copy = component_plotDataframe(new_companies_data, "Buscar Recorrência")
            function_copy_dataframe_as_tsv(filtered_copy)
            function_box_lenDf(len_df=len(new_companies_data),df=new_companies_data,y='-130', x='440', box_id='box2')
        
class Showlighthouse():
     
    def render(self):
        self.data = {}
        day_ShowMonitoring1 = datetime.today().date()
        day_ShowMonitoring2 = datetime.today().date()
        day_churn_new = datetime.today().date().strftime('%Y-%m-%d')
        self.data['showMonitoring'] = show_monitoring_today_and_tomorrow(day_ShowMonitoring1, day_ShowMonitoring2)
        self.data['nextShows'] = show_in_next_one_hour()
        self.data['showToCancel'] = show_to_cancel(day_ShowMonitoring1, day_ShowMonitoring2)
        self.data['churnCompanies'] = churn_companies(day_churn_new)
        self.data['newCompanies'] = new_companies(day_churn_new)
        self.data['housesImplementationStabilization'] = houses_implementation_stabilization()
        #self.data['transfeeraStatementReport'] = get_statement_report()
        
        buildShowlighthouse(self.data['showMonitoring'],
                            self.data['nextShows'], 
                            self.data['showToCancel'], 
                            self.data['churnCompanies'], 
                            self.data['newCompanies'], 
                            self.data['housesImplementationStabilization']) 
                            #self.data['transfeeraStatementReport']