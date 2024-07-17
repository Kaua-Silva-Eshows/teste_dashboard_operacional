import streamlit as st
from menu.page import Page
from utils.components import *
from utils.functions import *
import pandas as pd
from datetime import datetime, timedelta

def buildOpportunity(proposalmap):
    st.markdown('## Oportunidades')

    row1 = st.columns(5)
    tile = row1[0].container(border=True)
    num_line_opportunity = len(proposalmap)
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

    component_plotDataframe(proposalmap, 'Mapa de Oportunidades')

class Opportunity (Page):
    def render(self):
        buildOpportunity(self.data['proposalMap'],)