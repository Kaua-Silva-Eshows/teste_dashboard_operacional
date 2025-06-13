import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from data.querys_blueme import *
from menu.page import Page
from utils import *
from utils.components import *
from utils.functions import *


def BuildSupplies(companies_, inputsExpenses, purchasesWithoutOrders, bluemeWithOrder, assocExpenseItems, supplierExpenseN5, averageInputN5Price, itemSold):

    tabs = st.tabs(["Análises", "Processos", "Ficha Tecnica"])

    with tabs[0]:

        row = st.columns(6)
        global day_analysis, day_analysis2
        #Filtro de data
        with row[2]:
            day_analysis = st.date_input('Data Inicio:', value=datetime.today().replace(day=1).date(), format='DD/MM/YYYY', key='day_analysis') 
        with row[3]:
            day_analysis2 = st.date_input('Data Final:', value=datetime.today().date(), format='DD/MM/YYYY', key='day_analysis2')
        #Precalção de erro
        if day_analysis > day_analysis2:
            st.warning('📅 Data Inicio deve ser menor que Data Final')
        
        else:
            inputsExpenses = inputs_expenses(day_analysis, day_analysis2)
            #Filtro de Casas
            row_companies = st.columns([1,1,1])
            with row_companies[1]:
                companies_filtered = st.multiselect('Selecione a(s) Casa(s):',options=sorted(inputsExpenses['Casa'].dropna().unique()), placeholder='Casas')
            #Caso nenhum esteja selecionado mostra todos
            if not companies_filtered:
                companies_filtered = inputsExpenses['Casa'].dropna().unique()

            inputsExpenses_filtered = inputsExpenses[inputsExpenses['Casa'].isin(companies_filtered)]
            #Agrupa por Casa e Categoria
            inputsExpenses_n2 = (inputsExpenses_filtered.groupby(['Casa', 'Nivel 2'])[['Valor Insumo']].sum().reset_index().sort_values(by=['Casa', 'Valor Insumo'], ascending=[True, False]))
            inputsExpenses_n2 = function_format_number_columns(inputsExpenses_n2, columns_money=['Valor Insumo'])
            #Agrupa por Categoria
            categoryN2_grafic = (inputsExpenses_filtered.groupby('Nivel 2')[['Valor Insumo']].sum().reset_index().sort_values(by='Valor Insumo', ascending=False))
            categoryN2_grafic['Percentual'] = (categoryN2_grafic['Valor Insumo'] / categoryN2_grafic['Valor Insumo'].sum() * 100).round(1)
            categoryN2_grafic['Label'] = categoryN2_grafic.apply(lambda x: f"{x['Nivel 2']} ({x['Percentual']}%)", axis=1)

            col1, col2 = st.columns([1, 0.8])

            with col1:

                component_plotDataframe_aggrid(inputsExpenses_n2, 'Insumos por Casa e Categoria')
                function_copy_dataframe_as_tsv(inputsExpenses_n2)
            
            with col2:
                component_plotPizzaChart(categoryN2_grafic['Label'], categoryN2_grafic['Valor Insumo'], 'Gastos por Categoria', 19)

            st.markdown('---')

            row_categoryN2 = st.columns([1,1,1])
            with row_categoryN2[1]:
                categoryN2_selected = st.multiselect('Selecione a(s) Categoria(s) (Nivel 2):',options=sorted(inputsExpenses['Nivel 2'].dropna().unique()), placeholder='Categorias')

            if not categoryN2_selected:
                categoryN2_selected = inputsExpenses['Nivel 2'].dropna().unique()

            categoryN2 = inputsExpenses[inputsExpenses['Nivel 2'].isin(categoryN2_selected)]

            with st.expander('Gastos por Fornecedor insumo N5', expanded=False):
                supplierExpenseN5 = supplier_expense_n5(day_analysis, day_analysis2)
                supplierExpenseN5 = supplierExpenseN5[supplierExpenseN5['Casa'].isin(companies_filtered)]

                row_expenses = st.columns([1,1,1])

                with row_expenses[1]:
                    supplierExpenseN5_selected = st.multiselect('Selecione o(s) Fornecedor(es):',options=sorted(supplierExpenseN5['Fornecedor'].dropna().unique()), placeholder='Fornecedores')
                
                if not supplierExpenseN5_selected:
                    supplierExpenseN5_selected = supplierExpenseN5['Fornecedor'].dropna().unique()

                supplierExpenseN5_filtered = supplierExpenseN5[supplierExpenseN5['Fornecedor'].isin(supplierExpenseN5_selected)]

                supplierExpenseN5_filtered = function_format_number_columns(supplierExpenseN5_filtered, columns_money=['Valor Insumo', 'Valor Med Por Insumo'])
                component_plotDataframe_aggrid(supplierExpenseN5_filtered, 'Despesas por Fornecedor')
                function_copy_dataframe_as_tsv(supplierExpenseN5_filtered)

            col3, col4 = st.columns([1, 1])

            with col3:
                categoryN2_supplier_companies = (categoryN2.groupby(['Casa', 'Fornecedor'])[['Valor Insumo']].sum().reset_index().sort_values(by=['Casa', 'Valor Insumo'], ascending=[True, False]))
                
                categoryN2_supplier_companies = function_format_number_columns(categoryN2_supplier_companies, columns_money=['Valor Insumo'])
                
                component_plotDataframe(categoryN2_supplier_companies, 'Insumos por Casa e Fornecedor')
                function_copy_dataframe_as_tsv(categoryN2_supplier_companies)

            with col4:
                categoryN2_supplier = (categoryN2.groupby('Fornecedor')[['Valor Insumo']].sum().reset_index().sort_values(by='Valor Insumo', ascending=False))
                categoryN2_supplier['Percentual'] = (categoryN2_supplier['Valor Insumo'] / categoryN2_supplier['Valor Insumo'].sum() * 100).round(1)
                categoryN2_supplier = function_format_number_columns(categoryN2_supplier, columns_money=['Valor Insumo'])
                categoryN2_supplier['Valor Gasto (R$)'] = categoryN2_supplier['Valor Insumo']
                component_plotDataframe(categoryN2_supplier[['Fornecedor', 'Valor Gasto (R$)', 'Percentual']], 'Distribuição por Fornecedor', column_config= {"Percentual": st.column_config.ProgressColumn("Percentual",format="%.1f%%", min_value=0, max_value=100)})


            st.markdown('---')

            categoryN2_inputs = (categoryN2.groupby('Insumo')[['Valor Insumo', 'Quantidade Insumo']].sum().reset_index())
            categoryN2_inputs['Preco Medio'] = categoryN2_inputs['Valor Insumo'] / categoryN2_inputs['Quantidade Insumo']
            categoryN2_inputs['Percentual Repres'] = (categoryN2_inputs['Valor Insumo'] / categoryN2_inputs['Valor Insumo'].sum() * 100).round(1)
            categoryN2_inputs = categoryN2_inputs.sort_values(by='Valor Insumo', ascending=False)

            #Pegando primeiro e ultimo dia do mês passado para calcular preço médio anterior
            last_day_last_month = datetime.today().replace(day=1) - pd.Timedelta(days=1)
            first_day_last_month = (datetime.today().replace(day=1) - pd.Timedelta(days=1)).replace(day=1)
            
            categoryN2_inputs_last_month = inputs_expenses(first_day_last_month.strftime('%Y-%m-%d'), last_day_last_month.strftime('%Y-%m-%d'))
            categoryN2_inputs_last_month = (categoryN2_inputs_last_month.groupby('Insumo')[['Valor Insumo', 'Quantidade Insumo']].sum().reset_index())
            categoryN2_inputs_last_month['Preco Medio Anterior'] = categoryN2_inputs_last_month['Valor Insumo'] / categoryN2_inputs_last_month['Quantidade Insumo']
            categoryN2_inputs_last_month = categoryN2_inputs_last_month[['Insumo', 'Preco Medio Anterior']]
            
            #Faz o merge e calcula a variação percentual
            categoryN2_inputs_merged = categoryN2_inputs.merge(categoryN2_inputs_last_month, on='Insumo', how='left')
            categoryN2_inputs_merged['Variação Percentual'] = ((categoryN2_inputs_merged['Preco Medio'] - categoryN2_inputs_merged['Preco Medio Anterior']) / categoryN2_inputs_merged['Preco Medio Anterior'] * 100)

            #Formatação das colunas
            categoryN2_inputs_merged = function_format_number_columns(categoryN2_inputs_merged, columns_money=['Valor Insumo', 'Preco Medio', 'Preco Medio Anterior'], columns_number=['Quantidade Insumo'])
            categoryN2_inputs_merged['Percentual Repres'] = categoryN2_inputs_merged['Percentual Repres'].map(lambda x: f"{x:.1f}%")
            categoryN2_inputs_merged['Variação Percentual'] = categoryN2_inputs_merged['Variação Percentual'].map(lambda x: f"{x:+.1f}%" if pd.notnull(x) else '-')
            categoryN2_inputs_merged_style = categoryN2_inputs_merged.style.map(function_highlight_percentage, subset=['Variação Percentual'], invert_color=True)
            
            component_plotDataframe(categoryN2_inputs_merged_style, 'Detalhamento por Insumo')
            function_copy_dataframe_as_tsv(categoryN2_inputs_merged)

    with tabs[1]:

        row2 = st.columns(6)
        global day_process, day_process2
        #Filtro de data
        with row2[2]:
            day_process = st.date_input('Data Inicio:', value=datetime.today().replace(day=1).date(), format='DD/MM/YYYY', key='day_process') 
        with row2[3]:
            day_process2 = st.date_input('Data Final:', value=datetime.today().date(), format='DD/MM/YYYY', key='day_process2')
        #Precalção de erro
        if day_process > day_process2:
            st.warning('📅 Data Inicio deve ser menor que Data Final')
        
        else:
            #Puxando a base de empresas
            companies_ = companies(day_process, day_process2)
            #Filtro de Casas
            row_companies2 = st.columns([1,1,1])
            with row_companies2[1]:
                companies_selected = st.multiselect('Selecione a(s) Casa(s):',options=sorted(companies_['Casa'].dropna().unique()), placeholder='Casas')
            #Caso nenhum esteja selecionado mostra todos
            if not companies_selected:
                companies_selected = companies_['Casa'].dropna().unique()

            with st.expander('Compras Sem Pedido', expanded=True):
                st.warning('Não devem ocorrer')
                st.markdown('---')

                #Puxando a base de Compras Sem Pedido
                purchasesWithoutOrders = purchases_without_orders(day_process, day_process2)
                purchasesWithoutOrders = purchasesWithoutOrders[purchasesWithoutOrders['Casa'].isin(companies_selected)]

                #Agrupar e somar (antes de formatar!)
                purchasesWithoutOrders_grouped = (purchasesWithoutOrders.groupby('Casa').agg(Valor_Original=('Valor Original', 'sum'), Valor_Liquido=('Valor Liquido', 'sum'), Quantidade_Despesas=('Valor Original', 'count')).reset_index())
                purchasesWithoutOrders_grouped.rename(columns={'Valor_Original': 'Valor Original', 'Valor_Liquido': 'Valor Liquido', 'Quantidade_Despesas': 'Quantidade Despesas'}, inplace=True)
                # Criar coluna de Percentual
                purchasesWithoutOrders_grouped['Percentual'] = (purchasesWithoutOrders_grouped['Valor Original'] / purchasesWithoutOrders_grouped['Valor Original'].sum() * 100).round(1)

                purchasesWithoutOrders_grouped = function_format_number_columns(purchasesWithoutOrders_grouped, columns_money=['Valor Original', 'Valor Liquido'])
                # Exibir com as colunas configuradas
                component_plotDataframe(purchasesWithoutOrders_grouped[['Casa', 'Quantidade Despesas', 'Valor Original', 'Valor Liquido', 'Percentual']], 'Compras Sem Pedido', column_config={
                    "Quantidade Despesas": st.column_config.TextColumn(
                        "Qtd. Despesas"
                    ),
                    "Valor Original": st.column_config.TextColumn(
                        "Valor Original (R$)"
                    ),
                    "Valor Liquido": st.column_config.TextColumn(
                        "Valor Líquido (R$)"
                    ),
                    "Percentual": st.column_config.ProgressColumn(
                        "Percentual do Total",
                        format="%.1f%%",
                        min_value=0,
                        max_value=100,
                    )
                })

                purchasesWithoutOrders = purchasesWithoutOrders.sort_values(by=['Casa', 'Valor Original'], ascending=[True, False])
                purchasesWithoutOrders = function_format_number_columns(purchasesWithoutOrders, columns_money=['Valor Original', 'Valor Liquido'])
                component_plotDataframe_aggrid(purchasesWithoutOrders, 'Base Sem Pedido Completa')
                function_copy_dataframe_as_tsv(purchasesWithoutOrders)

            st.markdown('---')

            with st.expander('Distorções (Valor da Despesa - Valor dos Insumos)', expanded=True):

                st.markdown('---')
                
                # Puxando a base de insumos nas despesas
                bluemeWithOrder = blueme_with_order(day_process, day_process2)

                bluemeWithOrder = bluemeWithOrder[bluemeWithOrder['Casa'].isin(companies_selected)]

                # Calcular divergência
                bluemeWithOrder['Divergencia'] = bluemeWithOrder['Valor Original'] - bluemeWithOrder['Valor Cotação']
                bluemeWithOrder = bluemeWithOrder[bluemeWithOrder['Divergencia'] != 0]
                
                #Ordenar por Casa (ascendente) e Divergência (decrescente)
                bluemeWithOrder = bluemeWithOrder.sort_values(by=['Casa', 'Divergencia'], ascending=[True, False])                   

                # Ajustando formato BR
                #bluemeWithOrder = function_format_number_columns(bluemeWithOrder, ['Valor_Original', 'Valor_Liquido', 'Valor_Cotacao'])  

                if bluemeWithOrder.empty:
                    st.warning("Nenhum dado com distorção encontrado.")
                else:
                    col1, col2 = st.columns([3, 1]) 
                    with col1:
                        assocExpenseItems = assoc_expense_items(day_process, day_process2)
                        bluemeWithOrder['Data Competencia'] = bluemeWithOrder['Data Competencia'].astype(str)
                        bluemeWithOrder['Data Vencimento'] = bluemeWithOrder['Data Vencimento'].astype(str)
                        bluemeWithOrder_copy = bluemeWithOrder.copy()
                        assocExpenseItems['Data Competencia'] = assocExpenseItems['Data Competencia'].astype(str)
                        bluemeWithOrder = function_format_number_columns(bluemeWithOrder, columns_money=['Divergencia', 'Valor Original', 'Valor Liquido', 'Valor Cotação'])
                        assocExpenseItems = function_format_number_columns(assocExpenseItems, columns_money=['Valor Unitario', 'Valor Total'], columns_number=['Quantidade Insumo'])
                        component_plotDataframe_aggrid(bluemeWithOrder, 'Detalhamento das Distorções', df_details=assocExpenseItems, coluns_merge_details='ID Despesa', coluns_name_details='Casa' ,key="grid_distorcoes")
                    
                    with col2:
                        # Agrupar por casa e calcular quantidade e valor total da divergência
                        bluemeWithOrder_divergence = (bluemeWithOrder_copy.groupby('Casa').agg(Quantidade=('Divergencia', 'count'),Valor_Total_Distorcido=('Divergencia', 'sum')).reset_index().sort_values(by='Valor_Total_Distorcido', ascending=False))
                        bluemeWithOrder_divergence.rename(columns={'Valor_Total_Distorcido': 'Valor Total Distorcido'}, inplace=True)
                        # Ordenar do maior para o menor valor total distorcido
                        bluemeWithOrder_divergence = bluemeWithOrder_divergence.sort_values(by='Valor Total Distorcido', ascending=False)
                        bluemeWithOrder_divergence = function_format_number_columns(bluemeWithOrder_divergence, columns_money=['Valor Total Distorcido'])

                        bluemeWithOrder_style = bluemeWithOrder_divergence.style.map(function_highlight_value, ['Valor Total Distorcido'])
                        component_plotDataframe(bluemeWithOrder_style, 'Resumo por Casa')
                
                # Puxando a base de insumos nas despesas

                # Ajustando formato BR
                #assocExpenseItems = function_format_number_columns(assocExpenseItems, columns_money=['Quantidade_Insumo', 'Valor_Unitario', 'Valor_Total'])  

                # Exibir os insumos da despesa selecionada
                # if selected_rows is not None and len(selected_rows) > 0:
                #     input_id = selected_rows.iloc[0]['ID_Despesa']
                #     assocExpenseItems_filtered = assocExpenseItems[assocExpenseItems['ID_Despesa'] == input_id]

                #     component_plotDataframe(assocExpenseItems_filtered, f'Despesa ID:{input_id}')
                #     function_copy_dataframe_as_tsv(assocExpenseItems_filtered)
                # else:
                #     st.info("Selecione uma despesa com distorção para visualizar os itens.")

    with tabs[2]:

        row3 = st.columns(6)
        global day_technical_sheet, day_technical_sheet2
        #Filtro de data
        with row3[2]:
            day_technical_sheet = st.date_input('Data Inicio:', value=(datetime.today().replace(day=1) - timedelta(days=1)).replace(day=1).date(), format='DD/MM/YYYY', key='day_technical_sheet') 
        with row3[3]:
            day_technical_sheet2 = st.date_input('Data Final:', value=datetime.today().replace(day=1) - timedelta(days=1), format='DD/MM/YYYY', key='day_technical_sheet2')
        #Precalção de erro
        if day_technical_sheet > day_technical_sheet2:
            st.warning('📅 Data Inicio deve ser menor que Data Final')

        else:
            averageInputN5Price = average_inputN5_price(day_technical_sheet, day_technical_sheet2)
            averageInputN5Price_itemsold = averageInputN5Price[['EMPRESA', 'Insumo de Estoque', 'Média Preço (Insumo de Compra)', 'Média Preço (Insumo Estoque)']]

            row_averageInputN5Price_filters = st.columns([1,1,1,1])
            with row_averageInputN5Price_filters[1]:
                enterprise_selected = st.multiselect('Selecione a(s) Casa(s):',options=sorted(averageInputN5Price['EMPRESA'].dropna().unique()), placeholder='Casas')
            
            if enterprise_selected:
                available_inputs = averageInputN5Price[averageInputN5Price['EMPRESA'].isin(enterprise_selected)]['INSUMO N5'].dropna().unique()
            else:
                available_inputs = averageInputN5Price['INSUMO N5'].dropna().unique()

            with row_averageInputN5Price_filters[2]:
                input_selected = st.multiselect('Selecione o(s) Insumo(s):',options=sorted(available_inputs), placeholder='Insumos')
            
            if enterprise_selected:
                averageInputN5Price = averageInputN5Price[averageInputN5Price['EMPRESA'].isin(enterprise_selected)]

            if input_selected:
                averageInputN5Price = averageInputN5Price[averageInputN5Price['INSUMO N5'].isin(input_selected)]

            if  (enterprise_selected or input_selected):
                function_format_number_columns(averageInputN5Price, columns_money=['MÉDIA PREÇO MÊS'])
                component_plotDataframe_aggrid(averageInputN5Price, 'Preço Médio de Insumo N5')

            st.write('---')

            itemSold = item_sold()
            merged = itemSold.merge(averageInputN5Price_itemsold, how='left', on=['Insumo de Estoque', 'EMPRESA'])
            merged['Valor na Ficha'] = merged.apply(lambda row: (row['Média Preço (Insumo Estoque)'] / 1000) * row['Quantidade na Ficha'] 
            if row['Unidade Medida'] in ['KG', 'LT'] 
            else row['Média Preço (Insumo Estoque)'], axis=1)
            item_valuer = merged.copy()
            item_valuer['Valor Vendido'] = item_valuer['VALOR DO ITEM']
            item_valuer = item_valuer.groupby(['EMPRESA', 'Item Vendido', 'Valor Vendido']).agg({'Valor na Ficha': 'sum'}).reset_index()
            item_valuer['Custo do Item'] = item_valuer['Valor na Ficha']
            item_valuer = item_valuer[['EMPRESA', 'Item Vendido', 'Custo do Item', 'Valor Vendido']]
            item_valuer['CMV'] = (item_valuer['Custo do Item'].astype(float) / item_valuer['Valor Vendido'].astype(float)) * 100
            item_valuer['Lucro do Item'] = item_valuer['Valor Vendido'].astype(float) - item_valuer['Custo do Item'].astype(float)
            function_format_number_columns(item_valuer, columns_money=['Custo do Item', 'Valor Vendido', 'Lucro do Item'], columns_percent=['CMV'])
            component_plotDataframe_aggrid(item_valuer, 'Valor dos Itens Vendidos')
            row_itemValuer_selected = st.columns(3)
            with row_itemValuer_selected[1]:
                itemValuer_selected = st.multiselect('Selecione o(s) Item(s) Vendido(s):',options=sorted(merged['Item Vendido'].dropna().unique()), placeholder='Itens Vendidos')
            
            if itemValuer_selected:
                merged = merged[merged['Item Vendido'].isin(itemValuer_selected)]
                merged['Unidade de Medida na Ficha'] = merged.apply(function_format_quantidade, axis=1)
                merged = merged.drop(columns=['VALOR DO ITEM', 'Média Preço (Insumo de Compra)'])
                merged = merged[['EMPRESA','Item Vendido', 'Insumo de Estoque', 'Unidade Medida', 'Média Preço (Insumo Estoque)', 'Quantidade na Ficha', 'Unidade de Medida na Ficha' ,'Valor na Ficha' ]]
                function_format_number_columns(merged, columns_money=['MÉDIA PREÇO MÊS', 'Valor na Ficha'])
                component_plotDataframe_aggrid(merged, 'Itens Vendidos Detalhado')
            


class Supplies(Page):
    def render(self):
        self.data = {}
        day_analysis = datetime.today().replace(day=1).date()
        day_analysis2 = datetime.today().date()
        self.data['inputsExpenses'] = inputs_expenses(day_analysis, day_analysis2)
        self.data['supplierExpenseN5'] = supplier_expense_n5(day_analysis, day_analysis2)

        day_process = datetime.today().replace(day=1).date()
        day_process2 = datetime.today().date()
        self.data['companies_'] = companies(day_process, day_process2)
        self.data['purchasesWithoutOrders'] = purchases_without_orders(day_process, day_process2)
        self.data['bluemeWithOrder'] = blueme_with_order(day_process, day_process2)
        self.data['assocExpenseItems'] = assoc_expense_items(day_process, day_process2)

        day_technical_sheet = (datetime.today().replace(day=1) - timedelta(days=1)).replace(day=1).date()
        day_technical_sheet2 = datetime.today().replace(day=1) - timedelta(days=1)
        self.data['averageInputN5Price'] = average_inputN5_price(day_technical_sheet, day_technical_sheet2)

        self.data['itemSold'] = item_sold()

        BuildSupplies(self.data['companies_'],
                      self.data['inputsExpenses'],
                      self.data['purchasesWithoutOrders'],
                      self.data['bluemeWithOrder'],
                      self.data['assocExpenseItems'],
                      self.data['supplierExpenseN5'],
                      self.data['averageInputN5Price'],
                      self.data['itemSold'])