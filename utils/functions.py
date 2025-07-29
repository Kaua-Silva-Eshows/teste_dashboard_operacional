import random
import pandas as pd
from datetime import datetime, timedelta, time
import streamlit as st
import os
from data.queries import hole_map
import streamlit.components.v1 as components


# retorna um dataframe filtrado pelas data de hoje
def function_get_today_data(df):
    today = datetime.now().date()
    try:
        df['DATA INÍCIO'] = pd.to_datetime(df['DATA INÍCIO'],format='%d/%m/%Y', errors='coerce').dt.date
        filtered_df = df[df['DATA INÍCIO'] == today]
        filtered_df['DATA INÍCIO'] = filtered_df['DATA INÍCIO'].apply(lambda x: x.strftime('%d/%m/%Y') if pd.notnull(x) else '')

        
    except:
        return df
    return filtered_df

def function_get_today_tomorrow_date(df, data):
    df['DATA INÍCIO'] = pd.to_datetime(df['DATA INÍCIO'], format='%d/%m/%Y',).dt.date
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    if data == 'Hoje':
        df = df[df['DATA INÍCIO'] == today]
    elif data == 'Amanhã':
        df = df[df['DATA INÍCIO'] == tomorrow]
    df['DATA INÍCIO'] = df['DATA INÍCIO'].apply(lambda x: x.strftime('%d/%m/%Y') if pd.notnull(x) else '')
    return df

def function_filter_hourly(df, showtime):
    df['HORÁRIO INÍCIO'] = pd.to_datetime(df['HORÁRIO INÍCIO'], format='%H:%M').dt.time
    
    if showtime == 'Almoço':
        filtered = df[(df['HORÁRIO INÍCIO'] >= pd.to_datetime('11:00').time()) &
                                (df['HORÁRIO INÍCIO'] <= pd.to_datetime('14:30').time())]
    elif showtime == 'Happy Hour':
        filtered1 = df[(df['HORÁRIO INÍCIO'] >= pd.to_datetime('14:31').time()) &
                                (df['HORÁRIO INÍCIO'] <= pd.to_datetime('17:30').time())]
        filtered2 = df[(df['HORÁRIO INÍCIO'] >= pd.to_datetime('23:01').time()) |
                                (df['HORÁRIO INÍCIO'] <= pd.to_datetime('10:59').time())]
        filtered = pd.concat([filtered1, filtered2]).reset_index(drop=True) #pd.concat ferramenta do pandas que concatena (nesse caso) os filtros do dataframe

    elif showtime == 'Jantar':
        filtered = df[(df['HORÁRIO INÍCIO'] >= pd.to_datetime('17:31').time()) &
                                (df['HORÁRIO INÍCIO'] <= pd.to_datetime('23:00').time())] 

    elif showtime == 'Todos':
        filtered = df


    return filtered
    
def function_calculate_artistFavoriteBlocked(df):
    # Contar quantas linhas têm zero em todos os campos 'FAVORITO', 'BLOQUEADO', e 'APROVADO'
    zero_count = df.apply(lambda row: all(row[['FAVORITO', 'BLOQUEADO', 'APROVADO']] == 0), axis=1).sum()

    # Contar quantas linhas têm 1 em pelo menos dois dos campos 'FAVORITO', 'BLOQUEADO', e 'APROVADO'
    count_at_least_two_ones = df.apply(lambda row: (row[['FAVORITO', 'BLOQUEADO', 'APROVADO']] == 1).sum() >= 2, axis=1).sum()

    # Filtrar linhas com 0 nas três colunas e linhas com 1 em pelo menos duas das colunas
    zero_in_all_three = df.apply(lambda row: all(row[['FAVORITO', 'BLOQUEADO', 'APROVADO']] == 0), axis=1) 
    one_in_at_least_two = df.apply(lambda row: (row[['FAVORITO', 'BLOQUEADO', 'APROVADO']] == 1).sum() >= 2, axis=1)

    # Criar um DataFrame secundário com linhas que atendem a qualquer uma das condições
    filtered_df = df.loc[zero_in_all_three | one_in_at_least_two]

    return filtered_df, count_at_least_two_ones, zero_count

def function_update_csv(df, csv):
    new_df = (df[['ID PROPOSTA', 'LAST_UPDATE']])
    csv = "./assets/csvs/holemap.csv"
    existing_csv = pd.read_csv(csv)
    # Comparar os dados existentes com os novos dados do DataFrame
    new_data = new_df[~new_df.isin(existing_csv)].dropna()  # Filtrar os novos dados que não estão no CSV existente
    #juntar o csv com new_data e sobrescrever o arquivo csv local
    updated_csv = pd.concat([existing_csv, new_data]).drop_duplicates()
    updated_csv.to_csv(csv, index=False)
    
    return updated_csv

def function_add_outputdate_in_solved_itens(df, csv):
    ids_csv = set(csv['ID PROPOSTA'])
    ids_df = set(df['ID PROPOSTA'])
    missing_ids = ids_csv - ids_df
    
    # Filtrar os registros do CSV que têm os IDs ausentes
    missing_records = csv[csv['ID PROPOSTA'].isin(missing_ids)]
    
    current_datetime = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    missing_records['OUTPUT_DATE'] = current_datetime

    csv.loc[csv['ID PROPOSTA'].isin(missing_ids), 'OUTPUT_DATE'] = current_datetime
    
def function_add_outputdate_in_solved_itens(df, csv):
    ids_csv = set(csv['ID PROPOSTA'])
    ids_df = set(df['ID PROPOSTA'])
    missing_ids = ids_csv - ids_df
    
    # Filtrar os registros do CSV que têm os IDs ausentes
    missing_records = csv[csv['ID PROPOSTA'].isin(missing_ids)]
    
    current_datetime = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    missing_records['OUTPUT_DATE'] = current_datetime

    csv.loc[csv['ID PROPOSTA'].isin(missing_ids), 'OUTPUT_DATE'] = current_datetime
    
    return csv

def filter_by_hour(df, now_datetime):
    now_hour = now_datetime.hour
    return df[df['OUTPUT_DATE'].dt.hour == now_hour]

def filter_by_day(df, now_datetime):
    return df[df['OUTPUT_DATE'].dt.date == now_datetime.date()]

def filter_by_week(df, now_datetime):
    current_week = now_datetime.isocalendar().week
    current_year = now_datetime.year
    return df[(df['OUTPUT_DATE'].dt.isocalendar().week == current_week) &
              (df['OUTPUT_DATE'].dt.year == current_year)]

def filter_by_month(df, now_datetime):
    current_month = now_datetime.month
    current_year = now_datetime.year
    return df[(df['OUTPUT_DATE'].dt.month == current_month) &
              (df['OUTPUT_DATE'].dt.year == current_year)]

def calculate_average_time_diff(df):
    return (df['OUTPUT_DATE'] - df['LAST_UPDATE']).mean()

def function_calculate_average_hole_time(csv, option):
    try:
        if csv is None: return 0
        if option is None: option = 'Hora'
        now_datetime = datetime.now()

        output_date_not_null = csv[csv['OUTPUT_DATE'].notnull()].copy()
        output_date_not_null['OUTPUT_DATE'] = pd.to_datetime(output_date_not_null['OUTPUT_DATE'])
        output_date_not_null['LAST_UPDATE'] = pd.to_datetime(output_date_not_null['LAST_UPDATE'])
        
        if option == 'Hora':
            filtered_df = filter_by_day(output_date_not_null, now_datetime)
            filtered_df = filter_by_hour(filtered_df, now_datetime)
        elif option == 'Semana':
            filtered_df = filter_by_week(output_date_not_null, now_datetime)
        elif option == 'Mês':
            filtered_df = filter_by_month(output_date_not_null, now_datetime)
        else:
            st.error(f"Opção desconhecida: {option}")
            return None
        
        average_time_diff = calculate_average_time_diff(filtered_df)
        return average_time_diff
    except:
        return 0

def format_timedelta_to_pt_br(timedelta):
    try:
        # Extrair dias, horas, minutos e segundos do timedelta
        total_seconds = int(timedelta.total_seconds())
        days = total_seconds // (24 * 3600)
        total_seconds = total_seconds % (24 * 3600)
        hours = total_seconds // 3600
        total_seconds = total_seconds % 3600
        minutes = total_seconds // 60
        seconds = total_seconds % 60

        # Formatar para o padrão desejado
        formatted_time = f"{days} dias {hours:02}:{minutes:02}:{seconds:02}"
        return formatted_time
    except:
        return timedelta
    
def function_rename_holemap(day_Hole1,day_Hole2):
        df_renomed = hole_map(day_Hole1, day_Hole2).rename(columns={
        'ID': 'ID PROPOSTA',
        'ARTISTA_ORIGINAL': 'ARTISTA ORIGINAL',
        'DATA_INICIO': 'DATA INÍCIO',
        'HORARIO': 'HORARIO',
        'ESTABELECIMENTO': 'ESTABELECIMENTO',
        'KEY_ACCOUNT': 'KEY_ACCOUNT',
        'PALCO': 'PALCO',
        'FORMACAO': 'FORMAÇÃO',
        'ID_OPORTUNIDADE': 'ID OPORTUNIDADE',
        'OBSERVACAO': 'OBSERVAÇÃO',
        'PROBLEMA': 'PROBLEMA',
        'MOTIVO': 'MOTIVO',
        'STATUS_FINAL': 'STATUS FINAL',
        'ORIGEM': 'ORIGEM',
        'STATUS_COMPANY': 'STATUS DA EMPRESA',
        'VER_PROPOSTA_ORIGINAL': 'VER PROPOSTA ORIGINAL',
        'LAST_UPDATE': 'LAST_UPDATE'
    })
        return df_renomed

def overlap(start1, end1, start2, end2):
    #Retorna True se os intervalos (start1, end1) e (start2, end2) se sobrepõem.
    return max(start1, start2) < min(end1, end2)

def find_overlaps(df):
    filtered = []
    for i, row1 in df.iterrows():
        for j, row2 in df.iterrows():
            if i != j and row1['Estabelecimento Show Padrão'] == row2['Estabelecimento Show Padrão'] and row1['Data Inicio Proposta'] == row2['Data Inicio Proposta']:
                if overlap(row1['Hora Inicio Show Padrão'], row1['Hora Fim Show Padrão'], row2['Hora Inicio Show Padrão'], row2['Hora Fim Show Padrão']):
                    filtered.append(row1)
                    filtered.append(row2)
    return pd.DataFrame(filtered).drop_duplicates()

def function_copy_dataframe_as_tsv(df):
    # Converte o DataFrame para uma string TSV
    df_tsv = df.to_csv(index=False, sep='\t')
    
    # Gera código HTML e JavaScript para copiar o conteúdo para a área de transferência
    components.html(
        f"""
        <style>
            .custom-copy-btn {{
                background: linear-gradient(90deg, #ffb131 0%, #ff7f50 100%);
                color: #fff;
                border: none;
                padding: 12px 28px 12px 18px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                display: inline-flex;
                align-items: center;
                box-shadow: 0 2px 8px rgba(0,0,0,0.10);
                transition: background 0.3s, color 0.3s;
                position: relative;
                gap: 8px;
            }}
            .custom-copy-btn:hover {{
                background: linear-gradient(90deg, #ff7f50 0%, #ffb131 100%);
                color: #222;
            }}
            .copy-icon {{
                width: 20px;
                height: 20px;
                vertical-align: middle;
                fill: currentColor;
            }}
        </style>
        <textarea id="clipboard-textarea" style="position: absolute; left: -10000px;">{df_tsv}</textarea>
        <button class="custom-copy-btn" id="copy-btn" onclick="copyDF()">
            <svg class='copy-icon' viewBox='0 0 24 24'><path d='M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z'/></svg>
            <span id="copy-btn-text">Copiar DataFrame</span>
        </button>
        <script>
        function copyDF() {{
            var textarea = document.getElementById('clipboard-textarea');
            textarea.select();
            document.execCommand('copy');
            var btn = document.getElementById('copy-btn');
            var btnText = document.getElementById('copy-btn-text');
            btnText.innerText = 'Copiado!';
            btn.style.background = 'linear-gradient(90deg, #4BB543 0%, #43e97b 100%)';
            setTimeout(function() {{
                btnText.innerText = 'Copiar DataFrame';
                btn.style.background = 'linear-gradient(90deg, #ffb131 0%, #ff7f50 100%)';
            }}, 1500);
        }}
        </script>
        """,
        height=110
    )

def highlight_canceled(row, column='', canceled_statuses=None):
    if canceled_statuses is None:
        canceled_statuses = ['Pendente', '—']
    
    color = 'background-color: red' if row[column] in canceled_statuses else ''
    return [color] * len(row)

def highlight_recent_dates(row, column='', today=None):
    if today is None:
        today = datetime.today()
    
    five_days_ago = today - timedelta(days=5)
    
    if isinstance(row[column], pd.Timestamp) and row[column] > five_days_ago:
        return ['background-color: orange'] * len(row)
    else:
        return [''] * len(row)

def function_box_lenDf(len_df,df,y='', x='', box_id=''):
    len_df = len(df)
    st.markdown(
        """
        <style>
        .small-box {
            border: 1px solid #ffb131; /* Cor da borda */
            border-radius: 5px; /* Cantos arredondados */
            padding: 10px; /* Espaçamento interno */
            background-color: transparent; /* Cor de fundo da caixa */
            box-shadow: 0px 0px 5px rgba(0, 0, 0, 0.1); /* Sombra */
            font-size: 14px; /* Tamanho da fonte */
            font-weight: bold; /* Negrito */
            text-align: center; /* Alinhamento do texto */
            width: 150px; /* Largura da caixinha */
            z-index: 1; /* Garantir que a caixa fique acima de outros elementos */
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # CSS para o posicionamento específico via ID
    st.markdown(
        f"""
        <style>
        #{box_id} {{
            position: absolute; /* Posicionamento absoluto */
            top: {y}px; /* Distância do topo da página */
            left: {x}px; /* Distância da borda esquerda da página */
        }}
        </style>
        <div id="{box_id}" class="small-box">
            O DataFrame contém <span style="color: #ffb131;">{len_df}</span> itens.
        </div>
        """,
        unsafe_allow_html=True
    )

