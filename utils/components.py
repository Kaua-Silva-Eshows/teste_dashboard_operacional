import streamlit as st
from streamlit_echarts import st_echarts

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
    keywords = ['VER DETALHES', 'VER CANDIDATOS', 'DISPARAR WPP', 'PERFIL ARTISTA'] # usado para procurar colunas que contenham links
    columns_with_link = [col_name for col_name in df.columns if any(keyword in col_name.upper() for keyword in keywords)]
    
    if columns_with_link:
        column_config = {
            col: st.column_config.LinkColumn(
                col, display_text="[Saiba mais]"
            ) for col in columns_with_link
        }
        st.dataframe(df, use_container_width=True, column_config=column_config, hide_index=True)
    else:
        st.dataframe(df, hide_index=True, use_container_width=True)

def component_filterMultiselect(df, column, text):
    options = df[column].unique().tolist()

    selected_options = st.multiselect(text, options, default=options)
    return selected_options

def component_filterDataSelect():
    data = ['Todos','Hoje','Amanhã']
    selected_data = st.selectbox('Escolha uma data:', data, index=0)
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
