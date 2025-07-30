import streamlit as st
from data.queries import *
from menu.page import Page
from utils.components import *
from utils.functions import *
import pandas as pd
from datetime import datetime, timedelta

def biuldArtistCancelation(artistCancelation, companieCancelation, artistCancelationDetailed, companieCancelationDetailed):
    st.markdown('## Cancelamento de Artistas')
    
    row = st.columns(5)
    with row [2]:
        day_Cancelation1 = st.date_input('Data Inicio:', value=datetime.today().date(), format='DD/MM/YYYY', key='day_ArtistCancelation1')
        
    with row [3]:
        day_Cancelation2 = st.date_input('Data Final:', value=datetime.today().date(), format='DD/MM/YYYY', key='day_ArtistCancelation2')

        day_companieCancelation = companie_cancelation(day_Cancelation1.strftime('%d/%m/%Y'),day_Cancelation2.strftime('%d/%m/%Y'))
        day_ArtistCancelation = artist_cancelation(day_Cancelation1.strftime('%d/%m/%Y'),day_Cancelation2.strftime('%d/%m/%Y'))

    with row[1]:
        name_group = st.selectbox("Buscar Grupo:", options=["Nenhum"] + list(day_companieCancelation['GRUPO'].unique()), placeholder="Selecione um Grupo", key='name_group')

    row1 = st.columns(2)
    with row1[0]:
        if name_group != 'Nenhum':
            filters = "ANd GC.NOME = '" + name_group + "'"
            day_ArtistCancelation = artist_cancelation(day_Cancelation1.strftime('%d/%m/%Y'),day_Cancelation2.strftime('%d/%m/%Y'), filters)
        else:
            filters = ''
        filtered_copy_artist, count = component_plotDataframe(day_ArtistCancelation, "Artistas")
        function_copy_dataframe_as_tsv(filtered_copy_artist)
        function_box_lenDf(len_df=count, df=filtered_copy_artist,y='-130', x='440', box_id='box2')
    
    with row1[1]:
        if name_group != 'Nenhum':
            #filtra as casas pelo grupo selecionado
            day_companieCancelation = day_companieCancelation[day_companieCancelation['GRUPO'] == name_group]            
        filtered_copy_companie, count = component_plotDataframe(day_companieCancelation, "Casas")
        function_copy_dataframe_as_tsv(filtered_copy_companie)
        function_box_lenDf(len_df=count, df=filtered_copy_companie,y='-130', x='440', box_id='box2')

    row2 = st.columns([1,1])
    with row2[0]:
        #Mesclar a coluna de id com o nome do artista id - artista
        day_ArtistCancelation['ARTISTA'] = day_ArtistCancelation['ID'].astype(str) + ' - ' + day_ArtistCancelation['ARTISTA']
        #faz o filtro baseado no grupo selecionado
        name_artist = st.selectbox("Buscar Artista:", options=["Nenhum"] + list(day_ArtistCancelation['ARTISTA'].unique()), placeholder="Selecione um Artista")
        if name_artist != 'Nenhum':#Pega somente o id do artista baseado no filtro
            id_artist = day_ArtistCancelation[day_ArtistCancelation['ARTISTA'] == name_artist]['ID'].iloc[0]

    with row2[1]:
        if name_group != 'Nenhum':
            #Filtra as casas pelo grupo selecionado
            filtered_copy_companie = filtered_copy_companie[filtered_copy_companie['GRUPO'] == name_group]
            name_companie = st.selectbox("Buscar Casa:", options=["Nenhum"] + list(filtered_copy_companie['CASA'].unique()), placeholder="Selecione uma Casa")
        else:
            name_companie = st.selectbox("Buscar Casa:", options=["Nenhum"] + list(filtered_copy_companie['CASA'].unique()), placeholder="Selecione uma Casa")    

    if name_artist != 'Nenhum':
        artistCancelation_Detailed = artist_cancelation_detailed(day_Cancelation1.strftime('%d/%m/%Y'),day_Cancelation2.strftime('%d/%m/%Y'), id_artist)
        filtered_copy_artist, count = component_plotDataframe(artistCancelation_Detailed, "Buscar Artistas")
        function_copy_dataframe_as_tsv(filtered_copy_artist)
        function_box_lenDf(len_df=count, df=filtered_copy_artist,y='-130', x='440', box_id='box2')

    filters = ''

    if name_group != 'Nenhum':
        filters += f" AND GC.NOME = '{name_group}'"

    if name_companie != 'Nenhum':
        filters += f" AND C.NAME = '{name_companie}'"

    if name_group != 'Nenhum' or name_companie != 'Nenhum':
        companieCancelation_Detailed = companie_cancelation_detailed(day_Cancelation1.strftime('%d/%m/%Y'),day_Cancelation2.strftime('%d/%m/%Y'), filters)
        filtered_copy_companie, count = component_plotDataframe(companieCancelation_Detailed, "Buscar Casas")
        function_copy_dataframe_as_tsv(filtered_copy_companie)
        function_box_lenDf(len_df=count, df=filtered_copy_companie,y='-130', x='440', box_id='box2')


class ArtistCancelation ():
    def render(self):
        self.data = {}
        day_ArtistCancelation1 = datetime.today().date()
        day_ArtistCancelation2 = datetime.today().date()
        name_artist = ''
        id_CompaniesCancelation = ''
        self.data['artistCancelation'] = artist_cancelation(day_ArtistCancelation1, day_ArtistCancelation2)
        self.data['companieCancelation'] = companie_cancelation(day_ArtistCancelation1, day_ArtistCancelation2)
        self.data['artistCancelationDetailed'] = artist_cancelation_detailed(day_ArtistCancelation1, day_ArtistCancelation2, name_artist)
        self.data['companieCancelationDetailed'] = companie_cancelation_detailed(day_ArtistCancelation1, day_ArtistCancelation2, id_CompaniesCancelation)

        biuldArtistCancelation(self.data['artistCancelation'], self.data['companieCancelation'], self.data['artistCancelationDetailed'], self.data['companieCancelationDetailed'])

