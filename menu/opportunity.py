import streamlit as st
from data.queries import proposal_map
from menu.page import Page
from utils.components import *
from utils.functions import *
import pandas as pd
from datetime import datetime, timedelta

def buildOpportunity(proposalmap):
    st.markdown('## Oportunidades')

    row = st.columns(6)
    with row[2]:
        global day_Proposal1, day_Proposal2
        day_Proposal1 = st.date_input('Data Início:', value=datetime.today().date(), format='DD/MM/YYYY', key="Proposal1") 
    with row[3]:
        day_Proposal2 = st.date_input('Data Final:', value=datetime.today().date(), format='DD/MM/YYYY', key="Proposal2")

    
    proposalmap = proposal_map(day_Proposal1, day_Proposal2)
    filtredproposalmap = proposalmap.copy()

    row1 = st.columns(5)
    tile = row1[0].container(border=True)

    # proposalmap['DATA INÍCIO'] = pd.to_datetime(proposalmap['DATA INÍCIO'], format='%d/%m/%Y', errors='coerce')
    # today = datetime.today().date()
    # filtered_df = proposalmap[(proposalmap['DATA INÍCIO'].dt.date == today)]
    # proposalmap['DATA INÍCIO'] = proposalmap['DATA INÍCIO'].dt.strftime('%d/%m/%Y')
    
    num_line_opportunity = len(proposalmap)
    num_line_opportunity_closed = len(proposalmap[proposalmap['STATUS'] == 'Encerrada'])
    tile.write(f"<p style='text-align: center;'>Encerradas / Oportunidades</br>{ num_line_opportunity_closed } / { num_line_opportunity }</p>", unsafe_allow_html=True)
    
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
    tile.write(f"<p style='text-align: center;'>Nº de Propostas Confirmadas</br>{num_line_opportunity}</p>", unsafe_allow_html=True)

    #row3 = st.columns(3)
    # with row3[0]:
    #     establishment = ['Todos'] + filtredproposalmap['ESTABELECIMENTO'].unique().tolist()
    #     establishment = sorted(establishment)
    #     establishment.insert(0,"Todos")
    #     filter_establishment = st.selectbox('Escolha o Estabelecimento:', establishment, index=0)
    # if filter_establishment == 'Todos':
    #     filtredproposalmap = filtredproposalmap
    # else:
    #     filtredproposalmap = filtredproposalmap[filtredproposalmap['ESTABELECIMENTO'] == filter_establishment]

    # with row3[1]:
    #     status = component_filterMultiselect(proposalmap, 'STATUS', "Status da Oportunidade:")
    #     filtredproposalmap = filtredproposalmap[filtredproposalmap['STATUS'].isin(status)]
    
    filtered_copy = component_plotDataframe(filtredproposalmap, 'Mapa de Oportunidades')
    function_copy_dataframe_as_tsv(filtered_copy)
    function_box_lenDf(len_df=len(filtredproposalmap),df=filtredproposalmap,y='-100', x='500', box_id='box1')

class Opportunity ():
    def render(self):
        self.data = {}
        day_Proposal1 = datetime.today().date()
        day_Proposal2 = datetime.today().date()
        self.data['proposalMap'] = proposal_map(day_Proposal1, day_Proposal2)

        buildOpportunity(self.data['proposalMap'],)