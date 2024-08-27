import streamlit as st
from data.queries import *
from menu.page import Page
from utils.components import *
from utils.functions import *
import pandas as pd
from datetime import datetime, timedelta

def buildImplantation(housesImplementationStabilization, churnCompanies, newCompanies, newImplementation):
    st.markdown('## Implantações')

    component_plotDataframe(newImplementation, "Em Implantação")
    
    temp = newImplementation.groupby('STATUS').size().reset_index(name='QUANTIDADE')

    center = st.columns([1.5,2,1.5])
    with center[1]:
        plotPizzaChart(temp['STATUS'], temp['QUANTIDADE'], None)
    

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