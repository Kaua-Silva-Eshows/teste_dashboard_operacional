import streamlit as st
from data.querys_eshows import *
from menu.page import Page
from utils.components import *
from utils.functions import *
from datetime import date, datetime

def BuildManegementBilling(generalRevenue, groupsCompanies, generalRevenueProposal):

    row1 = st.columns(6)
    global day_ManegementBilling1, day_ManegementBilling2
    
    with row1[2]:
        day_ManegementBilling1 = st.date_input('Data Inicio:', value=datetime(2025, 1, 1).date(), format='DD/MM/YYYY', key='day_ManegementBilling1') 
    with row1[3]:
        day_ManegementBilling2 = st.date_input('Data Final:', value=datetime.today().date(), format='DD/MM/YYYY', key='day_ManegementBilling2')

    row2 = st.columns(1)
    with row2[0]:
        generalRevenue = general_revenue(day_ManegementBilling1, day_ManegementBilling2)    
        generalRevenue = function_format_numeric_columns(generalRevenue, columns_num=['Valor Total', 'Comissão B2B', 'Comissão B2C', 'SAAS Mensalidade', 'SAAS Percentual', 'Curadoria', 'Taxa Adiantamento', 'Taxa Emissão NF', 'Faturamento Total'], columns_percent=['Take Rate','Percentual Faturamento'])
        filtered_copy, count = component_plotDataframe(generalRevenue, "Faturamento Eshows Gerencial")
        function_copy_dataframe_as_tsv(filtered_copy)

    tabs = st.tabs(["Filtro por Grupo", "Filtro por KeyAccount"])
    with tabs[0]:
        
        cols = st.columns([2,1,1])
        with cols[0]:
            groupsCompanies = groups_companies(day_ManegementBilling1, day_ManegementBilling2)

            selected_groups = st.multiselect("Selecione um grupo:", ['Outros'] + sorted(filter(None, groupsCompanies['NOME'].unique())), default=[], placeholder='Grupos')
        if selected_groups:
            selected_groups.append(None)
            groupsCompanies_filtered = groupsCompanies[groupsCompanies['NOME'].isin(selected_groups)]

            selected_groups_str = ", ".join(f"'{group}'" for group in selected_groups)
            if "Outros" in selected_groups:
                filters = f"AND (GC.NOME IN ({selected_groups_str}) OR (GC.NOME IS NULL))"
            else:
                filters = f"AND GC.NOME IN ({selected_groups_str})"

            with cols[1]:
                groupsCompanies = groups_companies(day_ManegementBilling1, day_ManegementBilling2, filters)

                select_keyaccount = st.multiselect("Selecione o KY", options=groupsCompanies['KY'].dropna().unique(), default=None,placeholder='KY')            
                select_keyaccount_str = ", ".join(f"'{ky}'" for ky in select_keyaccount)
                if select_keyaccount:
                    filters += f" AND KE.NOME IN ({select_keyaccount_str})"

            with cols[2]:
                groupsCompanies_filtered = groups_companies(day_ManegementBilling1, day_ManegementBilling2, filters)

                if "Outros" not in selected_groups:
                    groupsCompanies_filtered = groupsCompanies_filtered.dropna(subset=['NOME'])
                select_companies = st.multiselect("Selecione as casas:", groupsCompanies_filtered['NAME'].unique(), placeholder='Casas')
            
            if select_companies:
                groupsCompanies_filtered = groupsCompanies_filtered[groupsCompanies_filtered['NAME'].isin(select_companies)]

            if select_companies:
                select_companies_str = ", ".join(f"'{company}'" for company in select_companies)
                if "Outros" in selected_groups:
                    filters += f" AND (C.NAME IN ({select_companies_str}) OR GC.NOME IS NULL)"
                else:
                    filters += f" AND C.NAME IN ({select_companies_str})"

            generalRevenue = general_revenue(day_ManegementBilling1, day_ManegementBilling2, filters)
            generalRevenue = function_format_numeric_columns(generalRevenue, columns_num=['Valor Total', 'Comissão B2B', 'Comissão B2C', 'SAAS Mensalidade', 'SAAS Percentual', 'Curadoria', 'Taxa Adiantamento', 'Taxa Emissão NF', 'Faturamento Total'], columns_percent=['Take Rate','Percentual Faturamento'])
            
            filtered_copy, count = component_plotDataframe(generalRevenue, "Faturamento Detalhado")
            function_copy_dataframe_as_tsv(filtered_copy)

            with st.expander("📊 Abertura por Proposta", expanded=False):
                generalRevenueProposal = general_revenue_proposal(day_ManegementBilling1, day_ManegementBilling2, filters)
                generalRevenueProposal = function_format_numeric_columns(generalRevenueProposal, columns_num=['VALOR BRUTO','VALOR LIQUIDO','VALOR TOTAL','COMISSÃO B2B','COMISSÃO B2C','ADIANTAMENTO','SAAS PERCENTUAL','SAAS MENSALIDADE','TAXA EMISSÃO NF'], columns_percent=['% LIQUIDO'])
                
                filtered_copy, count = component_plotDataframe(generalRevenueProposal, "Abertura por Proposta")
                function_copy_dataframe_as_tsv(filtered_copy)
                function_box_lenDf(len_df=count, df=filtered_copy, y='-100', x='500', box_id='box1', item='Propostas')
        
        with tabs[1]:
            cols = st.columns([2,1,1])
            with cols[0]:
                groupsCompanies = groups_companies(day_ManegementBilling1, day_ManegementBilling2)

                select_keyaccount = st.multiselect("Selecione o KY", options=groupsCompanies['KY'].dropna().unique(), default=None, placeholder='KY')
            if select_keyaccount:
                select_keyaccount_str = ", ".join(f"'{ky}'" for ky in select_keyaccount)
                filters = ""
                filters += f" AND KE.NOME IN ({select_keyaccount_str})"

                groupsCompanies = groups_companies(day_ManegementBilling1, day_ManegementBilling2, filters)

                with cols[1]:
                    selected_groups = st.multiselect("Selecione um grupo:", ['Outros'] + sorted(filter(None, groupsCompanies['NOME'].unique())), default=[], placeholder='Grupos', key='tab2_groups')

                    if selected_groups:
                        selected_groups.append(None)
                        selected_groups_str = ", ".join(f"'{group}'" for group in selected_groups)
                        if "Outros" in selected_groups:
                            filters += f" AND (GC.NOME IN ({selected_groups_str}) OR GC.NOME IS NULL)"
                        else:
                            filters += f" AND GC.NOME IN ({selected_groups_str})"

                        groupsCompanies = groups_companies(day_ManegementBilling1, day_ManegementBilling2, filters)

                with cols[2]:
                    if "Outros" not in selected_groups:
                        groupsCompanies = groupsCompanies.dropna(subset=['NOME'])

                    select_companies = st.multiselect("Selecione as casas:", groupsCompanies['NAME'].unique(), placeholder='Casas')

                    if select_companies:
                        groupsCompanies = groupsCompanies[groupsCompanies['NAME'].isin(select_companies)]
                        select_companies_str = ", ".join(f"'{company}'" for company in select_companies)
                        if "Outros" in selected_groups:
                            filters += f" AND (C.NAME IN ({select_companies_str}) OR GC.NOME IS NULL)"
                        else:
                            filters += f" AND C.NAME IN ({select_companies_str})"

                generalRevenue = general_revenue(day_ManegementBilling1, day_ManegementBilling2, filters)
                generalRevenue = function_format_numeric_columns(generalRevenue, columns_num=['Valor Total', 'Comissão B2B', 'Comissão B2C', 'SAAS Mensalidade', 'SAAS Percentual', 'Curadoria', 'Taxa Adiantamento', 'Taxa Emissão NF', 'Faturamento Total'], columns_percent=['Take Rate','Percentual Faturamento'])
                
                filtered_copy, count = component_plotDataframe(generalRevenue, "Faturamento Detalhado", key='tab2')
                function_copy_dataframe_as_tsv(filtered_copy)

                with st.expander("📊 Abertura por Proposta", expanded=False):
                    generalRevenueProposal = general_revenue_proposal(day_ManegementBilling1, day_ManegementBilling2, filters)
                    generalRevenueProposal = function_format_numeric_columns(generalRevenueProposal, columns_num=['VALOR BRUTO','VALOR LIQUIDO','VALOR TOTAL','COMISSÃO B2B','COMISSÃO B2C','ADIANTAMENTO','SAAS PERCENTUAL','SAAS MENSALIDADE','TAXA EMISSÃO NF'], columns_percent=['% LIQUIDO'])
                    
                    filtered_copy, count = component_plotDataframe(generalRevenueProposal, "Abertura por Proposta", key='tab2')
                    function_copy_dataframe_as_tsv(filtered_copy)
                    function_box_lenDf(len_df=count, df=filtered_copy, y='-100', x='500', box_id='box1', item='Propostas')

class ManegementBilling():
    def render(self):
        self.data = {}
        day_ManegementBilling1 = datetime.today().date()
        day_ManegementBilling2 = datetime.today().date()
        self.data['generalRevenue'] = general_revenue(day_ManegementBilling1, day_ManegementBilling2, filters='')
        self.data['groupsCompanies'] = groups_companies(day_ManegementBilling1, day_ManegementBilling2)
        self.data['generalRevenueProposal'] = general_revenue_proposal(day_ManegementBilling1, day_ManegementBilling2, filters='')

        BuildManegementBilling(self.data['generalRevenue'],
                               self.data['groupsCompanies'],
                               self.data['generalRevenueProposal'])