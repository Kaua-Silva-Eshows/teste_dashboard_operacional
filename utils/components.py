import streamlit as st
from streamlit_echarts import st_echarts
from datetime import datetime, timedelta
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import JsCode
from st_aggrid import GridUpdateMode

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
    st.markdown("""
    <style>
        .full-width-line-white {
            width: 100%;
            border-bottom: 1px solid #ffffff;
            margin-bottom: 0.5em;
        }
        .full-width-line-black {
            width: 100%;
            border-bottom: 1px solid #000000;
            margin-bottom: 0.5em;
        }
    </style>
    """, unsafe_allow_html=True)

def component_plotDataframe(df, name):
    st.markdown(f"<h5 style='text-align: center; background-color: #ffb131; padding: 0.1em;'>{name}</h5>", unsafe_allow_html=True)
    keywords = ['VER DETALHES', 'VER CANDIDATOS', 'DISPARAR WPP', 'PERFIL ARTISTA']  # usado para procurar colunas que contenham links
    columns_with_link = [col_name for col_name in df.columns if any(keyword in col_name.upper() for keyword in keywords)]
    
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(filter=True)  # Habilitar filtro para todas as colunas
    
    # Configurar a seleção de linhas (opcional)
    gb.configure_selection(
        selection_mode='multiple',  # 'single' ou 'multiple'
        use_checkbox=False,         # Habilitar caixas de seleção
        pre_selected_rows=[],
        suppressRowClickSelection=False  # Permite selecionar ao clicar em qualquer célula
    )
    
    grid_options = gb.build()

    # Adicionar configurações adicionais para seleção de células
    grid_options.update({
        "enableRangeSelection": True,         # Habilita a seleção por faixa
        "suppressRowClickSelection": True,    # Impede a seleção de linha ao clicar
        "cellSelection": True                  # Habilita a seleção de células
    })

    # Exibir o DataFrame usando AgGrid com filtros
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        enable_enterprise_modules=True,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True  # Ajusta as colunas automaticamente ao carregar
        
    )

    # Recupera o DataFrame filtrado
    filtered_df = grid_response['data']

    return filtered_df

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

