import streamlit as st
from data.queries import *
from menu.page import Page
from utils.components import *
from utils.functions import *
import pandas as pd
from datetime import datetime, timedelta

def buildImplantation(newImplementation, implementationFirstProposal):
    st.markdown('## Implantações')

    tab1, tab2 = st.tabs(["Em implantação e Estabilização", "Primeira Proposta"])
    
    with tab1:    
        component_plotDataframe(newImplementation, "Em Implantação")
    
        temp = newImplementation.groupby('STATUS').size().reset_index(name='QUANTIDADE')

        center = st.columns([1.5,2,1.5])
        with center[1]:
            plotPizzaChart(temp['STATUS'], temp['QUANTIDADE'], None)

    with tab2:
        component_plotDataframe(implementationFirstProposal, "Primeira Proposta Da Casa")
    

class Implantation ():
    def render(self):
        self.data = {}
        self.data['newImplementation'] = new_implementation()
        self.data['implementationFirstProposal'] = implementation_first_proposal()

        buildImplantation(self.data['newImplementation'], self.data['implementationFirstProposal'])