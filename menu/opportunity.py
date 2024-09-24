import streamlit as st
from data.queries import proposal_map
from menu.page import Page
from utils.components import *
from utils.functions import *
import pandas as pd
from datetime import datetime, timedelta
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

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


    st.markdown(f"<h5 style='text-align: center; background-color: #ffb131; padding: 0.1em;'>TESTE</h5>", unsafe_allow_html=True)
    gb = GridOptionsBuilder.from_dataframe(proposalmap)
    gb.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)
    gb.configure_selection('multiple', use_checkbox=True)

    gb.configure_grid_options(localeText={
        'selectAll': 'Selecionar Todos',
        'resetFilter': 'Redefinir Filtro',
        'contains': 'Contém',
        'equals': 'É igual a',
        'notEquals': 'Não é igual a',
        'startsWith': 'Começa com',
        'endsWith': 'Termina com',
        'filterOoo': 'Filtro...',
        'filter': 'Filtro',
        'applyFilter': 'Aplicar Filtro',
        'cancelFilter': 'Cancelar',
        'clearFilter': 'Limpar Filtro',
    })


    for col in proposalmap.columns:
        gb.configure_column(col, filter=True, width=150)  # Ajuste o valor de width conforme necessário

    grid_options = gb.build()

    # Exibindo o DataFrame com filtros
    AgGrid(proposalmap, gridOptions=grid_options, enable_enterprise_modules=True, theme="streamlit")


class Opportunity ():
    def render(self):
        self.data = {}
        self.data['proposalMap'] = proposal_map()

        buildOpportunity(self.data['proposalMap'],)