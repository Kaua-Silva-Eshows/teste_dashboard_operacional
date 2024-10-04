import streamlit as st
from data.queries import *
from menu.page import Page
from utils.components import *
from utils.functions import *
import pandas as pd
from datetime import datetime, timedelta

def buildImplantation(newImplementation, implementationFirstProposal, imlementationOpportunity):
    st.markdown('## Implantações')

    tab1, tab2, tab3 = st.tabs(["Em implantação e Estabilização", "Oportunidades", "Primeira Proposta"])
    
    with tab1: 
        newImplementation = newImplementation.drop(['CASA ID'], axis=1) 
        newImplementation['CREATED AT'] = pd.to_datetime(newImplementation['CREATED AT'], format='%d/%m/%Y')
        
        filtered_copy = component_plotDataframe(newImplementation, "Em Implantação")
        function_copy_dataframe_as_tsv(filtered_copy)
        function_box_lenDf(len_df=len(newImplementation),df=newImplementation,y='-100', x='500', box_id='box1')
        
        row = st.columns(1)
        filterimplementationFirstProposal = implementationFirstProposal.drop(['GRUPO', 'KEY ACCOUNT', 'ID PROPOSTA', 'STATUS DA PROPOSTA','ARTISTA', 'DATA E HORA'], axis=1)
        with row[0]: 
            with st.expander("Mais Informações"):
                filtered_df = filterimplementationFirstProposal.drop_duplicates(subset='CASA')
                filtered_copy = component_plotDataframe(filtered_df, 'Informações Formulario')
                function_copy_dataframe_as_tsv(filtered_copy)
                function_box_lenDf(len_df=len(filtered_df),df=filtered_df,y='-100', x='500', box_id='box1')
            
        temp = newImplementation.groupby('STATUS').size().reset_index(name='QUANTIDADE')

        center = st.columns([1.5,2,1.5])
        with center[1]:
            plotPizzaChart(temp['STATUS'], temp['QUANTIDADE'], None)

    with tab2:
        imlementationOpportunity = imlementationOpportunity.drop(['CASA ID'], axis=1)
        imlementationOpportunity['VER CANDIDATOS'] = imlementationOpportunity['VER CANDIDATOS'].str.replace('SAIBA MAIS', 'VER MAIS')
        imlementationOpportunity = imlementationOpportunity[imlementationOpportunity['ID OPORTUNIDADE'] != '—']
        filtered_copy = component_plotDataframe(imlementationOpportunity, 'Oportunidades')
        function_copy_dataframe_as_tsv(filtered_copy)
        function_box_lenDf(len_df=len(imlementationOpportunity),df=imlementationOpportunity,y='-100', x='500', box_id='box1')
        

    with tab3:
        
        filterimplementationFirstProposal = implementationFirstProposal[['STATUS', 'GRUPO', 'CASA', 'KEY ACCOUNT', 'ID PROPOSTA', 'DATA E HORA','ARTISTA', 'STATUS DA PROPOSTA']]
        filterimplementationFirstProposal = filterimplementationFirstProposal[filterimplementationFirstProposal['ID PROPOSTA'] != '—']

        # row1 = st.columns(2)
        # with row1[0]:
        #     establishment = ['Todos'] + filterimplementationFirstProposal['CASA'].unique().tolist()
        #     filter_establishment = st.selectbox('Escolha a Casa:', establishment, index=0)
        # if filter_establishment == 'Todos':
        #     filterimplementationFirstProposal = filterimplementationFirstProposal
        # else:
        #     filterimplementationFirstProposal = filterimplementationFirstProposal[filterimplementationFirstProposal['CASA'] == filter_establishment]
        filtered_copy = component_plotDataframe(filterimplementationFirstProposal, "Primeira Proposta Da Casa")
        function_copy_dataframe_as_tsv(filtered_copy)
        function_box_lenDf(len_df=len(filterimplementationFirstProposal),df=filterimplementationFirstProposal,y='-100', x='500', box_id='box1')
        
        
class Implantation ():
    def render(self):
        self.data = {}
        self.data['newImplementation'] = new_implementation()
        self.data['implementationFirstProposal'] = implementation_first_proposal()
        self.data['imlementationOpportunity'] = imlementation_opportunity()

        buildImplantation(self.data['newImplementation'], self.data['implementationFirstProposal'], self.data['imlementationOpportunity'])