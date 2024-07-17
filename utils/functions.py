import pandas as pd
from datetime import datetime, timedelta, time
import streamlit as st


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