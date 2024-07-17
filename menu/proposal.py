import streamlit as st
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
    num_line_showMonitoring = len(showMonitoring[showMonitoring['STATUS'] == 'Checkin'])
    tile.write(f"<p style='text-align: center;'>Check-in</br>{num_line_showMonitoring}</p>", unsafe_allow_html=True)

    tile = row1[4].container(border=True)
    num_line_showMonitoring = len(showMonitoring[showMonitoring['STATUS'] == 'Checkout'])
    tile.write(f"<p style='text-align: center;'>Check-out</br>{num_line_showMonitoring}</p>", unsafe_allow_html=True)
    
    row2 = st.columns(3)
    filtredShowMonitoring = showMonitoring.copy()
    with row2[0]:
        confirmation = component_filterMultiselect(showMonitoring, 'CONFIRMAÇÃO', "Status da confirmação:")
        filtredShowMonitoring = filtredShowMonitoring[filtredShowMonitoring['CONFIRMAÇÃO'].isin(confirmation)]
    with row2[1]:
        status = component_filterMultiselect(showMonitoring, 'STATUS', "Proposta da semana recorrente")
        filtredShowMonitoring = filtredShowMonitoring[filtredShowMonitoring['STATUS'].isin(status)]
    
    component_plotDataframe(filtredShowMonitoring, 'Monitoramento de shows hoje')

    temp = filtredShowMonitoring.groupby('STATUS').size().reset_index(name='QUANTIDADE')
    
    center = st.columns([1.5,2,1.5])
    with center[1]:
        plotPizzaChart(temp['STATUS'], temp['QUANTIDADE'], None)
        
class Proposal (Page):
    def render(self):
        buildProposal(self.data['showMonitoring'])