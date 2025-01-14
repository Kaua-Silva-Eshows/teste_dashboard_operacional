import streamlit as st
from data.queries import *
from menu.page import Page
from utils.components import *
from utils.functions import *
import pandas as pd
from datetime import datetime, timedelta

def biuldArtistCancelation(artistCancelation, companieCancelation, artistCancelationDetailed, companieCancelationDetailed):
    st.markdown('## Cancelamento de Artistas')
    
    row = st.columns(4)
    with row [1]:
        day_Cancelation1 = st.date_input('Data Inicio:', value=datetime.today().date(), format='DD/MM/YYYY', key='day_ArtistCancelation1')
        
    with row [2]:
        day_Cancelation2 = st.date_input('Data Final:', value=datetime.today().date(), format='DD/MM/YYYY', key='day_ArtistCancelation2')


    row1 = st.columns(2)
    with row1[0]:
        day_ArtistCancelation = artist_cancelation(day_Cancelation1.strftime('%d/%m/%Y'),day_Cancelation2.strftime('%d/%m/%Y'))
        filtered_copy_artist, count = component_plotDataframe(day_ArtistCancelation, "Artistas")
        function_copy_dataframe_as_tsv(filtered_copy_artist)
        function_box_lenDf(len_df=count, df=filtered_copy_artist,y='-130', x='440', box_id='box2')
    
    with row1[1]:
        day_companieCancelation = companie_cancelation(day_Cancelation1.strftime('%d/%m/%Y'),day_Cancelation2.strftime('%d/%m/%Y'))
        filtered_copy_companie, count = component_plotDataframe(day_companieCancelation, "Casas")
        function_copy_dataframe_as_tsv(filtered_copy_companie)
        function_box_lenDf(len_df=count, df=filtered_copy_companie,y='-130', x='440', box_id='box2')

    row2 = st.columns(2)
    with row2[0]:
        name_artist = st.selectbox("Buscar Artista:", options=["Nenhum"] + list(filtered_copy_artist['ARTISTA'].unique()), placeholder="Selecione um Artista"
)        
    with row2[1]:
        name_companie = st.selectbox("Buscar Casa:", options=["Nenhum"] + list(filtered_copy_companie['CASA'].unique()), placeholder="Selecione uma Casa")


    if name_artist != 'Nenhum':
        artistCancelation_Detailed = artist_cancelation_detailed(day_Cancelation1.strftime('%d/%m/%Y'),day_Cancelation2.strftime('%d/%m/%Y'), name_artist)
        filtered_copy_artist, count = component_plotDataframe(artistCancelation_Detailed, "Artistas")
        function_copy_dataframe_as_tsv(filtered_copy_artist)
        function_box_lenDf(len_df=count, df=filtered_copy_artist,y='-130', x='440', box_id='box2')

    if name_companie != 'Nenhum':
        companieCancelation_Detailed = companie_cancelation_detailed(day_Cancelation1.strftime('%d/%m/%Y'),day_Cancelation2.strftime('%d/%m/%Y'), name_companie)
        filtered_copy_companie, count = component_plotDataframe(companieCancelation_Detailed, "Casas")
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

