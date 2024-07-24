import requests
import os
import zipfile
import pandas as pd
import time
import pymysql
import numpy as np

def authorization():
    url = "https://login-api.transfeera.com/authorization"

    payload = {
        "grant_type": "client_credentials",
        "client_id": "ae374604-ec8e-4410-bd7a-03ed796d7b3b",
        "client_secret": "215531fd-4ecd-408d-ab04-8b5857394fc0c7a456b7-4f54-4cca-b7c7-b7d61662b95d"
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.json()


def request_report(token, start_date, end_date):
    url = "https://api.transfeera.com/statement_report"

    authorization = "Bearer " + token

    payload = {
        "format": "csv",
        "created_at__gte": start_date,
        "created_at__lte": end_date
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": authorization
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.json()


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

        diretorio_destino = "./files"

        # Cria o diretório se ele não existir
        if not os.path.exists(diretorio_destino):
            os.makedirs(diretorio_destino)

        with open(os.path.join(diretorio_destino, "relatorio.zip"), 'wb') as f:
            f.write(response.content)

        with zipfile.ZipFile(os.path.join(diretorio_destino, "relatorio.zip"), 'r') as zip_ref:
            filename = zip_ref.namelist()[0]
            zip_ref.extractall(diretorio_destino)
            os.rename(os.path.join(diretorio_destino, filename), os.path.join(diretorio_destino, "extrato.csv"))

        return True
    except Exception as e:
        print(e)
        return False


def read_report():
    df = pd.read_csv("./files/extrato.csv")
    os.remove('./files/extrato.csv')
    os.remove('./files/relatorio.zip')

    print(df, df.columns)

    df = df[df["Crédito / Débito"] == "D"]

    df["Chave / Dado bancário"] = df["Chave / Dado bancário"].apply(lambda x: x.split(' ') if isinstance(x, str) else x)
    df["Banco"] = df["Chave / Dado bancário"].apply(lambda x: x[1] if isinstance(x, list) and len(x) > 1 else None)
    df["Agencia"] = df["Chave / Dado bancário"].apply(lambda x: x[3] if isinstance(x, list) and len(x) > 3 else None)
    df["Tipo de Conta"] = df["Chave / Dado bancário"].apply(lambda x: x[-4] if isinstance(x, list) and len(x) > 3 else None)
    df["Conta"] = df["Chave / Dado bancário"].apply(lambda x: x[-3] if isinstance(x, list) and len(x) > 3 else None)
    df["Digito"] = df["Chave / Dado bancário"].apply(lambda x: x[-1] if isinstance(x, list) and len(x) > 1 else None)
    df["Titular"] = df["Descrição"].apply(lambda x: x.split('"')[1] if isinstance(x, str) else x)

    df = df[["Data", "Crédito / Débito", "Tipo", "ID do pagamento", "Valor", "ID de integração", "Banco", "Agencia", "Tipo de Conta", "Conta", "Digito", "Titular"]]

    df["Valor"] = df["Valor"].abs()
    df["Valor"] = df["Valor"].map("{:.2f}".format)  

    return df


def insert_epm(tid, fid, data):
    login_data = {
        "username": "fabio.pereira@eshows.com.br",
        "password": "Fgp090501!",
        "loginSource": 1,
    }
    login = requests.post(
        'https://apps.eshows.com.br/eshows/Security/Login',
        json=login_data).json()
    ticket = login['data']['auth_ticket']

    headersEPM = {'Content-Type': 'application/json', 'auth': ticket}

    data3 = {
        "tid": tid,
        "fid": fid,
        "data": data,
        "type": 1,
    }
    create = requests.post(
        "https://apps.eshows.com.br/eshows/Integration/Save",
        headers=headersEPM,
        json=data3).json()
    print('Adição', create)


def insert_database(df):
    df.fillna(value='', inplace=True)
    for index, row in df.iterrows():
        print(row["Data"], row["Tipo"], row["ID do pagamento"], row["Valor"], row["ID de integração"], row["Banco"], row["Agencia"], row["Tipo de Conta"], row["Conta"], row["Digito"])
        insert_epm("VF9DT05DSUxJQUNBT19QQUdBTUVOVE9TOjE4MTQzOA==", 293, {
            "DATA_PAGAMENTO": row["Data"],
            "TIPO_DE_TRANSACAO": row["Tipo"],
            "ID_TRANSACAO": row["ID do pagamento"],
            "VALOR_PAGAMENTO": row["Valor"],
            "ID_INTEGRACAO": row["Titular"],
            "BANCO": row["Banco"],
            "CONTA": row["Conta"],
            "TIPO_DE_CONTA": row["Tipo de Conta"],
            "AGENCIA": row["Agencia"],
            "DIGITO_CONTA": row["Digito"],
        })


# Código principal
token = authorization().get("access_token")
request_id = request_report(token, "2024-06-07", "2024-07-03").get("id")
time.sleep(50)
file_url = get_report_url(token, request_id).get("file_url")
response = download_report(file_url)

if response:
    report = read_report()
    print(report)
    insert_database(report)

    #dias subidos 01/05 a 03/07 
    #teremos que testar depois uma maneira de deixar automatico e verificar se os dias em que não ocorreram pagamentos irão atrapalhar o código de funcionar