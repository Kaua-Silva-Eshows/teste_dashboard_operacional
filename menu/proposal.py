import streamlit as st
from data.queries import show_monitoring_today_and_tomorrow
from menu.page import Page
from utils.components import *
from utils.functions import *

def buildProposal(showMonitoring):
    showMonitoring = function_get_today_data(showMonitoring.copy())
    showMonitoring = showMonitoring.drop(['OBSERVAÇÃO CHECKIN', 'HORÁRIO CHECKIN','SOLICITAÇÃO DE CANCELAMENTO',
        'SINALIZOU PROBLEMA', 'OBSERVAÇÃO DO ARTISTA', 'COMISSÃO', 'STATUS MANUAL', 'STATUS ESTABELECIMENTO'], axis=1)
    st.markdown('## Propostas')
    row1 = st.columns(5)

    tile = row1[0].container(border=True)
    num_line_showMonitoring = len(showMonitoring)
    tile.write(f"<p style='text-align: center;'>Propostas abertas hoje</br>{num_line_showMonitoring}</p>", unsafe_allow_html=True)

    tile = row1[1].container(border=True)
    num_line_showMonitoring = len(showMonitoring[showMonitoring['STATUS'] == 'Pendente'])
    tile.write(f"<p style='text-align: center;'>Propostas pendentes</br>{num_line_showMonitoring}</p>", unsafe_allow_html=True)

    tile = row1[2].container(border=True)
    num_line_showMonitoring = len(showMonitoring[showMonitoring['STATUS'] == 'Aceita'])
    tile.write(f"<p style='text-align: center;'>Propostas aceitas</br>{num_line_showMonitoring}</p>", unsafe_allow_html=True)

    tile = row1[3].container(border=True)
    num_line_showMonitoring = len(showMonitoring[showMonitoring['STATUS'] == 'Checkin Realizado'])
    tile.write(f"<p style='text-align: center;'>Check-in</br>{num_line_showMonitoring}</p>", unsafe_allow_html=True)

    tile = row1[4].container(border=True)
    num_line_showMonitoring = len(showMonitoring[showMonitoring['STATUS'] == 'Checkout Realizado'])
    tile.write(f"<p style='text-align: center;'>Check-out</br>{num_line_showMonitoring}</p>", unsafe_allow_html=True)

    row2 = st.columns(3)
    
    tile = row2[0].container(border=True)
    today_shows = showMonitoring['ESTABELECIMENTO'].nunique()
    tile.write(f"<p style='text-align: center;'>Casas com show hoje</br>{today_shows}</p>", unsafe_allow_html=True)

    tile = row2[1].container(border=True)
    today_artists_shows = showMonitoring['ARTISTA'].nunique()
    tile.write(f"<p style='text-align: center;'>Artistas com shows hoje</br>{today_artists_shows}</p>", unsafe_allow_html=True)

    tile = row2[2].container(border=True)
    quanty_0 = len(showMonitoring[showMonitoring['NÚMERO DE SHOWS'] == 0])
    quanty_1 = len(showMonitoring[showMonitoring['NÚMERO DE SHOWS'] == 1])
    tile.write(f"<p style='text-align: center;'>Artistas com show pela primeira vez</br>{quanty_0 + quanty_1}</p>", unsafe_allow_html=True)

    row3 = st.columns(3)
    filtredShowMonitoring = showMonitoring.copy()
    with row3[0]:
        confirmation = component_filterMultiselect(showMonitoring, 'CONFIRMAÇÃO', "Status da confirmação:")
        filtredShowMonitoring = filtredShowMonitoring[filtredShowMonitoring['CONFIRMAÇÃO'].isin(confirmation)]
    with row3[1]:
        status = component_filterMultiselect(showMonitoring, 'STATUS', "Proposta da semana recorrente")
        filtredShowMonitoring = filtredShowMonitoring[filtredShowMonitoring['STATUS'].isin(status)]
    
    component_plotDataframe(filtredShowMonitoring, 'Monitoramento de shows hoje')

    temp = filtredShowMonitoring.groupby('STATUS').size().reset_index(name='QUANTIDADE')
    
    center = st.columns([1.5,2,1.5])
    with center[1]:
        plotPizzaChart(temp['STATUS'], temp['QUANTIDADE'], None)
        
class Proposal ():
   def render(self):
        self.data = {}
        self.data['showMonitoring'] = show_monitoring_today_and_tomorrow()
        buildProposal(self.data['showMonitoring'])