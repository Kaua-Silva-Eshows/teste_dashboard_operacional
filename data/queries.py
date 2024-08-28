from data.dbconnect import get_dataframe_from_query
import streamlit as st
import time

@st.cache_data
def show_monitoring_today_and_tomorrow():
    return get_dataframe_from_query("""
    SELECT
P.ID AS 'ID PROPOSTA',
S.DESCRICAO AS 'STATUS',
C.NAME AS ESTABELECIMENTO,
C.CITY AS CIDADE,
C.LOGRADOURO AS ENDEREÇO,
A.NOME AS ARTISTA,
DATE_FORMAT(P.DATA_INICIO, '%d/%m/%Y') AS 'DATA INÍCIO',
DATE_FORMAT(DATA_INICIO, '%H:%i') AS 'HORÁRIO INÍCIO',
DATE_FORMAT(DATA_FIM, '%H:%i') AS 'HORÁRIO FIM',

CASE
WHEN LENGTH(REPLACE(REPLACE (REPLACE (REPLACE (A.CELULAR, '(', ''), ')', ''), '-', ''), ' ', '')) > 12 AND SUBSTRING(REPLACE(REPLACE (REPLACE (REPLACE (A.CELULAR, '(', ''), ')', ''), '-', ''), ' ', ''), 3,2) NOT IN (11, 16, 19, 21, 27, 18, 22, 12)
THEN REPLACE(REPLACE (REPLACE (REPLACE (A.CELULAR, '(', ''), ')', ''), '-', ''), ' ', '')
WHEN LENGTH(REPLACE(REPLACE (REPLACE (REPLACE (A.CELULAR, '(', ''), ')', ''), '-', ''), ' ', '')) = 11 AND SUBSTRING(REPLACE(REPLACE (REPLACE (REPLACE (A.CELULAR, '(', ''), ')', ''), '-', ''), ' ', ''), 1,2) NOT IN (11, 16, 19, 21, 27, 18, 22, 12)
THEN CONCAT('55', SUBSTRING(REPLACE(REPLACE (REPLACE (REPLACE (A.CELULAR, '(', ''), ')', ''), '-', ''), ' ', ''), 1,2), SUBSTRING(REPLACE(REPLACE (REPLACE (REPLACE (A.CELULAR, '(', ''), ')', ''), '-', ''), ' ', ''), 4, 8))
WHEN LENGTH(REPLACE(REPLACE (REPLACE (REPLACE (A.CELULAR, '(', ''), ')', ''), '-', ''), ' ', '')) = 10 AND SUBSTRING(REPLACE(REPLACE (REPLACE (REPLACE (A.CELULAR, '(', ''), ')', ''), '-', ''), ' ', ''), 1,2) NOT IN (11, 16, 19, 21, 27, 18, 22, 12)
THEN CONCAT('55', REPLACE (REPLACE (REPLACE (REPLACE (A.CELULAR, '(', ''), ')', ''), '-', ''), ' ', ''))
WHEN LENGTH(REPLACE(REPLACE (REPLACE (REPLACE (A.CELULAR, '(', ''), ')', ''), '-', ''), ' ', '')) > 12 AND SUBSTRING(REPLACE(REPLACE (REPLACE (REPLACE (A.CELULAR, '(', ''), ')', ''), '-', ''), ' ', ''), 3,2) IN (11, 16, 19, 21, 27, 18, 22, 12)
THEN REPLACE(REPLACE (REPLACE (REPLACE (A.CELULAR, '(', ''), ')', ''), '-', ''), ' ', '')
WHEN LENGTH(REPLACE(REPLACE (REPLACE (REPLACE (A.CELULAR, '(', ''), ')', ''), '-', ''), ' ', '')) = 11 AND SUBSTRING(REPLACE(REPLACE (REPLACE (REPLACE (A.CELULAR, '(', ''), ')', ''), '-', ''), ' ', ''), 1,2) IN (11, 16, 19, 21, 27, 18, 22, 12)
THEN CONCAT('55',REPLACE(REPLACE (REPLACE (REPLACE (A.CELULAR, '(', ''), ')', ''), '-', ''), ' ', ''))
ELSE A.CELULAR
END AS 'CELULAR DO ARTISTA',
                                    
DATE_FORMAT(CIN.HORARIO_CHECKIN, '%H:%i') AS 'HORÁRIO CHECKIN',
CASE WHEN CIN.AUTOMATICO = 1 THEN 'AUTOMATICO' 
ELSE CIN.RESPONSAVEL_CASA 
END AS 'OBSERVAÇÃO CHECKIN',                                    
DATE_FORMAT(CUT.HORARIO_CHECKOUT, '%H:%i') AS 'HORÁRIO CHECKOUT',

CASE 
WHEN R.CONFIRMACAO = 0 THEN 'Negativa'
WHEN R.CONFIRMACAO = 1 THEN 'Positiva'
WHEN R.CONFIRMACAO IS NULL THEN 'Aguardando'
WHEN MCP.FK_PROPOSTA IS NOT NULL THEN 'Cancelamento'
END AS 'CONFIRMAÇÃO',

CASE 
WHEN MCP.FK_PROPOSTA IS NOT NULL THEN 'SIM'
END AS 'SOLICITAÇÃO DE CANCELAMENTO',

CASE
WHEN SPP.FK_PROPOSTA IS NOT NULL THEN 'SIM'
END AS 'SINALIZOU PROBLEMA',

CASE
WHEN MCP.FK_PROPOSTA IS NOT NULL THEN CONCAT(MC.TEXTO_MOTIVO, ': ', COALESCE(MCP.DESCRICAO_CANCELAMENTO, "sem comentários"))
WHEN SPP.FK_PROPOSTA IS NOT NULL THEN CONCAT(SP.TITULO, ': ', COALESCE(SPP.SINAL_PROBLEMA_DESCRICAO, "sem comentários"))
ELSE NULL
END AS 'OBSERVAÇÃO DO ARTISTA',

TAD.NUMERO_SHOWS AS 'NÚMERO DE SHOWS',

(SELECT COUNT(*)
FROM T_PROPOSTAS P2
WHERE P2.FK_CONTRATADO = P.FK_CONTRATADO AND P2.FK_CONTRANTE = P.FK_CONTRANTE
AND P2.FK_CONTRANTE NOT IN (102,343,633,632)
AND P2.FK_STATUS_PROPOSTA IN (100,101,103,104)) AS 'NÚMERO DE SHOWS NA CASA',

CASE 
WHEN P.VALOR_BRUTO = P.VALOR_LIQUIDO THEN 'Sem Comissão'
ELSE 'Com Comissão'
END AS 'COMISSÃO',

CASE WHEN P.OCULTO_TABELA_ADMIN = 1 AND P.CONTA IS NOT NULL THEN P.CONTA
WHEN P.OCULTO_TABELA_ADMIN = 1 AND P.CONTA IS NULL THEN 'Resolvido sem observações' 
END AS 'STATUS MANUAL',
TSC.STATUS AS 'STATUS ESTABELECIMENTO',

CONCAT('https://admin.eshows.com.br/proposta/', P.ID) AS 'VER DETALHES'

FROM T_PROPOSTAS P
INNER JOIN T_COMPANIES C ON P.FK_CONTRANTE = C.ID
INNER JOIN T_ATRACOES A ON P.FK_CONTRATADO = A.ID
LEFT JOIN T_PROPOSTA_STATUS S ON P.FK_STATUS_PROPOSTA = S.ID
LEFT JOIN T_SINAL_PROBLEMA_PROPOSTA SPP ON SPP.FK_PROPOSTA = P.ID
LEFT JOIN T_SINAL_PROBLEMA SP ON SP.ID = SPP.FK_SINAL_PROBLEMA
LEFT JOIN T_MOTIVO_CANCELAMENTO_PROPOSTA MCP ON MCP.FK_PROPOSTA = P.ID
LEFT JOIN T_MOTIVO_CANCELAMENTO MC ON MC.ID = MCP.FK_ID_SOLICITACAO_CANCELAMENTO
LEFT JOIN T_STATUS_COMPANIES TSC ON TSC.ID = C.FK_STATUS_COMPANY
LEFT JOIN T_CHECKIN CIN ON CIN.FK_PROPOSTA = P.ID
LEFT JOIN T_CHECKOUT CUT ON CUT.FK_PROPOSTA = P.ID
LEFT JOIN T_RECONFIRMACAO R ON R.FK_PROPOSTA = P.ID
INNER JOIN T_ATRACOES_DADOS TAD ON A.ID = TAD.FK_ATRACAO

WHERE
P.FK_CONTRANTE NOT IN (102,343,633,632)
AND P.FK_STATUS_PROPOSTA IN (100,101,103,104)
AND P.DATA_INICIO BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 2 DAY)
AND C.CONTROLADORIA_ESHOWS = 1
AND A.ID NOT IN (12166)

GROUP BY P.ID
ORDER BY P.DATA_INICIO ASC;
    """)

@st.cache_data
def show_in_next_one_hour():
    return get_dataframe_from_query("""
    SELECT 
    tp.ID as 'ID PROPOSTA',
    CASE
    WHEN LENGTH(REPLACE(REPLACE (REPLACE (REPLACE (ta.CELULAR, '(', ''), ')', ''), '-', ''), ' ', '')) > 12 AND SUBSTRING(REPLACE(REPLACE (REPLACE (REPLACE (ta.CELULAR, '(', ''), ')', ''), '-', ''), ' ', ''), 3,2) NOT IN (11, 16, 19, 21, 27, 18, 22, 12)
    THEN REPLACE(REPLACE (REPLACE (REPLACE (ta.CELULAR, '(', ''), ')', ''), '-', ''), ' ', '')
    WHEN LENGTH(REPLACE(REPLACE (REPLACE (REPLACE (ta.CELULAR, '(', ''), ')', ''), '-', ''), ' ', '')) = 11 AND SUBSTRING(REPLACE(REPLACE (REPLACE (REPLACE (ta.CELULAR, '(', ''), ')', ''), '-', ''), ' ', ''), 1,2) NOT IN (11, 16, 19, 21, 27, 18, 22, 12)
    THEN CONCAT('55', SUBSTRING(REPLACE(REPLACE (REPLACE (REPLACE (ta.CELULAR, '(', ''), ')', ''), '-', ''), ' ', ''), 1,2), SUBSTRING(REPLACE(REPLACE (REPLACE (REPLACE (ta.CELULAR, '(', ''), ')', ''), '-', ''), ' ', ''), 4, 8))
    WHEN LENGTH(REPLACE(REPLACE (REPLACE (REPLACE (ta.CELULAR, '(', ''), ')', ''), '-', ''), ' ', '')) = 10 AND SUBSTRING(REPLACE(REPLACE (REPLACE (REPLACE (ta.CELULAR, '(', ''), ')', ''), '-', ''), ' ', ''), 1,2) NOT IN (11, 16, 19, 21, 27, 18, 22, 12)
    THEN CONCAT('55', REPLACE (REPLACE (REPLACE (REPLACE (ta.CELULAR, '(', ''), ')', ''), '-', ''), ' ', ''))
    WHEN LENGTH(REPLACE(REPLACE (REPLACE (REPLACE (ta.CELULAR, '(', ''), ')', ''), '-', ''), ' ', '')) > 12 AND SUBSTRING(REPLACE(REPLACE (REPLACE (REPLACE (ta.CELULAR, '(', ''), ')', ''), '-', ''), ' ', ''), 3,2) IN (11, 16, 19, 21, 27, 18, 22, 12)
    THEN REPLACE(REPLACE (REPLACE (REPLACE (ta.CELULAR, '(', ''), ')', ''), '-', ''), ' ', '')
    WHEN LENGTH(REPLACE(REPLACE (REPLACE (REPLACE (ta.CELULAR, '(', ''), ')', ''), '-', ''), ' ', '')) = 11 AND SUBSTRING(REPLACE(REPLACE (REPLACE (REPLACE (ta.CELULAR, '(', ''), ')', ''), '-', ''), ' ', ''), 1,2) IN (11, 16, 19, 21, 27, 18, 22, 12)
    THEN CONCAT('55',REPLACE(REPLACE (REPLACE (REPLACE (ta.CELULAR, '(', ''), ')', ''), '-', ''), ' ', ''))
    ELSE ta.CELULAR
    END AS 'CELULAR DO ARTISTA',

    ta.ID as 'ID ARTISTA',
    ta.NOME as 'ARTISTA',
    tc.NAME as 'ESTABELECIMENTO',
    DATE_FORMAT(tp.DATA_INICIO, '%d/%m/%Y') as 'DATA INÍCIO',
    DATE_FORMAT(tp.DATA_INICIO, '%H:%i') AS 'HORÁRIO INÍCIO',
    TIMESTAMPDIFF(MINUTE, NOW(), tp.DATA_INICIO) as 'MINUTOS FALTANTES',
    tps.DESCRICAO as 'STATUS',
    CASE 
    WHEN tp.CONFIRMACAO = 0 THEN 'Negativa'
    WHEN tp.CONFIRMACAO = 1 THEN 'Positiva'
    WHEN tp.CONFIRMACAO IS NULL THEN 'Aguardando'
    WHEN tp.FK_ID_SOLICITACAO_CANCELAMENTO IS NOT NULL THEN 'Cancelamento'
    END AS 'CONFIRMAÇÃO',
    CASE 
    WHEN tp.VALOR_BRUTO = tp.VALOR_LIQUIDO THEN 0
    ELSE 1
    END AS 'COMISSÃO',
    PAL.NOME AS PALCO,
    tc.CONTROLADORIA_ESHOWS,
    #CASE WHEN tp.OCULTO_TABELA_ADMIN = 1 THEN 'Resolvido' END AS STATUS_MANUAL,
    TSC.STATUS AS 'STATUS ESTABALECIMENTO',
    CASE WHEN (SELECT WN.ID FROM T_WHATSAPP_NOTIFICACOES WN
    WHERE WN.FK_PROPOSTA = tp.ID
    AND WN.TIPO = 'DISPARO_CHECKIN') IS NOT NULL THEN 'Disparo Checkin Enviado'
    WHEN tp.CONTROLE = "Disparo Solicitado" THEN "Disparo Checkin Solicitado"
    ELSE tp.CONTROLE END AS 'CONTROLE DISPARO',
    CASE WHEN CGC.FK_PROPOSTA IS NOT NULL AND CGC.ENVIO = 1 THEN 'Mensagem para a casa enviada'
    ELSE NULL END AS COMUNICADO_CASA,
    CONCAT('https://admin.eshows.com.br/proposta/', tp.ID) AS 'VER DETALHES'
    
    FROM
    T_PROPOSTAS tp 
    INNER JOIN T_ATRACOES ta ON (tp.FK_CONTRATADO = ta.ID)
    INNER JOIN T_COMPANIES tc ON (tp.FK_CONTRANTE = tc.ID)
    INNER JOIN T_PROPOSTA_STATUS tps ON (tp.FK_STATUS_PROPOSTA = tps.ID)
    LEFT JOIN T_STATUS_COMPANIES TSC ON TSC.ID = tc.FK_STATUS_COMPANY
    LEFT JOIN T_PALCOS PAL ON PAL.ID = tp.FK_PALCOS
    LEFT JOIN T_COMUNICADO_GRUPO_CHECKIN CGC ON CGC.FK_PROPOSTA = tp.ID

    WHERE tp.FK_STATUS_PROPOSTA NOT IN (102, 103, 104)
    AND tp.DATA_INICIO > DATE_ADD(NOW(), INTERVAL -1 MINUTE)
    AND tp.DATA_INICIO < DATE_ADD(NOW(), INTERVAL 1 HOUR)
    AND tp.FK_CONTRANTE NOT IN (102, 633, 343, 632)
    #AND tp.OCULTO_TABELA_ADMIN = 0
    AND ta.ID NOT IN (12166)

    ORDER BY 'MINUTOS FALTANTES'
    """)

@st.cache_data
def show_to_cancel():
    return get_dataframe_from_query("""
SELECT
    P.ID AS 'ID PROPOSTA', 
    AU.FULL_NAME AS 'Nome Usuario',
    DATE_FORMAT(P.LAST_UPDATE, '%d/%m/%Y às %H:%i') as 'ÚLTIMA ATUALIZAÇÃO',

        CASE 
            WHEN S.DESCRICAO IS NULL THEN "Cancelada"
        ELSE S.DESCRICAO
    END AS 'STATUS DA PROPOSTA',
    
    DATE_FORMAT(P.DATA_INICIO, '%d/%m/%Y') AS 'DATA INÍCIO',
    DATE_FORMAT(P.DATA_INICIO, '%H:%i:%s') AS 'HORÁRIO INÍCIO',
    C.ID AS 'ID ESTABELECIMENTO',
    C.NAME AS 'ESTABELECIMENTO',
    A.NOME AS 'ARTISTA',
    F.DESCRICAO AS 'FORMAÇÃO',
    MC.TEXTO_MOTIVO AS MOTIVO,
    MCP.DESCRICAO_CANCELAMENTO AS 'DESCRIÇÃO DO CANCELAMENTO',
    TSC.STATUS AS 'STATUS ESTABALECIMENTO',
    CONCAT('https://admin.eshows.com.br/proposta/', P.ID) AS 'VER DETALHES'


    FROM T_PROPOSTAS P
    INNER JOIN ADMIN_USERS AU ON (AU.ID = P.LAST_USER)
    INNER JOIN T_COMPANIES C ON (P.FK_CONTRANTE = C.ID)
    INNER JOIN T_ATRACOES A ON (P.FK_CONTRATADO = A.ID)
    LEFT JOIN T_PROPOSTA_STATUS S ON (P.FK_STATUS_PROPOSTA = S.ID)
    INNER JOIN T_MOTIVO_CANCELAMENTO_PROPOSTA MCP ON MCP.FK_PROPOSTA = P.ID
    LEFT JOIN T_MOTIVO_CANCELAMENTO MC ON MC.ID = MCP.FK_ID_SOLICITACAO_CANCELAMENTO
    LEFT JOIN T_FORMACAO F ON F.ID = P.FK_FORMACAO
    LEFT JOIN T_STATUS_COMPANIES TSC ON TSC.ID = C.FK_STATUS_COMPANY

    WHERE
    P.FK_CONTRANTE NOT IN (102, 633, 343, 632)
    AND P.DATA_INICIO >= "2024-08-01 00:00:00"
    AND MCP.LAST_UPDATE > DATE_SUB(CURDATE(), INTERVAL 7 DAY)
    AND MCP.ADMIN = 0
    AND P.DATA_INICIO >= CURDATE()
    GROUP BY P.ID
    ORDER BY P.DATA_INICIO ASC;
    """)

@st.cache_data
def hole_map():
    return get_dataframe_from_query("""                       
SELECT
*
FROM (
(SELECT
P.ID AS ID,
A.NOME AS ARTISTA_ORIGINAL,
DATE_FORMAT(P.DATA_INICIO, '%d/%m') as DATA_INICIO,
TIME_FORMAT(P.DATA_INICIO, '%H:%i') as HORARIO,
C.NAME AS ESTABELECIMENTO,
KE.NOME AS KEY_ACCOUNT,
PA.NOME AS PALCO,
TF.DESCRICAO AS FORMACAO,
OP.ID as "ID_OPORTUNIDADE",
P.CONTA as OBSERVACAO,
CASE 
WHEN P.FK_STATUS_PROPOSTA = 102 THEN "RECUSA PROPOSTA"
WHEN MCP.FK_PROPOSTA IS NOT NULL THEN "CANCELAMENTO"
WHEN R.CONFIRMACAO = 0 THEN "CONFIRMACAO NEGATIVA"
WHEN SPP.FK_PROPOSTA IS NOT NULL THEN "PROPOSTA COM PROBLEMA"
END AS "PROBLEMA",
#IF(MR.MOTIVO IS NULL, "Não informado", MR.MOTIVO) as MOTIVO,
CASE 
WHEN P.FK_STATUS_PROPOSTA = 102 AND MRP.FK_MOTIVO_RECUSA IS NOT NULL THEN CONCAT(COALESCE(MR.MOTIVO,""), ": ", COALESCE(MRP.DESCRICAO_RECUSA,"(sem comentário)"))
WHEN MCP.FK_PROPOSTA IS NOT NULL THEN CONCAT(COALESCE(MC.TEXTO_MOTIVO,""), ": ", COALESCE(MCP.DESCRICAO_CANCELAMENTO,"sem comentário"))
WHEN R.CONFIRMACAO = 0 THEN "Não informado"
WHEN SPP.FK_PROPOSTA IS NOT NULL THEN CONCAT(COALESCE(SP.TITULO,""), ": ", COALESCE(SPP.SINAL_PROBLEMA_DESCRICAO,""))
ELSE "Não informado"
END AS MOTIVO,
IF((SELECT tp.ID FROM T_PROPOSTAS tp
LEFT JOIN T_RECONFIRMACAO R ON R.FK_PROPOSTA = tp.ID
LEFT JOIN T_MOTIVO_CANCELAMENTO_PROPOSTA MCP ON MCP.FK_PROPOSTA = tp.ID
LEFT JOIN T_SINAL_PROBLEMA_PROPOSTA SPP ON SPP.FK_PROPOSTA = tp.ID
WHERE tp.FK_STATUS_PROPOSTA IN (100,101,103,104)
AND P.DATA_INICIO = tp.DATA_INICIO
AND P.FK_CONTRANTE = tp.FK_CONTRANTE
AND MCP.FK_ID_SOLICITACAO_CANCELAMENTO IS NULL 
AND (R.CONFIRMACAO = 1 OR R.CONFIRMACAO IS NULL)
AND SPP.FK_PROPOSTA IS NULL
LIMIT 1) IS NULL, "BURACO", "OK") AS STATUS_FINAL,
"PROPOSTA" as ORIGEM,
TSC.STATUS AS STATUS_COMPANY,
CONCAT('https://abertura-oportunidade-proposta-com-problema-fabiopereira15.replit.app/proposta/', P.ID) AS 'LANÇAR PROPOSTA RELAMPAGO',
CONCAT('https://admin.eshows.com.br/proposta/', P.ID) AS VER_PROPOSTA_ORIGINAL,
P.LAST_UPDATE

FROM T_PROPOSTAS P
INNER JOIN T_ATRACOES A ON (A.ID = P.FK_CONTRATADO)
INNER JOIN T_COMPANIES C ON (C.ID = P.FK_CONTRANTE)
LEFT JOIN T_OPERADORES O ON (C.FK_OPERADOR = O.ID)
LEFT JOIN T_MOTIVO_RECUSA_PROPOSTA MRP ON MRP.FK_PROPOSTA = P.ID
LEFT JOIN T_MOTIVO_RECUSA MR ON MR.ID = MRP.FK_MOTIVO_RECUSA
LEFT JOIN T_KEYACCOUNT_ESTABELECIMENTO KE ON (KE.ID = C.FK_KEYACCOUNT)
LEFT JOIN T_OPORTUNIDADE_RELAMPAGO TOR ON (TOR.FK_PROPOSTA = P.ID)
LEFT JOIN T_OPORTUNIDADES OP ON (OP.FK_OPORTUNIDADE_RELAMPAGO = TOR.ID)
LEFT JOIN T_SINAL_PROBLEMA_PROPOSTA SPP ON SPP.FK_PROPOSTA = P.ID
LEFT JOIN T_SINAL_PROBLEMA SP ON SP.ID = SPP.FK_SINAL_PROBLEMA
LEFT JOIN T_MOTIVO_CANCELAMENTO_PROPOSTA MCP ON MCP.FK_PROPOSTA = P.ID
LEFT JOIN T_MOTIVO_CANCELAMENTO MC ON MC.ID = MCP.FK_ID_SOLICITACAO_CANCELAMENTO
LEFT JOIN T_FORMACAO TF ON TF.ID = P.FK_FORMACAO
LEFT JOIN T_PALCOS PA ON PA.ID = P.FK_PALCOS
LEFT JOIN T_STATUS_COMPANIES TSC ON TSC.ID = C.FK_STATUS_COMPANY
LEFT JOIN T_RECONFIRMACAO R ON R.FK_PROPOSTA = P.ID
WHERE (P.FK_STATUS_PROPOSTA = 102 OR MCP.FK_ID_SOLICITACAO_CANCELAMENTO IS NOT NULL OR R.CONFIRMACAO = 0 OR SPP.FK_PROPOSTA IS NOT NULL)
AND P.FK_CONTRANTE NOT IN (102,343,632,633)
AND P.LAST_UPDATE > "2023-07-07 00:00:00"
AND P.DATA_INICIO > "2023-07-10 00:00:00"
AND P.DATA_INICIO > SUBDATE(CURRENT_TIMESTAMP(), INTERVAL 6 HOUR)
AND P.DATA_INICIO < ADDDATE(CURRENT_TIMESTAMP(), INTERVAL 25 DAY)
-- AND P.OCULTO_TABELA_ADMIN = 0
GROUP BY P.ID
HAVING STATUS_FINAL = "BURACO"
ORDER BY P.ID DESC)

UNION ALL

(SELECT
TSP.ID as T_ID,
IF(A.NOME IS NULL, "BURACO", A.NOME) as ARTISTA,
DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL (DAYOFWEEK(CURDATE()) + 7 - TSP.DIA_DA_SEMANA) % 7 DAY), '%d/%m') as DATA_INICIO,
DATE_FORMAT(TSP.HORARIO_INICIO, '%H:%i') as HORARIO,
C.NAME as ESTABALECIMENTO,
KE.NOME as KEY_ACCOUNT,
PA.NOME as PALCO,
TF.DESCRICAO AS FORMACAO,
TOP.ID,
TSP.OBSERVACAO,
"SHOW PADRÃO" as PROBLEMA,
"Show Padrão" as MOTIVO,
"BURACO" as Status_final,
"SHOW_PADRAO" as ORIGEM,
TSC.STATUS AS STATUS_COMPANY,
CONCAT('https://abertura-oportunidade-proposta-com-problema-fabiopereira15.replit.app/proposta/', TSP.ID) AS LINK,
CONCAT("https://admin.eshows.com.br/show-padrao/edit/", TSP.ID) as LINK,
TSP.LAST_UPDATE

FROM T_SHOWS_PADRAO TSP
LEFT JOIN T_COMPANIES C ON (C.ID = TSP.FK_COMPANIES)
LEFT JOIN T_KEYACCOUNT_ESTABELECIMENTO KE ON (KE.ID = C.FK_KEYACCOUNT)
LEFT JOIN T_OPERADORES O ON (O.ID = C.FK_OPERADOR)
LEFT JOIN T_PROPOSTAS P ON (WEEKDAY(P.DATA_INICIO) = SUBSTRING(TSP.DIA_DA_SEMANA, 3,1) 
AND ((P.FK_PALCOS = TSP.FK_PALCOS) OR (P.FK_CONTRANTE = TSP.FK_COMPANIES))
AND (DATE_FORMAT(P.DATA_INICIO, '%H:%i')) = DATE_FORMAT(TSP.HORARIO_INICIO, '%H:%i')
AND P.FK_STATUS_PROPOSTA IN (100,101,103,104,105)
AND DATE_FORMAT(P.DATA_INICIO, "%Y-%m-%d") BETWEEN CURDATE() AND ADDDATE(CURDATE(), INTERVAL 6 DAY)
AND P.FK_CONTRANTE NOT IN (102, 633, 343, 632))
LEFT JOIN T_ATRACOES A ON (A.ID = P.FK_CONTRATADO)
LEFT JOIN T_OPORTUNIDADES TOP ON (TOP.FK_SHOW_PADRAO = TSP.ID AND DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL (DAYOFWEEK(CURDATE()) + 7 - TSP.DIA_DA_SEMANA) % 7 DAY), '%d/%m') = DATE_FORMAT(TOP.DATA_INICIO, '%d/%m'))
LEFT JOIN T_FORMACAO TF ON TF.ID = TSP.FORMACAO
LEFT JOIN T_PALCOS PA ON PA.ID = TSP.FK_PALCOS
LEFT JOIN T_STATUS_COMPANIES TSC ON TSC.ID = C.FK_STATUS_COMPANY
WHERE TSP.STATUS = 1
AND (P.ID IS NULL OR (DATE_FORMAT(P.DATA_INICIO, '%H:%i') != DATE_FORMAT(TSP.HORARIO_INICIO, '%H:%i')))
AND C.CONTROLADORIA_ESHOWS = 1
AND C.ACTIVE = 1
AND TSP.FK_COMPANIES NOT IN (102, 633, 343, 632)
ORDER BY DATA_INICIO, DATE_FORMAT(TSP.HORARIO_INICIO, '%H:%i'))) AS TABELA

GROUP BY ESTABELECIMENTO, HORARIO, DATA_INICIO
ORDER BY DATA_INICIO, HORARIO
    """)

@st.cache_data
def proposal_map():
    return get_dataframe_from_query("""
    SELECT
    O.ID AS 'ID OPORTUNIDADE',
    DATE_FORMAT(O.CREATED_AT, '%d/%m/%Y às %H:%i') AS 'DATA CRIAÇÃO',
    TIMESTAMPDIFF(DAY, O.CREATED_AT, NOW()) AS "CRIADO HÁ",
    C.NAME AS ESTABELECIMENTO,
    DATE_FORMAT(O.DATA_INICIO, '%d/%m/%Y') as 'DATA INÍCIO',
    DATE_FORMAT(O.DATA_INICIO, '%H:%i') AS 'HORÁRIO DE INÍCIO',
    CASE WHEN O.FINALIZADA = 1 THEN 'Cancelada'
    ELSE SO.DESCRICAO 
    END AS STATUS,
    AU.FULL_NAME as "Responsável Abertura",
    KE.NOME AS "KEYACCOUNT",
    F.DESCRICAO AS 'FORMAÇAO',
    EM.DESCRICAO AS 'ESTILO 1',
    EM2.DESCRICAO AS 'ESTILO 2',
    EM3.DESCRICAO AS 'ESTILO 3',
    (SELECT COUNT(DISTINCT CAN.FK_ATRACAO) FROM T_CANDIDATOS CAN
    WHERE CAN.FK_OPORTUNIDADE = O.ID
    AND CAN.FK_STATUS_CANDIDATO IN (100,101)) AS 'QUANTIDADE DE CANDIDATOS',
    (SELECT COUNT(DISTINCT FAV.FK_ATRACAO) FROM T_FAVORITO FAV
    WHERE FAV.FK_ATRACAO = CAN.FK_ATRACAO
    AND O.FK_CONTRATANTE = FAV.FK_CONTRATANTE
    AND FAV.FAVORITE = 1 AND FAV.BLOCKED = 0) AS 'CANDIDATOS FAVORITOS',
    (SELECT COUNT(DISTINCT FAV.FK_ATRACAO) FROM T_FAVORITO FAV
    WHERE FAV.FK_ATRACAO = CAN.FK_ATRACAO
    AND O.FK_CONTRATANTE = FAV.FK_CONTRATANTE
    AND FAV.APROVADO = 1 AND FAV.BLOCKED = 0 AND FAV.FAVORITE = 0) AS 'CANDIDATOS APROVADOS',
    CASE WHEN O.FK_OPORTUNIDADE_RELAMPAGO IS NOT NULL THEN 'sim'
    ELSE 'nao' END AS 'ORIGEM RELÂMPAGO',
    CASE WHEN O.FK_SHOW_PADRAO IS NOT NULL THEN 'sim'
    ELSE 'nao' END AS 'ORIGEM PADRÃO',
    TSC.STATUS AS 'STATUS ESTABELECIMENTO',
    P.ID AS 'ID PROPOSTA',
    A.ID AS 'ID ARTISTA',
    A.NOME AS ARTISTA,
    PS.DESCRICAO AS STATUS_PROPOSTA,
    -- (SELECT ZC.LAST_UPDATE FROM ZLOG_T_CANDIDATOS ZC
    --  INNER JOIN T_CANDIDATOS CAND ON CAND.ID = ZC.ID
    --  WHERE ZC.FK_STATUS_CANDIDATO = 100
    --  AND CAND.FK_OPORTUNIDADE = O.ID
    --  LIMIT 1) AS DATA_ESCOLHA_CANDIDATO,
    DATE_FORMAT(P.CREATED_AT, '%d/%m/%Y às %H:%i') AS 'DATA ESCOLHA CANDIDATO',
    CONCAT('https://admin.eshows.com.br/oportunidades/candidatos/', O.ID) AS 'VER CANDIDATOS',
    CONCAT('https://disparo-oportunidade-fabiopereira15.replit.app/disparar/', O.ID) AS 'DISPARAR WPP'

    FROM T_OPORTUNIDADES O
    INNER JOIN T_COMPANIES C ON C.ID = O.FK_CONTRATANTE
    INNER JOIN T_STATUS_OPORTUNIDADE SO ON SO.ID = O.FK_STATUS_OPORTUNIDADE
    INNER JOIN T_FORMACAO F ON F.ID = O.FK_FORMACAO
    LEFT JOIN T_ESTILOS_MUSICAIS EM ON EM.ID = O.FK_ESTILO_INTERESSE_1
    LEFT JOIN T_ESTILOS_MUSICAIS EM2 ON EM2.ID = O.FK_ESTILO_INTERESSE_2
    LEFT JOIN T_ESTILOS_MUSICAIS EM3 ON EM3.ID = O.FK_ESTILO_INTERESSE_3
    LEFT JOIN T_PROPOSTAS P ON P.FK_OPORTUNIDADE = O.ID
    LEFT JOIN T_ATRACOES A ON A.ID = P.FK_CONTRATADO
    LEFT JOIN T_PROPOSTA_STATUS PS ON PS.ID = P.FK_STATUS_PROPOSTA
    LEFT JOIN ADMIN_USERS AU ON (AU.ID = O.CREATED_BY)
    LEFT JOIN T_KEYACCOUNT_ESTABELECIMENTO KE ON KE.ID = C.FK_KEYACCOUNT
    LEFT JOIN T_CANDIDATOS CAN ON CAN.FK_OPORTUNIDADE = O.ID
    LEFT JOIN T_STATUS_COMPANIES TSC ON TSC.ID = C.FK_STATUS_COMPANY

    WHERE
    O.DATA_INICIO > CURDATE()
    AND O.DATA_INICIO < DATE_ADD(CURDATE(), INTERVAL 45 DAY)
    AND (O.FINALIZADA = 0 OR O.FINALIZADA IS NULL)
    AND C.ID NOT IN (102,343,632,633)
    AND SO.DESCRICAO  != "Encerrada"

    GROUP BY O.ID
    ORDER BY O.DATA_INICIO ASC;
    """)

# @st.cache_data
# def artist_favorite_blocked():
#     return get_dataframe_from_query ("""
#     SELECT
#     TF.ID AS 'ID',
#     TA.FK_USUARIO AS 'ID USUARIO',
#     TF.FK_ATRACAO AS 'ID ATRAÇÃO',
#     AU.FULL_NAME AS 'NOME USUARIO',
#     TA.NOME AS 'NOME ARTISTA',
#     TC.NAME AS CONTRATANTE,
#     TF.FAVORITE AS FAVORITO,
#     TF.APROVADO AS APROVADO,
#     TF.BLOCKED AS BLOQUEADO,
#     TF.RECOMENDACAO_MANUAL AS 'RECOMENDAÇÃO MANUAL',
#     TF.REFUSED AS RECUSADO,
#     CONCAT ('https://perfil.eshows.com.br/', TA.slug) AS 'PERFIL ARTISTA'
#     FROM T_FAVORITO TF
#     INNER JOIN T_ATRACOES TA ON TF.FK_ATRACAO = TA.ID
#     INNER JOIN ADMIN_USERS AU ON TA.FK_USUARIO = AU.ID
#     INNER JOIN T_COMPANIES TC ON TC.ID = TF.FK_CONTRATANTE
#     WHERE TC.NAME NOT LIKE '%TESTE%'
#     """)

@st.cache_data
def holes_with_proposals():
    return get_dataframe_from_query("""
SELECT DISTINCT
O.ID AS 'ID OPORTUNIDADE',
P.ID AS 'ID PROPOSTA',
A.NOME AS 'NOME ARTISTA',
C.NAME AS 'ESTABELECIMENTO',
DATE_FORMAT(P.DATA_INICIO, '%d/%m/%Y') AS 'DATA INÍCIO',
TIME_FORMAT(P.DATA_INICIO, '%H:%i') AS 'HORÁRIO',
KE.NOME AS KEY_ACCOUNT,
TSC.STATUS AS 'STATUS ESTABELECIMENTO',
CONCAT("https://admin.eshows.com.br/oportunidades/candidatos/", O.ID) as 'LINK DA OPORTUNIDADE',
CONCAT('https://admin.eshows.com.br/proposta/', P.ID) AS 'VER PROPOSTA ORIGINAL'

FROM T_OPORTUNIDADES O
INNER JOIN T_PROPOSTAS P ON O.FK_CONTRATANTE = P.FK_CONTRANTE AND O.DATA_INICIO = P.DATA_INICIO
INNER JOIN T_ATRACOES A ON (A.ID = P.FK_CONTRATADO)
INNER JOIN T_COMPANIES C ON (C.ID = P.FK_CONTRANTE)
INNER JOIN T_KEYACCOUNT_ESTABELECIMENTO KE ON (KE.ID = C.FK_KEYACCOUNT)
INNER JOIN T_STATUS_COMPANIES TSC ON TSC.ID = C.FK_STATUS_COMPANY
INNER JOIN T_SHOWS_PADRAO TSP ON (O.FK_SHOW_PADRAO = TSP.ID)

WHERE P.DATA_INICIO IS NOT NULL
AND P.FK_STATUS_PROPOSTA NOT IN (102)
AND O.FK_PROPOSTA IS NULL
AND O.DATA_INICIO >= CURDATE()
AND P.DATA_INICIO >= CURDATE()
""")

@st.cache_data
def default_show_to_do():
    return get_dataframe_from_query("""
SELECT
    -- Dados do Show Padrão
    TSP.ID AS "ID Show Padrão",
    PAL_SHOW.NOME AS 'PALCO SHOW PADRÃO',
    TC.NAME AS "Estabelecimento Show Padrão",
    
    TDDS.DIA_DA_SEMANA AS "Dia da Semana Show Padrão",
    DATE_FORMAT(TSP.HORARIO_INICIO, '%H:%i') AS "Hora Inicio Show Padrão",
    DATE_FORMAT(TSP.HORARIO_FIM, '%H:%i') AS "Hora Fim Show Padrão",
    
    -- Dados da Proposta
    P.ID AS "ID Proposta",
    PAL_PROP.NOME AS 'PALCO PROPOSTA',
    DATE_FORMAT(P.DATA_INICIO, '%d/%m/%Y') AS "Data Inicio Proposta",
    CASE DAYOFWEEK(P.DATA_INICIO)
        WHEN 1 THEN 'Domingo'
        WHEN 2 THEN 'Segunda-Feira'
        WHEN 3 THEN 'Terça-Feira'
        WHEN 4 THEN 'Quarta-Feira'
        WHEN 5 THEN 'Quinta-Feira'
        WHEN 6 THEN 'Sexta-Feira'
        WHEN 7 THEN 'Sábado'
    END AS "Dia da Semana Proposta",
    DATE_FORMAT(P.DATA_INICIO, '%H:%i') AS "Hora Inicio Proposta",
    DATE_FORMAT(P.DATA_FIM, '%H:%i') AS "Hora Fim Proposta",
    
    -- Informações adicionais
    TKE.NOME AS "KeyAccount",
    TA.NOME AS "Nome Artista"
    
FROM T_SHOWS_PADRAO TSP
INNER JOIN T_DIAS_DA_SEMANA TDDS ON TSP.DIA_DA_SEMANA = TDDS.ID
INNER JOIN T_COMPANIES TC ON TSP.FK_COMPANIES = TC.ID
LEFT JOIN T_PALCOS PAL_SHOW ON TSP.FK_PALCOS = PAL_SHOW.ID
LEFT JOIN T_PROPOSTAS P ON P.FK_CONTRANTE = TSP.FK_COMPANIES
    AND (
    CASE DAYOFWEEK(P.DATA_INICIO)
        WHEN 1 THEN '106'
        WHEN 2 THEN '100'
        WHEN 3 THEN '101'
        WHEN 4 THEN '102'
        WHEN 5 THEN '103'
        WHEN 6 THEN '104'
        WHEN 7 THEN '105'
    END
) = TSP.DIA_DA_SEMANA
    AND TIME(P.DATA_INICIO) BETWEEN TIME(TSP.HORARIO_INICIO) AND TIME(TSP.HORARIO_FIM)
    AND TIME(P.DATA_FIM) BETWEEN TIME(TSP.HORARIO_INICIO) AND TIME(TSP.HORARIO_FIM)
LEFT JOIN T_PALCOS PAL_PROP ON P.FK_PALCOS = PAL_PROP.ID
LEFT JOIN T_KEYACCOUNT_ESTABELECIMENTO TKE ON TC.FK_KEYACCOUNT = TKE.ID
LEFT JOIN T_ATRACOES TA ON TA.ID = P.FK_CONTRATADO

WHERE DATE(P.DATA_INICIO) >= CURDATE()
AND P.FK_STATUS_PROPOSTA IS NOT NULL
AND P.FK_STATUS_PROPOSTA != '102'
AND TSP.STATUS = 1
AND PAL_SHOW.ID = PAL_PROP.ID
AND TSP.ID IN (
    SELECT TSP.ID
    FROM T_SHOWS_PADRAO TSP
    INNER JOIN T_PROPOSTAS P ON P.FK_CONTRANTE = TSP.FK_COMPANIES
        AND (
        CASE DAYOFWEEK(P.DATA_INICIO)
            WHEN 1 THEN '106'
            WHEN 2 THEN '100'
            WHEN 3 THEN '101'
            WHEN 4 THEN '102'
            WHEN 5 THEN '103'
            WHEN 6 THEN '104'
            WHEN 7 THEN '105'
        END
    ) = TSP.DIA_DA_SEMANA
    AND TIME(P.DATA_INICIO) BETWEEN TIME(TSP.HORARIO_INICIO) AND TIME(TSP.HORARIO_FIM)
    AND TIME(P.DATA_FIM) BETWEEN TIME(TSP.HORARIO_INICIO) AND TIME(TSP.HORARIO_FIM)
    WHERE DATE(P.DATA_INICIO) >= CURDATE()
    AND P.FK_STATUS_PROPOSTA IS NOT NULL
    AND P.FK_STATUS_PROPOSTA != '102'
    GROUP BY TSP.ID, DATE(P.DATA_INICIO)
    HAVING COUNT(DISTINCT P.ID) > 1
)
ORDER BY
    TC.NAME ASC,
    TSP.ID ASC
""")

@st.cache_data
def churn_companies(day):
    return get_dataframe_from_query(f""" 
WITH ShowsHoje AS (
    SELECT 
        C.ID AS company_id
    FROM 
        T_PROPOSTAS P
    INNER JOIN T_COMPANIES C ON P.FK_CONTRANTE = C.ID
    WHERE                           
       DATE(P.DATA_INICIO) = '{day}'
)

-- Consulta principal para obter as empresas com shows na semana passada
SELECT
    C.NAME,
    DATE_FORMAT(P.DATA_INICIO, '%d/%m/%Y') AS 'DATA SHOW',
    CASE DAYOFWEEK(P.DATA_INICIO)
        WHEN 1 THEN 'Domingo'
        WHEN 2 THEN 'Segunda-Feira'
        WHEN 3 THEN 'Terça-Feira'
        WHEN 4 THEN 'Quarta-Feira'
        WHEN 5 THEN 'Quinta-Feira'
        WHEN 6 THEN 'Sexta-Feira'
        WHEN 7 THEN 'Sábado'
    END AS "Dia da Semana Proposta"
FROM 
    T_PROPOSTAS P
INNER JOIN T_COMPANIES C ON P.FK_CONTRANTE = C.ID
LEFT JOIN ShowsHoje SH ON C.ID = SH.company_id
INNER JOIN T_ATRACOES A ON P.FK_CONTRATADO = A.ID
WHERE 
    DATE(P.DATA_INICIO) = '{day}' - INTERVAL 7 DAY
    AND SH.company_id IS NULL
    AND A.ID NOT IN ('12166')
ORDER BY 
    P.DATA_INICIO;
""")

@st.cache_data
def new_companies(day):
    return get_dataframe_from_query(f"""
WITH ShowsSemanaPassada AS (
    SELECT 
        C.ID AS company_id
    FROM 
        T_PROPOSTAS P
    INNER JOIN T_COMPANIES C ON P.FK_CONTRANTE = C.ID
    WHERE                           
        DATE(P.DATA_INICIO) = '{day}' - INTERVAL 7 DAY
)

-- Consulta principal para obter as empresas com shows no dia dessa semana mas não na semana passada
SELECT
    C.NAME,
    DATE_FORMAT(P.DATA_INICIO, '%d/%m/%Y') AS 'DATA SHOW',
    CASE DAYOFWEEK(P.DATA_INICIO)
        WHEN 1 THEN 'Domingo'
        WHEN 2 THEN 'Segunda-Feira'
        WHEN 3 THEN 'Terça-Feira'
        WHEN 4 THEN 'Quarta-Feira'
        WHEN 5 THEN 'Quinta-Feira'
        WHEN 6 THEN 'Sexta-Feira'
        WHEN 7 THEN 'Sábado'
    END AS "Dia da Semana Proposta"
FROM 
    T_PROPOSTAS P
INNER JOIN T_COMPANIES C ON P.FK_CONTRANTE = C.ID
LEFT JOIN ShowsSemanaPassada SP ON C.ID = SP.company_id
INNER JOIN T_ATRACOES A ON P.FK_CONTRATADO = A.ID
WHERE 
    DATE(P.DATA_INICIO) = '{day}'
    AND SP.company_id IS NULL
    AND A.ID NOT IN ('12166')
ORDER BY 
    P.DATA_INICIO;
""")

@st.cache_data
def houses_implementation_stabilization():
    return get_dataframe_from_query ("""
SELECT 
    DATE_FORMAT(C.CREATED_AT, '%d/%m/%Y') AS 'CREATED AT',
    C.ID AS 'ID',
    C.NAME AS 'NOME ESTABELECIMENTO',
    C.CNPJ,
    C.CITY AS 'CIDADE',
    DATE_FORMAT(C.INICIO_DA_OPERACAO, '%d/%m/%Y') AS 'INICIO DA OPERAÇÃO',
    C.FK_STATUS_COMPANY AS 'ID STATUS',
    SC.STATUS
    
FROM T_COMPANIES C
INNER JOIN T_STATUS_COMPANIES SC ON SC.ID = C.FK_STATUS_COMPANY
WHERE SC.STATUS IN ("Implantação", "Estabilização")
AND C.ACTIVE = 1
AND C.CONTROLADORIA_ESHOWS = 1
ORDER BY C.INICIO_DA_OPERACAO;
""")

@st.cache_data
def new_implementation():
    return get_dataframe_from_query ("""
WITH STATUS_100 AS (
    SELECT
        ZC.NAME,
        MIN(ZC.LOG_DATE) AS LOG_100
    FROM ZLOG_T_COMPANIES ZC
    WHERE ZC.FK_STATUS_COMPANY = '100'
    GROUP BY ZC.NAME
),

STATUS_102 AS (
    SELECT
        ZC.NAME,
        MIN(ZC.LOG_DATE) AS LOG_102
    FROM ZLOG_T_COMPANIES ZC
    WHERE ZC.FK_STATUS_COMPANY = '102'
    GROUP BY ZC.NAME
)

SELECT 
    DATE_FORMAT(C.CREATED_AT, '%d/%m/%Y') AS 'DATA CREATED AT',
    TIME_FORMAT(C.CREATED_AT, '%H:%i') AS 'HORÁRIO CREATED AT',
    SC.STATUS,
    C.ID AS 'CONTRATANTE ID',
    C.NAME AS CONTRATANTE,
    -- Adicionando a vírgula antes do CASE
    CASE 
        WHEN GC.GRUPO_CLIENTES IS NULL THEN 'OUTROS'
        ELSE GC.GRUPO_CLIENTES
    END AS GRUPO,
    C.CONTROLADORIA_ESHOWS,
    KA.NOME AS KEY_ACCOUNT,
    C.CITY AS CIDADE,
    DATE_FORMAT(C.INICIO_DA_OPERACAO, '%d/%m/%Y') AS 'INÍCIO DA OPERAÇÃO',
    
    -- Cálculo de inauguração
    CASE
    		WHEN C.INICIO_DA_OPERACAO IS NOT NULL THEN
        		CASE
                  WHEN DATEDIFF(C.INICIO_DA_OPERACAO, CURDATE()) < 0 THEN 'EM ATRASO'
                	ELSE CONCAT(DATEDIFF(C.INICIO_DA_OPERACAO, CURDATE()), ' dias')
        		END
        ELSE
        		'OPERAÇÃO NÃO INICIADA'
    END AS 'INAUGURAÇÃO',
    
    -- Cálculo do tempo de implantação
    CASE
        WHEN S100.LOG_100 IS NOT NULL THEN
            CONCAT(TIMESTAMPDIFF(HOUR, S100.LOG_100, NOW()), ' horas')
        ELSE
            'NÃO ESTA EM IMPLANTAÇÃO'
    END AS 'TEMPO EM IMPLANTAÇÃO',
    
    -- Cálculo do tempo de estabilização
    CASE
        WHEN S102.LOG_102 IS NOT NULL THEN
            CONCAT(TIMESTAMPDIFF(HOUR, S102.LOG_102, NOW()), ' horas')
        ELSE
            'AINDA NÃO ESTÁ ESTABILIZADO'
    END AS 'TEMPO EM ESTABILIZAÇÃO'
    
    
        
FROM T_COMPANIES C
INNER JOIN T_STATUS_COMPANIES SC ON SC.ID = C.FK_STATUS_COMPANY
LEFT JOIN T_GRUPOS_DE_CLIENTES GC ON GC.ID = C.FK_GRUPO
LEFT JOIN T_KEYACCOUNT_ESTABELECIMENTO KA ON KA.ID = C.FK_KEYACCOUNT
LEFT JOIN STATUS_100 S100 ON C.NAME = S100.NAME
LEFT JOIN STATUS_102 S102 ON C.NAME = S102.NAME
WHERE C.FK_STATUS_COMPANY IN (100, 102) -- Status Implantação ou Estabilização
AND C.ACTIVE = 1
ORDER BY C.INICIO_DA_OPERACAO;
""")

@st.cache_data
def implementation_first_proposal():
    return get_dataframe_from_query("""
WITH PRIMEIRA_PROPOSTA AS (
    SELECT
        P.FK_CONTRANTE AS COMPANY_ID,
        MIN(P.DATA_INICIO) AS PRIMEIRO_SHOW
    FROM T_PROPOSTAS P
    GROUP BY P.FK_CONTRANTE
),

PROPOSTAS_CANCELADAS AS (
    SELECT 
        P.ID AS PROPOSTA_ID
    FROM T_PROPOSTAS P
    LEFT JOIN T_PROPOSTA_STATUS PS ON PS.ID = P.FK_STATUS_PROPOSTA
    WHERE P.ID IS NOT NULL AND PS.DESCRICAO IS NULL
    GROUP BY P.ID
)

SELECT 
    SC.STATUS,
    CASE 
        WHEN GC.GRUPO_CLIENTES IS NULL THEN 'OUTROS'
        ELSE GC.GRUPO_CLIENTES
    END AS GRUPO,
    C.NAME AS CONTRATANTE,
    
    CASE
        WHEN KA.NOME IS NULL THEN '----------------'
        ELSE KA.NOME
    END AS KEY_ACCOUNT,
    
    CASE
        WHEN P.ID IS NULL THEN '----------------'
        WHEN PC.PROPOSTA_ID IS NOT NULL THEN '----------------' -- Quando é uma proposta cancelada
        ELSE P.ID
    END AS 'ID PROPOSTA',
    
    CASE
        WHEN P.ID IS NULL THEN '----------------'
        WHEN PC.PROPOSTA_ID IS NOT NULL THEN '----------------' -- Quando é uma proposta cancelada
        ELSE PS.DESCRICAO
    END AS 'STATUS DA PROPOSTA',
    
    CASE
        WHEN P.ID IS NULL THEN '----------------'
        WHEN PC.PROPOSTA_ID IS NOT NULL THEN '----------------' -- Quando é uma proposta cancelada
        ELSE CONCAT(DATE_FORMAT(P.DATA_INICIO, '%d/%m/%Y '), 'ás', DATE_FORMAT(P.DATA_INICIO, ' %H:%i'))
    END AS 'DATA INÍCIO'
        
FROM T_COMPANIES C
INNER JOIN T_STATUS_COMPANIES SC ON SC.ID = C.FK_STATUS_COMPANY
LEFT JOIN PRIMEIRA_PROPOSTA PR ON C.ID = PR.COMPANY_ID
LEFT JOIN T_PROPOSTAS P ON C.ID = P.FK_CONTRANTE AND P.DATA_INICIO = PR.PRIMEIRO_SHOW
LEFT JOIN PROPOSTAS_CANCELADAS PC ON P.ID = PC.PROPOSTA_ID
LEFT JOIN T_PROPOSTA_STATUS PS ON PS.ID = P.FK_STATUS_PROPOSTA
LEFT JOIN T_GRUPOS_DE_CLIENTES GC ON GC.ID = C.FK_GRUPO
LEFT JOIN T_KEYACCOUNT_ESTABELECIMENTO KA ON KA.ID = C.FK_KEYACCOUNT
WHERE C.FK_STATUS_COMPANY IN (100, 102) -- Status Implantação ou Estabilização
AND C.ACTIVE = 1
ORDER BY C.INICIO_DA_OPERACAO;
""")