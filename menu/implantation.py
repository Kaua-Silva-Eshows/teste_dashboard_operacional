import streamlit as st
from data.queries import *
from menu.page import Page
from utils.components import *
from utils.functions import *
import pandas as pd
from datetime import datetime, timedelta

def buildImplantation(newImplementation, implementationFirstProposal, imlementationOpportunity):
    st.markdown('## Implantações')

    tab1, tab2, tab3 = st.tabs(["Em implantação e Estabilização", "Primeira Proposta", "Oportunidades"])
    
    with tab1:    
        component_plotDataframe(newImplementation, "Em Implantação")
    
        temp = newImplementation.groupby('STATUS').size().reset_index(name='QUANTIDADE')

        center = st.columns([1.5,2,1.5])
        with center[1]:
            plotPizzaChart(temp['STATUS'], temp['QUANTIDADE'], None)

    with tab2:
        filterimplementationFirstProposal = implementationFirstProposal.drop(['ID CONTRATANTE','STATUS CADASTRO','OBS ERRO CADASTRO'], axis=1)
        component_plotDataframe(filterimplementationFirstProposal, "Primeira Proposta Da Casa")
        function_copy_dataframe_as_tsv(filterimplementationFirstProposal)
        
        row = st.columns(1)
        filterimplementationFirstProposal = implementationFirstProposal.drop(['GRUPO', 'KEY_ACCOUNT', 'ID PROPOSTA', 'STATUS DA PROPOSTA', 'DATA INÍCIO'], axis=1)
        with row[0]: 
            with st.expander("Mais Informações"):
                component_plotDataframe(filterimplementationFirstProposal, 'Visualizar Formulario')
                function_copy_dataframe_as_tsv(filterimplementationFirstProposal)

    with tab3:
        component_plotDataframe(imlementationOpportunity, 'Oportunidades')
        function_copy_dataframe_as_tsv(imlementationOpportunity)

class Implantation ():
    def render(self):
        self.data = {}
        self.data['newImplementation'] = new_implementation()
        self.data['implementationFirstProposal'] = implementation_first_proposal()
        self.data['imlementationOpportunity'] = imlementation_opportunity()

        buildImplantation(self.data['newImplementation'], self.data['implementationFirstProposal'], self.data['imlementationOpportunity'])