import pandas as pd
import streamlit as st
from st_aggrid import GridUpdateMode, JsCode, StAggridTheme
from st_aggrid import AgGrid, GridOptionsBuilder
from streamlit_echarts import st_echarts

from utils.functions import function_box_lenDf

def component_hide_sidebar():
    st.markdown(""" 
    <style>
        section[data-testid="stSidebar"][aria-expanded="true"]{
                display: none;
                }
    </style>
    """, unsafe_allow_html=True)

def component_fix_tab_echarts():
    streamlit_style = """
    <style>
    iframe[title="streamlit_echarts.st_echarts"]{ height: 450px; width: 750px;} 
   </style>
    """

    return st.markdown(streamlit_style, unsafe_allow_html=True)

def component_effect_underline():
    if st.session_state.get("base_theme") == "dark":
        color = "#ffffff"
    else:
        color = "#000000" 
    st.markdown(
    f"""<style>.full-width-line-white {{width: 100%;border-bottom: 1px solid {color};margin-bottom: 0.5em;}}</style>""",unsafe_allow_html=True)

def component_plotDataframe(df, name, num_columns=[], percent_columns=[], df_details=None, coluns_merge_details=None, coluns_name_details=None, key="default"):
    st.markdown(f"<h5 style='text-align: center; background-color: #ffb131; padding: 0.1em;'>{name}</h5>",unsafe_allow_html=True)
    # Converter colunas selecionadas para float com limpeza de texto
    for col in num_columns:
        if col in df.columns:
            df[f"{col}_NUM"] = (
                df[col]
                .astype(str)
                .str.upper()
                .str.replace(r'[A-Z$R\s]', '', regex=True)
                .str.replace('.', '', regex=False)
                .str.replace(',', '.', regex=False)
            )
            df[f"{col}_NUM"] = pd.to_numeric(df[f"{col}_NUM"], errors='coerce')

            # Formatar a coluna original como string BR
            df[col] = df[f"{col}_NUM"].apply(
                lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if pd.notnull(x) else ""
            )

    for col in percent_columns:
        if col in df.columns:
            df[f"{col}_NUM"] = (
                df[col]
                .astype(str)
                .str.replace('%', '', regex=False)
                .str.replace(',', '.', regex=False)
                .str.replace('−', '-', regex=False)
                .str.replace('–', '-', regex=False)
                .str.replace(r'[^\d\.\-]', '', regex=True)
            )
            df[f"{col}_NUM"] = pd.to_numeric(df[f"{col}_NUM"], errors='coerce')

            # Formatar a coluna original como string percentual
            df[col] = df[f"{col}_NUM"].apply(
                lambda x: f"{x:.2f}%".replace('.', ',') if pd.notnull(x) else ""
            )

    # Definir cellStyle para pintar valores negativos/positivos
    cellstyle_code = JsCode("""
    function(params) {
        const value = params.data[params.colDef.field + '_NUM'];
        if (value === null || value === undefined || isNaN(value)) {
            return {};
        }
        if (value <= 5) {
            return {
                color: '#90ee90',
                fontWeight: 'bold'
            };
        }
        if (value > 5 && value <= 10) {
            return {
                color: '#1e90ff',
                fontWeight: 'bold'
            };
        }
        if (value > 10 && value <= 20) {
            return {
                color: '#ffff00',
                fontWeight: 'bold'
            };
        }
        if (value > 20) {
            return {
                color: '#ff7b7b',
                fontWeight: 'bold'
            };
        }

        return {};
    }
    """)

    # Construir grid options builder
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(filter=True)

    # Esconder colunas _NUM e detail
    for col in num_columns + percent_columns:
        if f"{col}_NUM" in df.columns:
            gb.configure_column(f"{col}_NUM", hide=True, type=["numericColumn"])
    if "detail" in df.columns:
        gb.configure_column("detail", hide=True)

    grid_options = gb.build()

    if df_details is not None:
        df['detail'] = df[coluns_merge_details].apply(
            lambda i: df_details[df_details[coluns_merge_details] == i].to_dict('records')
        )

        special_column = {
            "field": coluns_name_details,
            "cellRenderer": "agGroupCellRenderer",
            "checkboxSelection": False,
        }

        other_columns = []
        for col in df.columns:
            if col in [coluns_name_details, "detail"]:
                continue
            col_def = {"field": col}
            if col in num_columns + percent_columns:
                col_def["cellStyle"] = cellstyle_code
            other_columns.append(col_def)

        columnDefs = [special_column] + other_columns

        detail_columnDefs = [{"field": c} for c in df_details.columns]

        grid_options.update({
            "masterDetail": True,
            "columnDefs": columnDefs,
            "detailCellRendererParams": {
                "detailGridOptions": {
                    "columnDefs": detail_columnDefs,
                },
                "getDetailRowData": JsCode("function(params) {params.successCallback(params.data.detail);}"),
            },
            "rowData": df.to_dict('records'),
            "enableRangeSelection": True,
            "suppressRowClickSelection": True,
            "cellSelection": True,
            "rowHeight": 40,
            "defaultColDef": {
                "flex": 1,
                "minWidth": 100,
                "autoHeight": False,
                "filter": True,
            }
        })

    else:
        grid_options.update({
            "enableRangeSelection": True,
            "suppressRowClickSelection": False,
            "cellSelection": False,
            "rowHeight": 40,
            "defaultColDef": {
                "flex": 1,
                "minWidth": 100,
                "autoHeight": False,
                "filter": True,
            }
        })

    # Criar DataFrame sem colunas técnicas
    df_to_show2 = df.copy()
    cols_to_drop = [col for col in df.columns if col.endswith('_NUM') or col == 'detail']
    df_to_show = df.drop(columns=cols_to_drop, errors='ignore')

    # Ajustar columnDefs se não for masterDetail
    if "masterDetail" not in grid_options:
        grid_options["columnDefs"] = []
        for col in df_to_show.columns:
            col_def = {"field": col}
            if col in num_columns + percent_columns:
                col_def["cellStyle"] = cellstyle_code  # Aplica o estilo de cores
            grid_options["columnDefs"].append(col_def)

    # Adicionar efeito zebra (linhas alternadas)
    if st.session_state.get("base_theme") == "dark":
        custom_theme = (StAggridTheme(base="balham").withParams().withParts('colorSchemeDark'))
    # Zebra escura
        grid_options["getRowStyle"] = JsCode('''
        function(params) {
            if (params.node.rowIndex % 2 === 0) {
                return { background: '#222', color: '#fff' };
            } else {
                return { background: '#333', color: '#fff' };
            }
        }
        ''')
    else:
    # Zebra clara (padrão)
        custom_theme = (StAggridTheme(base="balham").withParams())
        grid_options["getRowStyle"] = JsCode('''
        function(params) {
            if (params.node.rowIndex % 2 === 0) {
                return { background: '#fff', color: '#111' };
            } else {
                return { background: '#e0e0e0', color: '#111' };
            }
        }
        ''')

    # Mostrar AgGrid
    grid_response = AgGrid(
        df_to_show2,
        gridOptions=grid_options,
        enable_enterprise_modules=True,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
        key=f"aggrid_{name}_{key}",
        theme=custom_theme
    )

    filtered_df = grid_response['data']
    filtered_df = filtered_df.drop(columns=[col for col in filtered_df.columns if col.endswith('_NUM')], errors='ignore')
    return filtered_df, len(filtered_df)

def component_filterMultiselect(df, column, text):
    options = df[column].unique().tolist()

    selected_options = st.multiselect(text, options, default=options)
    return selected_options

def component_filterDataSelect(key=None):
    data = ['Todos','Hoje','Amanhã']
    selected_data = st.selectbox('Escolha uma data:', data, index=0, key=key)
    return selected_data

def plotPizzaChart(labels, sizes, name):
    chart_key = f"{labels}_{sizes}_{name}_"
    if name: st.markdown(f"<h5 style='text-align: center; background-color: #ffb131; padding: 0.1em;'>{name}</h5>", unsafe_allow_html=True)
    
    # Preparar os dados para o gráfico
    data = [{"value": size, "name": label} for size, label in zip(sizes, labels)]
    
    options = {
        "tooltip": {
            "trigger": "item",
            "formatter": "{b}: {c} ({d}%)" 
        },
        "legend": {
            "orient": "vertical",
            "left": "left",
            "top": "top", 
            "textStyle": {
                "color": "orange"
            }
        },
        "grid": {  # Adicionado para organizar o layout
            "left": "50%", 
            "right": "50%", 
            "containLabel": True
        },
        "color": ["#06B23B", "#238686","#E7D919","#E71919"],  # Lista de cores personalizadas
        "series": [
            {
                "name": "Quantidade",
                "type": "pie",
                "radius": "75%",
                "center": ["45%", "40%"],  # Posiciona o gráfico no meio verticalmente
                "data": data,
                "label": {
                    "show": False  # Ocultar os textos nas fatias
                },
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": "rgba(0, 0, 0, 0.5)",
                    }
                },
            }
        ],
    }
    
    st_echarts(options=options, height="450px", key=chart_key)

