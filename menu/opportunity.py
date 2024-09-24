import streamlit as st
from data.queries import proposal_map
from menu.page import Page
from utils.components import *
from utils.functions import *
import pandas as pd
from datetime import datetime, timedelta

def buildOpportunity(proposalmap):
    st.markdown('## Oportunidades')

    row1 = st.columns(5)
    tile = row1[0].container(border=True)

    proposalmap['DATA INÍCIO'] = pd.to_datetime(proposalmap['DATA INÍCIO'], format='%d/%m/%Y', errors='coerce')
    today = datetime.today().date()
    filtered_df = proposalmap[(proposalmap['DATA INÍCIO'].dt.date == today)]
    proposalmap['DATA INÍCIO'] = proposalmap['DATA INÍCIO'].dt.strftime('%d/%m/%Y')
    
    num_line_opportunity = len(filtered_df)
    tile.write(f"<p style='text-align: center;'>Oportunidades Hoje</br>{num_line_opportunity}</p>", unsafe_allow_html=True)
    
    tile = row1[1].container(border=True)

    num_line_opportunity = len(proposalmap[proposalmap['STATUS'] == 'Aberta'])
    tile.write(f"<p style='text-align: center;'>Oportunidades Abertas</br>{num_line_opportunity}</p>", unsafe_allow_html=True)
    
    tile = row1[2].container(border=True)
    num_line_opportunity = len(proposalmap[proposalmap['STATUS'] == 'Aguardando Artista'])
    tile.write(f"<p style='text-align: center;'>Aguardando Artista</br>{num_line_opportunity}</p>", unsafe_allow_html=True)
    
    tile = row1[3].container(border=True)
    num_line_opportunity = len(proposalmap[proposalmap['STATUS'] == 'Aguardando Contratante'])
    tile.write(f"<p style='text-align: center;'>Aguardando Contratante</br>{num_line_opportunity}</p>", unsafe_allow_html=True)
    
    tile = row1[4].container(border=True)
    num_line_opportunity = len(proposalmap[proposalmap['ORIGEM RELÂMPAGO'] == 'sim'])
    tile.write(f"<p style='text-align: center;'>Oportunidades Relampago</br>{num_line_opportunity}</p>", unsafe_allow_html=True)
    
    row2 = st.columns(1)
    tile = row2[0].container(border=True)
    num_line_opportunity = len(proposalmap[proposalmap['STATUS_PROPOSTA'] == 'Aceita'])
    tile.write(f"<p style='text-align: center;'>Nº de Propostas Confirmadas Hoje</br>{num_line_opportunity}</p>", unsafe_allow_html=True)

    row3 = st.columns(3)
    filtredproposalmap = proposalmap.copy()
    with row3[0]:
        establishment = ['Todos'] + filtredproposalmap['ESTABELECIMENTO'].unique().tolist()
        establishment = sorted(establishment)
        establishment.insert(0,"Todos")
        filter_establishment = st.selectbox('Escolha o Estabelecimento:', establishment, index=0)
    if filter_establishment == 'Todos':
        filtredproposalmap = filtredproposalmap
    else:
        filtredproposalmap = filtredproposalmap[filtredproposalmap['ESTABELECIMENTO'] == filter_establishment]

    with row3[1]:
        status = component_filterMultiselect(proposalmap, 'STATUS', "Status da Oportunidade:")
        filtredproposalmap = filtredproposalmap[filtredproposalmap['STATUS'].isin(status)]
    
    with row3[2]:
        data = component_filterDataSelect(key='selectbox_2')
        filtredproposalmap = function_get_today_tomorrow_date(filtredproposalmap, data)
    
    component_plotDataframe(filtredproposalmap, 'Mapa de Oportunidades')
    function_copy_dataframe_as_tsv(filtredproposalmap)
    function_box_lenDf(len_df=len(filtredproposalmap),df=filtredproposalmap,y='-100', x='500', box_id='box1')

class Opportunity ():
    def render(self):
        self.data = {}
        self.data['proposalMap'] = proposal_map()

        buildOpportunity(self.data['proposalMap'],)