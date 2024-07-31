import streamlit as st
import requests
import zipfile
import io
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def authorization():
    transfeera_config = st.secrets["tranfeera"]
    url = "https://login-api.transfeera.com/authorization"

    payload = {
        "grant_type": transfeera_config['grant_type'],
        "client_id": transfeera_config['client_id'],
        "client_secret": transfeera_config['client_secret'] 
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        st.error(f"Erro na autenticação: {response.text}")
        return None

def get_dates():
    today = datetime.today()
    first_day_current_month = today.replace(day=1)
    last_day_current_month = (first_day_current_month + relativedelta(months=1)) - timedelta(days=1)
    first_day_three_months_ago = first_day_current_month - relativedelta(months=3)

    start_date = first_day_three_months_ago.strftime("%Y-%m-%d")
    end_date = last_day_current_month.strftime("%Y-%m-%d")

    return start_date, end_date

def get_statement_response(token):
    start_date, end_date = get_dates()
    url = "https://api.transfeera.com/statement_report"

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "format": "csv",
        "created_at__gte": start_date,
        "created_at__lte": end_date
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Erro na requisição do relatório de extrato: {response.text}")
        return None

def get_report_url(token, request_id):
    url = "https://api.transfeera.com/statement_report/" + request_id

    authorization = "Bearer " + token

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": authorization
    }

    print(url)

    response = requests.get(url, headers=headers)

    return response.json()

def download_report(file_url):
    try:
        response = requests.get(file_url)
        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            filename = zip_ref.namelist()[0]
            with zip_ref.open(filename) as csvfile:
                df = pd.read_csv(csvfile)

        return df
    except Exception as e:
        st.error(f"Erro ao baixar e processar o relatório: {e}")
        return None

@st.cache_data
def get_statement_report():
    token = authorization()
    request_id = get_statement_response(token).get("id")
    time.sleep(50)
    file_url = get_report_url(token, request_id).get("file_url")
    response = download_report(file_url)
    return response