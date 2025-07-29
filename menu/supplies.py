import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from data.querys_blueme import *
from menu.page import Page
from utils import *
from utils.components import *
from utils.functions import *

def BuildSupplies(companies_, inputsExpenses, purchasesWithoutOrders, bluemeWithOrder, assocExpenseItems, supplierExpenseN5, averageInputN5Price, itemSold, inputProduced):

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
            
            input_total_value = function_format_number_columns(valor = inputsExpenses_n2['Valor Insumo'].sum()) # Salvando o valor total filtrado antes de formatar
            
            inputsExpenses_n2 = function_format_number_columns(inputsExpenses_n2, columns_money=['Valor Insumo'])
            #Agrupa por Categoria
            categoryN2_grafic = (inputsExpenses_filtered.groupby('Nivel 2')[['Valor Insumo']].sum().reset_index().sort_values(by='Valor Insumo', ascending=False))
            categoryN2_grafic['Percentual'] = (categoryN2_grafic['Valor Insumo'] / categoryN2_grafic['Valor Insumo'].sum() * 100).round(1)
            categoryN2_grafic['Label'] = categoryN2_grafic.apply(lambda x: f"{x['Nivel 2']} ({x['Percentual']}%)", axis=1)

            row = st.columns([2,1,2])
            with row[1]:
                if st.session_state.get("base_theme") == "dark":
                    color_back = "#222"
                    color_font = "#ffffff"
                else:
                    color_back = "#ffffff"
                    color_font = "#000000"
                st.write(f"""<div style='background: {color_back};border-radius: 20px;border: 1px solid #8B0000;padding: 15px 0 15px 0;margin: 8px 0;text-align: center;font-family: \"Segoe UI\", \"Arial\", sans-serif;'><div style='font-size: 13px; color: #D14D4D; font-weight: 500;'>💰 Valor Total dos Insumos</div><div style='font-size: 18px; color: {color_font}; font-weight: bold; margin-top: 2px;'>{input_total_value}</div></div>""", unsafe_allow_html=True)

            col1, col2 = st.columns([1, 0.8])
            with col1:
                component_plotDataframe_aggrid(inputsExpenses_n2, 'Insumos por Casa e Categoria')
                #function_copy_dataframe_as_tsv(inputsExpenses_n2)
            
            with col2:
                component_plotPizzaChart(categoryN2_grafic['Label'], categoryN2_grafic['Valor Insumo'], 'Gastos por Categoria', 19)

            st.markdown('---')

            row_categoryN2 = st.columns([1,1,1])
            with row_categoryN2[1]:
                # Filtro de categorias baseado nas casas selecionadas
                categorias_disponiveis = sorted(inputsExpenses_filtered['Nivel 2'].dropna().unique())
                categoryN2_selected = st.multiselect('Selecione a(s) Categoria(s) (Nivel 2):',options=categorias_disponiveis, placeholder='Categorias')
            if not categoryN2_selected:
                categoryN2_selected = categorias_disponiveis
            inputs_expenses_filtered_by_cat = inputsExpenses_filtered[inputsExpenses_filtered['Nivel 2'].isin(categoryN2_selected)]

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
                categoryN2_supplier_companies = (inputs_expenses_filtered_by_cat.groupby(['Casa', 'Fornecedor'])[['Valor Insumo']].sum().reset_index().sort_values(by=['Casa', 'Valor Insumo'], ascending=[True, False]))
                
                categoryN2_supplier_companies = function_format_number_columns(categoryN2_supplier_companies, columns_money=['Valor Insumo'])
                
                component_plotDataframe(categoryN2_supplier_companies, 'Insumos por Casa e Fornecedor')
                function_copy_dataframe_as_tsv(categoryN2_supplier_companies)

            with col4:
                categoryN2_supplier = (inputs_expenses_filtered_by_cat.groupby('Fornecedor')[['Valor Insumo']].sum().reset_index().sort_values(by='Valor Insumo', ascending=False))
                categoryN2_supplier['Percentual'] = (categoryN2_supplier['Valor Insumo'] / categoryN2_supplier['Valor Insumo'].sum() * 100).round(1)
                categoryN2_supplier = function_format_number_columns(categoryN2_supplier, columns_money=['Valor Insumo'])
                categoryN2_supplier['Valor Gasto (R$)'] = categoryN2_supplier['Valor Insumo']
                component_plotDataframe(categoryN2_supplier[['Fornecedor', 'Valor Gasto (R$)', 'Percentual']], 'Distribuição por Fornecedor', column_config= {"Percentual": st.column_config.ProgressColumn("Percentual",format="%.1f%%", min_value=0, max_value=100)})


            st.markdown('---')

            categoryN2_inputs = (inputs_expenses_filtered_by_cat.groupby('Insumo')[['Valor Insumo', 'Quantidade Insumo']].sum().reset_index())
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
            averageInputN5Price = average_inputN5_price(day_technical_sheet.strftime('%Y-%m-%d'), day_technical_sheet2.strftime('%Y-%m-%d'))
            averageInputN5Price_itemsold = averageInputN5Price.copy()
            averageInputN5Price_itemsold['QUANTIDADE DRI'] = averageInputN5Price_itemsold['QUANTIDADE DRI'].replace(['None', None, '', 'nan', 'NaN'], '0').astype(str).str.replace(',', '.', regex=False).astype(float)
            averageInputN5Price_itemsold['PROPORÇÃO ACE'] = averageInputN5Price_itemsold['PROPORÇÃO ACE'].replace(['None', None, '', 'nan', 'NaN'], '0').astype(str).str.replace(',', '.', regex=False).astype(float)
            averageInputN5Price_itemsold['Volume Total'] = averageInputN5Price_itemsold['QUANTIDADE DRI'] * averageInputN5Price_itemsold['PROPORÇÃO ACE']
            averageInputN5Price_itemsold = averageInputN5Price_itemsold.groupby(['EMPRESA', 'Insumo de Estoque']).agg({'Volume Total': 'sum', 'VALOR DRI': 'sum'})
            averageInputN5Price_itemsold['Média Preço (Insumo Estoque)'] = averageInputN5Price_itemsold['VALOR DRI'].astype(str).str.replace(',', '.', regex=False).astype(float) / averageInputN5Price_itemsold['Volume Total'].astype(str).str.replace(',', '.', regex=False).astype(float)
            averageInputN5Price_itemsold = averageInputN5Price_itemsold.reset_index()
            averageInputN5Price_itemsold = averageInputN5Price_itemsold[['EMPRESA', 'Insumo de Estoque', 'Média Preço (Insumo Estoque)']].reindex()

            row_averageInputN5Price_filters = st.columns([1,1,1,1])
            with row_averageInputN5Price_filters[1]:
                enterprise_selected = st.multiselect('Selecione a(s) Casa(s):',options=sorted(averageInputN5Price['EMPRESA'].dropna().unique()), placeholder='Casas', key='enterprise_selected')
            
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

            averageInputN5Price = averageInputN5Price.drop(columns=['VALOR DRI', 'QUANTIDADE DRI', 'PROPORÇÃO ACE'])
            function_format_number_columns(averageInputN5Price, columns_money=['Média Preço (Insumo de Compra)', 'Média Preço (Insumo Estoque)'])
            if  (enterprise_selected or input_selected): 
                component_plotDataframe_aggrid(averageInputN5Price, 'Preço Médio de Insumo N5') 
            else: 
                component_plotDataframe_aggrid(averageInputN5Price, 'Preço Médio de Insumo N5')

            st.write('---')

            itemSold = item_sold()
            #st.write(itemSold)
            #st.write(averageInputN5Price_itemsold)
            itemSold_merged = itemSold.merge(averageInputN5Price_itemsold, how='left', on=['Insumo de Estoque', 'EMPRESA'])
            itemSold_merged['Unidade de Medida na Ficha'] = itemSold_merged.apply(function_format_amount, axis=1)
            # Salvar o VALOR DO ITEM antes de remover
            valor_do_item = itemSold_merged['VALOR DO ITEM'].copy()
            itemSold_merged = itemSold_merged.drop(columns=['VALOR DO ITEM'])
            itemSold_merged = itemSold_merged[['EMPRESA','Item Vendido', 'CATEGORIA', 'Insumo de Estoque', 'Unidade Medida', 'Média Preço (Insumo Estoque)', 'Quantidade na Ficha', 'Unidade de Medida na Ficha']]
            #st.write(itemSold_merged)
            inputProduced = input_produced(day_technical_sheet.strftime('%Y-%m-%d'), day_technical_sheet2.strftime('%Y-%m-%d'))
            #st.dataframe(inputProduced)
            inputProduced_grouped = (inputProduced.groupby(['EMPRESA', 'ITEM PRODUZIDO', 'RENDIMENTO'])[['VALOR PRODUÇÃO']].sum().reset_index())
            inputProduced_grouped['VALOR DO KG'] = (inputProduced_grouped['VALOR PRODUÇÃO'] * 1000) / inputProduced_grouped['RENDIMENTO']

            #st.dataframe(inputProduced_grouped)
            inputProduced_grouped = inputProduced_grouped.rename(columns={'ITEM PRODUZIDO': 'INSUMO_DE_ESTOQUE', 'VALOR DO KG': 'VALOR_DO_KG'})
            
            inputProduced_merged = inputProduced.copy()

            while True:
                merge_temp = inputProduced_merged.merge(
                    inputProduced_grouped[['INSUMO_DE_ESTOQUE', 'VALOR_DO_KG']],
                    left_on='Insumo de Estoque',
                    right_on='INSUMO_DE_ESTOQUE',
                    how='left'
                )
                before_null = merge_temp['MÉDIA PREÇO NO ITEM KG'].isna().sum()
                merge_temp['MÉDIA PREÇO NO ITEM KG'] = merge_temp['MÉDIA PREÇO NO ITEM KG'].fillna(merge_temp['VALOR_DO_KG'])
                merge_temp['VALOR_PRODUÇÃO_ATUAL'] = merge_temp['VALOR PRODUÇÃO']
                mask = merge_temp['VALOR_PRODUÇÃO_ATUAL'].isna() & merge_temp['MÉDIA PREÇO NO ITEM KG'].notna()
                merge_temp.loc[mask, 'VALOR PRODUÇÃO'] = (merge_temp.loc[mask, 'QUANTIDADE INSUMO'] / 1000) * merge_temp.loc[mask, 'MÉDIA PREÇO NO ITEM KG']
                merge_temp = merge_temp.drop(columns=['INSUMO_DE_ESTOQUE', 'VALOR_DO_KG', 'VALOR_PRODUÇÃO_ATUAL'])
                after_null = merge_temp['MÉDIA PREÇO NO ITEM KG'].isna().sum()
                if after_null == before_null:
                    break
                inputProduced_merged = merge_temp
            #st.dataframe(inputProduced_merged)
            inputProduced_items = (inputProduced_merged.groupby(['EMPRESA', 'ITEM PRODUZIDO', 'RENDIMENTO'])[['VALOR PRODUÇÃO']].sum().reset_index())

            if 'VALOR DO KG' not in inputProduced_items.columns:
                inputProduced_items['VALOR DO KG'] = (inputProduced_items['VALOR PRODUÇÃO'] * 1000) / inputProduced_items['RENDIMENTO']

            #st.dataframe(inputProduced_items)

            # Criar a coluna Valor na Ficha inicialmente
            itemSold_merged['Valor na Ficha'] = itemSold_merged.apply(
                lambda row: (row['Média Preço (Insumo Estoque)'] / 1000) * row['Quantidade na Ficha'] 
                if row['Unidade Medida'] in ['KG', 'LT'] 
                else row['Média Preço (Insumo Estoque)'], 
                axis=1
            )

            # Verificar se há itens produzidos que correspondem aos insumos de estoque
            # Criar um dicionário com o valor do kg para cada item produzido
            inputProduced_items_dict = dict(zip(inputProduced_items['ITEM PRODUZIDO'], inputProduced_items['VALOR DO KG']))
            
            # Atualizar Média Preço (Insumo Estoque) com valores dos itens produzidos quando disponível
            itemSold_merged['Média Preço (Insumo Estoque)'] = itemSold_merged.apply(
                lambda row: inputProduced_items_dict.get(row['Insumo de Estoque'], row['Média Preço (Insumo Estoque)']), 
                axis=1
            )
            
            # Recalcular Valor na Ficha para os casos onde houve substituição
            itemSold_merged['Valor na Ficha'] = itemSold_merged.apply(
                lambda row: (row['Quantidade na Ficha'] / 1000) * row['Média Preço (Insumo Estoque)']
                if row['Insumo de Estoque'] in inputProduced_items_dict
                else (row['Média Preço (Insumo Estoque)'] / 1000) * row['Quantidade na Ficha'] if row['Unidade Medida'] in ['KG', 'LT'] else row['Média Preço (Insumo Estoque)'], 
                axis=1
            )
            #st.write(itemSold_merged)

            item_valuer = itemSold_merged.copy()
            item_valuer['Valor Vendido'] = valor_do_item
            item_valuer = item_valuer.groupby(['EMPRESA', 'Item Vendido', 'CATEGORIA', 'Valor Vendido']).agg({'Valor na Ficha': 'sum'}).reset_index()
            item_valuer['Custo do Item'] = item_valuer['Valor na Ficha']
            item_valuer = item_valuer[['EMPRESA', 'Item Vendido', 'CATEGORIA', 'Custo do Item', 'Valor Vendido']]
            item_valuer['CMV'] = (item_valuer['Custo do Item'].astype(float) / item_valuer['Valor Vendido'].astype(float)) * 100
            item_valuer['Lucro do Item'] = item_valuer['Valor Vendido'].astype(float) - item_valuer['Custo do Item'].astype(float)

            if enterprise_selected:
                item_valuer = item_valuer[item_valuer['EMPRESA'].isin(enterprise_selected)]

            function_format_number_columns(item_valuer, columns_money=['Custo do Item', 'Valor Vendido', 'Lucro do Item'], columns_percent=['CMV'])
            if  enterprise_selected:
                component_plotDataframe_aggrid(item_valuer, 'Valor dos Itens Vendidos')
            else:
                component_plotDataframe_aggrid(item_valuer, 'Valor dos Itens Vendidos')
            function_copy_dataframe_as_tsv(item_valuer)

            st.write('---')

            # with row_averageInputN5Price_filters[1]:
            #     enterprise_selected = st.multiselect('Selecione a(s) Casa(s):',options=sorted(averageInputN5Price['EMPRESA'].dropna().unique()), placeholder='Casas', key='enterprise_selected')
            
            # if enterprise_selected:
            #     available_inputs = averageInputN5Price[averageInputN5Price['EMPRESA'].isin(enterprise_selected)]['INSUMO N5'].dropna().unique()
            # else:
            #     available_inputs = averageInputN5Price['INSUMO N5'].dropna().unique()

            # with row_averageInputN5Price_filters[2]:
            #     input_selected = st.multiselect('Selecione o(s) Insumo(s):',options=sorted(available_inputs), placeholder='Insumos')

            if enterprise_selected:
                itemValuer_enterprise = itemSold_merged[itemSold_merged['EMPRESA'].isin(enterprise_selected)]['Item Vendido'].dropna().unique()
                itemSold_merged = itemSold_merged[itemSold_merged['EMPRESA'].isin(enterprise_selected)]
            else:
                itemValuer_enterprise = itemSold_merged['Item Vendido'].dropna().unique()

            row_itemValuer_selected = st.columns(3)
            with row_itemValuer_selected[1]:
                itemValuer_selected = st.multiselect('Selecione o(s) Item(s) Vendido(s):',options=sorted(itemValuer_enterprise),placeholder='Itens Vendidos')                

            if itemValuer_selected:
                itemSold_merged = itemSold_merged[itemSold_merged['Item Vendido'].isin(itemValuer_selected)]
                inputProduced_merged['Insumos para Produção'] = inputProduced_merged['Insumo de Estoque']
                inputProduced_merged['Insumo de Estoque'] = inputProduced_merged['ITEM PRODUZIDO']
                inputProduced_merged = inputProduced_merged[['Insumo de Estoque', 'RENDIMENTO', 'Insumos para Produção', 'QUANTIDADE INSUMO', 'MÉDIA PREÇO NO ITEM KG', 'VALOR PRODUÇÃO']]
                #st.dataframe(inputProduced_merged)
                function_format_number_columns(itemSold_merged, columns_money=['Média Preço (Insumo Estoque)', 'Valor na Ficha'], columns_number=['RENDIMENTO', 'QUANTIDADE INSUMO'])
                function_format_number_columns(inputProduced_merged, columns_money=['MÉDIA PREÇO NO ITEM KG', 'VALOR PRODUÇÃO'])
                component_plotDataframe_aggrid(itemSold_merged, 'Itens Vendidos Detalhado', df_details=inputProduced_merged, coluns_merge_details='Insumo de Estoque', coluns_name_details='EMPRESA')

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
        self.data['averageInputN5Price'] = average_inputN5_price(day_technical_sheet.strftime('%Y-%m-%d'), day_technical_sheet2.strftime('%Y-%m-%d'))
        self.data['inputProduced'] = input_produced(day_technical_sheet.strftime('%Y-%m-%d'), day_technical_sheet2.strftime('%Y-%m-%d'))

        self.data['itemSold'] = item_sold()


        BuildSupplies(self.data['companies_'],
                      self.data['inputsExpenses'],
                      self.data['purchasesWithoutOrders'],
                      self.data['bluemeWithOrder'],
                      self.data['assocExpenseItems'],
                      self.data['supplierExpenseN5'],
                      self.data['averageInputN5Price'],
                      self.data['itemSold'],
                      self.data['inputProduced'])