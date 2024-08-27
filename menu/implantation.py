import streamlit as st
from data.queries import *
from menu.page import Page
from utils.components import *
from utils.functions import *
import pandas as pd
from datetime import datetime, timedelta

def buildImplantation(housesImplementationStabilization, churnCompanies, newCompanies, newImplementation):
    st.markdown('## Implantações')

    row = st.columns(1)

    with row[0]: 
        with st.expander("Visualizar Casas em Implantação e Estabilização"):
            component_plotDataframe(housesImplementationStabilization, 'Tabela de Casas em Implantação e Estabilização')
            function_copy_dataframe_as_tsv(housesImplementationStabilization)

    tab1, tab2 = st.tabs(["Implantações", "Recorrência das Casas"])

    with tab1:

        component_plotDataframe(newImplementation, "Em Implantação")

    with tab2:
            row2 = st.columns(3)
            
            with row2 [1]:
                global day
                day = st.date_input('Escolha uma data', value=datetime.today().date(), format='DD/MM/YYYY') 

            row3 = st.columns(2)
            with row3[0]:

                churn_companies_data = churn_companies(day.strftime('%Y-%m-%d'))
                component_plotDataframe(churn_companies_data, "Sem Recorrência")
            
            with row3[1]:
                new_companies_data = new_companies(day.strftime('%Y-%m-%d'))
                component_plotDataframe(new_companies_data, "Buscar Recorrência")
    

class Implantation ():
    def render(self):
        self.data = {}
        self.data['housesImplementationStabilization'] = houses_implementation_stabilization()
        day = datetime.today().date().strftime('%Y-%m-%d')
        self.data['churnCompanies'] = churn_companies(day)
        self.data['newCompanies'] = new_companies(day)
        self.data['newImplementation'] = new_implementation()

        buildImplantation(self.data['housesImplementationStabilization'],
                            self.data['churnCompanies'], 
                            self.data['newCompanies'],
                            self.data['newImplementation'])