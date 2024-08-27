import streamlit as st
from data.queries import *
from menu.page import Page
from utils.components import *
from utils.functions import *
import pandas as pd
from datetime import datetime, timedelta
import os

def buildHole(holemap, holeWithProposals, defaultShowToDo):
    # file_path = "./assets/csvs/holemap.csv"
    # if not os.path.exists(file_path):
    #     columns = holemap[['ID PROPOSTA', 'LAST_UPDATE']]
    #     columns['OUTPUT_DATE'] = None
    #     columns.to_csv(file_path, index=False)

    # csv = pd.read_csv(file_path)
    # csv = function_update_csv(holemap, csv)

    # missing_records = function_add_outputdate_in_solved_itens(holemap, csv)
    # missing_records.to_csv(file_path, index=False)
    
    st.markdown('## Buracos')

    row1 = st.columns([1,1,1,1.5])
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
    
    # row2 = st.columns([4,1.5])
    # with row2[1]:
    #     choice_time = st.columns([1, 4.8, 1])[1].radio(label="", options=["Hora", "Semana", "Mês"], index=None, horizontal=True, label_visibility='collapsed')
    # avarege_time = function_calculate_average_hole_time(missing_records, choice_time)

    # tile = row1[4].container(border=True)
    # tile.write(f"<p style='text-align: center;'>Tempo Médio Para Preencher Buracos</br>{format_timedelta_to_pt_br(avarege_time)}</p>", unsafe_allow_html=True) 
    
    row3 = st.columns(2)
    with row3[0]:
        acconty = component_filterMultiselect(holemap, 'KEY_ACCOUNT', "Nomes")
        filtredAcconty = (holemap[holemap['KEY_ACCOUNT'].isin(acconty)])

    with row3[1]:
        observation = component_filterMultiselect(holemap, 'OBSERVAÇÃO', "Observações")
        filtredAcconty = (holemap[holemap['OBSERVAÇÃO'].isin(observation)])

    tab1, tab2, tab3= st.tabs(["Buracos de Hoje","Buracos de Amanhã","Todos os Buracos"])

    with tab1:
        row3 = st.columns(1)
        today = datetime.now().date()
        with row3[0]:
            component_plotDataframe(filtredAcconty[filtredAcconty['DATA INÍCIO'] == today.strftime('%d/%m')], 'Tabela Buracos Hoje') 
            function_copy_dataframe_as_tsv(filtredAcconty[filtredAcconty['DATA INÍCIO'] == today.strftime('%d/%m')])

    with tab2:
        row4 = st.columns(1)
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        with row4[0]: component_plotDataframe(filtredAcconty[filtredAcconty['DATA INÍCIO'] == tomorrow.strftime('%d/%m')], 'Tabela Buracos Amanhã')
        function_copy_dataframe_as_tsv(filtredAcconty[filtredAcconty['DATA INÍCIO'] == tomorrow.strftime('%d/%m')])

    with tab3:
        row5 = st.columns(1)
        with row5[0]: component_plotDataframe(filtredAcconty, 'Tabela Buracos')
        function_copy_dataframe_as_tsv(filtredAcconty) 

        with st.expander("Visualizar Pendências"): 
            holeWithProposals = holeWithProposals[['ESTABELECIMENTO', 'NOME ARTISTA', 'KEY_ACCOUNT', 'ID OPORTUNIDADE', 'ID PROPOSTA', 'LINK DA OPORTUNIDADE', 'VER PROPOSTA ORIGINAL','STATUS ESTABELECIMENTO']]
            component_plotDataframe(holeWithProposals, 'Tabela de Buracos com Oportunidades')
            function_copy_dataframe_as_tsv(holeWithProposals)

        with st.expander("Visualizar Pendências Shows Padrão"):

            grouped = defaultShowToDo.copy().groupby(['Estabelecimento Show Padrão', 'Data Inicio Proposta']).size().reset_index(name='Count')

            repeated_dates = grouped[grouped['Count'] > 1]

            filtered_dates_df = pd.merge(defaultShowToDo, repeated_dates[['Estabelecimento Show Padrão', 'Data Inicio Proposta']], on=['Estabelecimento Show Padrão', 'Data Inicio Proposta'])

            # Aplicar a função para encontrar as sobreposições
            filtered_df = find_overlaps(filtered_dates_df)


            component_plotDataframe(filtered_df, 'Tabela Shows Padrão com Proposta')

            function_copy_dataframe_as_tsv(filtered_df)

class Hole ():
    def render(self):
        self.data = {}
        self.data['holemap'] = function_rename_holemap()
        self.data['holeWithProposals'] = holes_with_proposals()
        self.data['defaultShowToDo'] = default_show_to_do()

        buildHole(self.data['holemap'], self.data['holeWithProposals'], self.data['defaultShowToDo'])