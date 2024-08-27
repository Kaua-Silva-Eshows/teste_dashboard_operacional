import pandas as pd
import streamlit as st
from data.queries import *
from data.transfeeraconnect import get_statement_report
from utils.functions import *

# Inicializa os valores de data
def initialize_data(id):
    # Dicionário com dados de entrada
    data = {
        'showMonitoring' : pd.DataFrame(),
        'nextShows' : pd.DataFrame(),
        'showToCancel' : pd.DataFrame(),
        'holeMap' : pd.DataFrame(),
        'proposalMap' : pd.DataFrame(),
        'artistFavoriteBlocked' : pd.DataFrame(),
        'transfeeraStatementReport' : pd.DataFrame(),
        'holeWithProposals' : pd.DataFrame(),
        'defaultShowToDo' : pd.DataFrame(),
        'churnCompanies' : pd.DataFrame(),
        'newCompanies' : pd.DataFrame(),
        'housesImplementationStabilization' : pd.DataFrame(),
        'newImplementation' : pd.DataFrame(),
        'id':id
    }

    return data

# def get_data(data):
#     try:
#         data['showMonitoring'] = show_monitoring_today_and_tomorrow()
#     except Exception as e:
#         st.error('Não foi possível acessar os dados de monitoramento.')

#     try:
#         data['nextShows'] = show_in_next_thirty_minutes()
#     except Exception as e:
#         st.error('Não foi possível acessar os dados de próximos shows.')

#     try:
#         data['showToCancel'] = show_to_cancel()
#     except Exception as e:
#         st.error('Não foi possível acessar os dados de show para cancelar.')

#     try:
#         data['holemap'] = function_rename_holemap()
#     except Exception as e:
#         st.error('Não foi possível acessar os dados de mapa de buracos')
#     try:
#         data['proposalMap'] = proposal_map()
#     except Exception as e:
#         st.error('Não foi possível acessar os dados de mapa de propostas.')

#     # try:
#     #     data['artistFavoriteBlocked'] = artist_favorite_blocked()
#     # except Exception as e:
#     #     st.error('Não foi possível acessar os dados de Artistas Favoritos e Bloqueados')
    
#     try:
#         data['transfeeraStatementReport'] = get_statement_report()
#     except Exception as e:
#         st.error('Não foi possível acessar os dados do Transfeera')

#     try:
#         data['holeWithProposals'] = holes_with_proposals()
#     except Exception as e:
#         st.error('Não foi possível acessar os dados de Buracos com Propostas')
    
#     return data