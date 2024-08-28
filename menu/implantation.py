import streamlit as st
from data.queries import *
from menu.page import Page
from utils.components import *
from utils.functions import *
import pandas as pd
from datetime import datetime, timedelta

def buildImplantation(newImplementation):
    st.markdown('## Implantações')

    component_plotDataframe(newImplementation, "Em Implantação")
    
    temp = newImplementation.groupby('STATUS').size().reset_index(name='QUANTIDADE')

    center = st.columns([1.5,2,1.5])
    with center[1]:
        plotPizzaChart(temp['STATUS'], temp['QUANTIDADE'], None)
    

class Implantation ():
    def render(self):
        self.data = {}
        self.data['newImplementation'] = new_implementation()

        buildImplantation(self.data['newImplementation'])