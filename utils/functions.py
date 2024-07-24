import pandas as pd
from datetime import datetime, timedelta, time
import streamlit as st
import os
from data.queries import hole_map


# retorna um dataframe filtrado pelas data de hoje
def function_get_today_data(df):
    today = datetime.now().date()
    try:
        df['DATA INÍCIO'] = pd.to_datetime(df['DATA INÍCIO'], errors='coerce').dt.date
        filtered_df = df[df['DATA INÍCIO'] == today]
        filtered_df['DATA INÍCIO'] = filtered_df['DATA INÍCIO'].apply(lambda x: x.strftime('%d/%m/%Y') if pd.notnull(x) else '')
    except:
        return df
    return filtered_df

def function_get_today_tomorrow_date(showMonitoring, data):
    showMonitoring['DATA INÍCIO'] = pd.to_datetime(showMonitoring['DATA INÍCIO'], errors='coerce').dt.date
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    if data == 'Hoje':
        showMonitoring = showMonitoring[showMonitoring['DATA INÍCIO'] == today]
    elif data == 'Amanhã':
        showMonitoring = showMonitoring[showMonitoring['DATA INÍCIO'] == tomorrow]
    showMonitoring['DATA INÍCIO'] = showMonitoring['DATA INÍCIO'].apply(lambda x: x.strftime('%d/%m/%Y') if pd.notnull(x) else '')
    return showMonitoring

def function_filter_hourly(df, showtime):
    df['HORÁRIO INÍCIO'] = pd.to_datetime(df['HORÁRIO INÍCIO'], format='%H:%M').dt.time
    
    if showtime == 'Almoço':
        filtered = df[(df['HORÁRIO INÍCIO'] >= pd.to_datetime('11:00').time()) &
                                (df['HORÁRIO INÍCIO'] <= pd.to_datetime('15:30').time())]
    elif showtime == 'Happy Hour':
        filtered = df[(df['HORÁRIO INÍCIO'] >= pd.to_datetime('15:31').time()) &
                                (df['HORÁRIO INÍCIO'] <= pd.to_datetime('19:30').time())]
    elif showtime == 'Jantar':
        filtered = df[(df['HORÁRIO INÍCIO'] >= pd.to_datetime('19:31').time())]

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
    
def function_rename_holemap():
        df_renomed = hole_map().rename(columns={
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


