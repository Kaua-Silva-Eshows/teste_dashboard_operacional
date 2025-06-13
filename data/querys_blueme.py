from data.dbconnect import get_dataframe_from_query
import streamlit as st

@st.cache_data
def companies(day,day2):
  return get_dataframe_from_query(f'''
    SELECT DISTINCT 
    E.ID as 'ID_Casa',
    E.NOME_FANTASIA as 'Casa'
    FROM T_DESPESA_RAPIDA DR 
    LEFT JOIN T_EMPRESAS E ON (DR.FK_LOJA = E.ID)
    WHERE E.FK_GRUPO_EMPRESA = 100
    AND STR_TO_DATE(DR.COMPETENCIA, '%Y-%m-%d') >= '{day}'
    AND STR_TO_DATE(DR.COMPETENCIA, '%Y-%m-%d') <= '{day2}'
    AND E.ID NOT IN (127,165,166,167,117,101,162,129,161,142,143,130,111,131)
    ORDER BY E.NOME_FANTASIA 
  ''', use_fabrica=True)

@st.cache_data
def inputs_expenses(day,day2):
  return get_dataframe_from_query(f'''
    SELECT 
    DRI.ID AS 'ID_zAssociac Despesa Item',
    E.ID AS 'ID Casa',
    E.NOME_FANTASIA AS 'Casa',
    DR.ID AS 'ID Despesa',
    F.ID AS 'ID Fornecedor',
    LEFT(F.FANTASY_NAME, 23) AS 'Fornecedor',
    STR_TO_DATE(DR.COMPETENCIA, '%Y-%m-%d') AS 'Data Competencia',
    I5.ID AS 'ID Insumo',
    I5.DESCRICAO AS 'Insumo',
    I4.ID AS 'ID Nivel 4',
    I4.DESCRICAO AS 'Nivel 4',
    I3.ID AS 'ID Nivel 3',
    I3.DESCRICAO AS 'Nivel 3',
    I2.ID AS 'ID Nivel 2',
    I2.DESCRICAO AS 'Nivel 2',
    I1.ID AS 'ID Nivel 1',
    I1.DESCRICAO AS 'Nivel 1',
    ROUND(CAST(DRI.QUANTIDADE AS FLOAT), 3) AS 'Quantidade Insumo',
    tudm.UNIDADE_MEDIDA_NAME AS 'Unidade Medida',
    ROUND(CAST(DRI.VALOR AS FLOAT), 2) AS 'Valor Insumo'
    FROM T_DESPESA_RAPIDA_ITEM DRI 
    INNER JOIN T_INSUMOS_NIVEL_5 I5 ON (DRI.FK_INSUMO = I5.ID)
    INNER JOIN T_INSUMOS_NIVEL_4 I4 ON (I5.FK_INSUMOS_NIVEL_4 = I4.ID)
    INNER JOIN T_INSUMOS_NIVEL_3 I3 ON (I4.FK_INSUMOS_NIVEL_3 = I3.ID)
    INNER JOIN T_INSUMOS_NIVEL_2 I2 ON (I3.FK_INSUMOS_NIVEL_2 = I2.ID)
    INNER JOIN T_INSUMOS_NIVEL_1 I1 ON (I2.FK_INSUMOS_NIVEL_1 = I1.ID)
    INNER JOIN ADMIN_USERS au ON (DRI.LAST_USER = au.ID)
    INNER JOIN T_DESPESA_RAPIDA DR ON (DRI.FK_DESPESA_RAPIDA = DR.ID)
    INNER JOIN T_EMPRESAS E ON (DR.FK_LOJA = E.ID)
    INNER JOIN T_FORNECEDOR F ON (DR.FK_FORNECEDOR = F.ID)
    LEFT JOIN T_UNIDADES_DE_MEDIDAS tudm ON (I5.FK_UNIDADE_MEDIDA = tudm.ID)
    WHERE STR_TO_DATE(DR.COMPETENCIA, '%Y-%m-%d') >= '{day}'
    AND STR_TO_DATE(DR.COMPETENCIA, '%Y-%m-%d') <= '{day2}'
    AND I1.ID IN (100,101)
    AND E.FK_GRUPO_EMPRESA = 100
    ORDER BY DR.ID
  ''', use_fabrica=True)

@st.cache_data
def purchases_without_orders(day,day2):
  return get_dataframe_from_query(f'''
   WITH Ultimo_Status AS (
    SELECT
        FK_DESPESA_RAPIDA,
        MAX(ID) AS Ultimo_Status_ID
    FROM T_DESPESA_STATUS
    GROUP BY FK_DESPESA_RAPIDA
)
    SELECT
    DISTINCT DR.ID AS 'tdr_ID',
    E.NOME_FANTASIA AS 'Casa',
    LEFT(F.FANTASY_NAME, 23) AS 'Fornecedor',
    DR.NF AS 'Doc Serie',
    DATE_FORMAT(DR.COMPETENCIA, '%d/%m/%Y') AS 'Data Competencia',
    DATE_FORMAT(DR.VENCIMENTO, '%d/%m/%Y') AS 'Data Vencimento',
    CCG1.DESCRICAO AS 'Class Cont Grupo 1',
    CCG2.DESCRICAO AS 'Class Cont Grupo 2',
    DR.OBSERVACAO AS 'Observação',
    DR.VALOR_PAGAMENTO AS 'Valor Original',
    DR.VALOR_LIQUIDO AS 'Valor Liquido',
    CASE
	WHEN SP2.DESCRICAO = 'Provisionado' THEN 'Provisionado'
	     ELSE 'Real'
    END AS 'Status Provisão Real',
    SP.DESCRICAO AS 'Status Pagamento',
    DATE_FORMAT(STR_TO_DATE(DR.COMPETENCIA, '%Y-%m-%d'), '%m/%Y') AS 'Mes Texto'
    FROM T_DESPESA_RAPIDA DR
    INNER JOIN T_EMPRESAS E ON (DR.FK_LOJA = E.ID)
    LEFT JOIN T_FORNECEDOR F ON (DR.FK_FORNECEDOR = F.ID)
    LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_1 CCG1 ON (DR.FK_CLASSIFICACAO_CONTABIL_GRUPO_1 = CCG1.ID)
    LEFT JOIN T_CLASSIFICACAO_CONTABIL_GRUPO_2 CCG2 ON (DR.FK_CLASSIFICACAO_CONTABIL_GRUPO_2 = CCG2.ID)
    LEFT JOIN T_STATUS_PAGAMENTO SP ON (DR.FK_STATUS_PGTO = SP.ID)
    LEFT JOIN T_DESPESA_RAPIDA_ITEM tdri ON (DR.ID = tdri.FK_DESPESA_RAPIDA)
    LEFT JOIN Ultimo_Status US ON (DR.ID = US.FK_DESPESA_RAPIDA)
    LEFT JOIN T_DESPESA_STATUS DS ON (DR.ID = DS.FK_DESPESA_RAPIDA AND DS.ID = US.Ultimo_Status_ID)
    LEFT JOIN T_STATUS S ON (DS.FK_STATUS_NAME = S.ID)
    LEFT JOIN T_STATUS_PAGAMENTO SP2 ON (S.FK_STATUS_PAGAMENTO = SP2.ID)
    WHERE tdri.ID IS NULL
    AND DATE(DR.COMPETENCIA) >= '{day}'
    AND DATE(DR.COMPETENCIA) <= '{day2}'
    AND DR.FK_CLASSIFICACAO_CONTABIL_GRUPO_1 = 236
    AND E.FK_GRUPO_EMPRESA = 100
    ORDER BY DR.ID ASC
  ''', use_fabrica=True)  

@st.cache_data
def blueme_with_order(day,day2):
  return get_dataframe_from_query(f'''
    SELECT
        BP.tdr_ID AS 'ID Despesa',
        BP.ID_Loja AS 'ID Casa',
        BP.Loja AS 'Casa',
        BP.Fornecedor AS 'Fornecedor',
        BP.Doc_Serie AS 'Doc Serie',
        DATE_FORMAT(BP.Data_Emissao, '%d/%m/%Y') AS 'Data Competencia',                                  
        DATE_FORMAT(BP.Data_Vencimento, '%d/%m/%Y') AS 'Data Vencimento',
        BP.Valor_Original AS 'Valor Original',
        BP.Valor_Liquido AS 'Valor Liquido',
        BP.Valor_Insumos AS 'Valor Cotação',
        DATE_FORMAT(BP.Data_Emissao, '%d/%m/%Y') AS 'Mes Texto'                               
      FROM View_BlueMe_Com_Pedido BP
      LEFT JOIN View_Insumos_Receb_Agrup_Por_Categ virapc ON BP.tdr_ID = virapc.tdr_ID
      WHERE DATE(BP.Data_Emissao) >= '{day}'
      AND DATE(BP.Data_Emissao) <= '{day2}'
  ''', use_fabrica=True)

@st.cache_data
def assoc_expense_items(day,day2):
  return get_dataframe_from_query(f'''
  SELECT 
  DRI.ID AS 'ID Associac Despesa Item',
  E.ID AS 'ID Casa',
  E.NOME_FANTASIA AS 'Casa',
  DR.ID AS 'ID Despesa',
  DATE_FORMAT(DR.COMPETENCIA, '%d/%m/%Y') AS 'Data Competencia',
  I5.ID AS 'ID Insumo',
  I5.DESCRICAO AS 'Insumo',
  UM.UNIDADE_MEDIDA_NAME AS 'Unidade Medida',                         
  CAST(REPLACE(DRI.QUANTIDADE, ',', '.') AS DECIMAL(10,2)) AS 'Quantidade Insumo',
  DRI.VALOR / CAST(REPLACE(DRI.QUANTIDADE, ',', '.') AS DECIMAL(10,2)) AS 'Valor Unitario',
  DRI.VALOR AS 'Valor Total'
  FROM T_DESPESA_RAPIDA_ITEM DRI 
  INNER JOIN T_INSUMOS_NIVEL_5 I5 ON (DRI.FK_INSUMO = I5.ID)
  INNER JOIN T_INSUMOS_NIVEL_4 I4 ON (I5.FK_INSUMOS_NIVEL_4 = I4.ID)
  INNER JOIN T_INSUMOS_NIVEL_3 I3 ON (I4.FK_INSUMOS_NIVEL_3 = I3.ID)
  INNER JOIN T_INSUMOS_NIVEL_2 I2 ON (I3.FK_INSUMOS_NIVEL_2 = I2.ID)
  INNER JOIN T_INSUMOS_NIVEL_1 I1 ON (I2.FK_INSUMOS_NIVEL_1 = I1.ID)
  INNER JOIN ADMIN_USERS AU ON (DRI.LAST_USER = AU.ID)
  INNER JOIN T_DESPESA_RAPIDA DR ON (DRI.FK_DESPESA_RAPIDA = DR.ID)
  INNER JOIN T_EMPRESAS E ON (DR.FK_LOJA = E.ID)
  LEFT JOIN T_UNIDADES_DE_MEDIDAS UM ON (I5.FK_UNIDADE_MEDIDA = UM.ID)
  ''', use_fabrica=True)

@st.cache_data
def supplier_expense_n5(day,day2):
  return get_dataframe_from_query(f"""
SELECT 
		F.ID AS 'ID Fornecedor',
		F.FANTASY_NAME AS 'Fornecedor',
    E.NOME_FANTASIA AS 'Casa',
    N5.ID AS 'ID Nivel 5',
    N5.DESCRICAO AS 'INSUMO N5',
    SUM(DRI.QUANTIDADE) AS 'Quantidade Insumo',
    SUM(DRI.VALOR) AS 'Valor Insumo',
    SUM(DRI.VALOR) / SUM(DRI.QUANTIDADE) AS 'Valor Med Por Insumo'                                
    FROM T_DESPESA_RAPIDA_ITEM DRI 
    INNER JOIN T_INSUMOS_NIVEL_5 N5 ON (DRI.FK_INSUMO = N5.ID)
    INNER JOIN T_DESPESA_RAPIDA DR ON (DRI.FK_DESPESA_RAPIDA = DR.ID)
    INNER JOIN T_FORNECEDOR F ON (DR.FK_FORNECEDOR = F.ID)
    INNER JOIN T_EMPRESAS E ON (DR.FK_LOJA = E.ID)
    WHERE DR.COMPETENCIA >= '{day}'
    AND DR.COMPETENCIA <= '{day2}'

		GROUP BY F.ID, N5.ID
    ORDER BY F.FANTASY_NAME, N5.DESCRICAO
""", use_fabrica=True)

@st.cache_data
def average_inputN5_price(day, day2):
  return get_dataframe_from_query(f"""
SELECT
  MIN(COALESCE(E.ID, DRI.ID_CASA)) AS 'CASA ID',
  MIN(COALESCE(E.NOME_FANTASIA, DRI.NOME_FANTASIA)) AS 'EMPRESA',
	N5.ID AS 'ID N5',
	N5.DESCRICAO AS 'INSUMO N5',
  UM.UNIDADE_MEDIDA_NAME AS 'Unidade de  Medida N5',
  (DRI.VALOR / DRI.QUANTIDADE) AS 'Média Preço (Insumo de Compra)',
  IE.ID AS 'ID Insumo de Estoque',
  IE.DESCRICAO AS 'Insumo de Estoque',
  UM2.UNIDADE_MEDIDA_NAME AS 'Unidade de Medida Estoque',
  ACE.PROPORCAO AS 'Proporção Compra',
  (DRI.VALOR / DRI.QUANTIDADE) / ACE.PROPORCAO AS 'Média Preço (Insumo Estoque)'
FROM T_INSUMOS_NIVEL_5 N5
LEFT JOIN T_CONTAGEM_INSUMOS CI ON CI.FK_INSUMO = N5.ID
LEFT JOIN T_VALORACAO_ESTOQUE VE ON VE.FK_CONTAGEM = CI.ID
LEFT JOIN T_UNIDADES_DE_MEDIDAS UM ON N5.FK_UNIDADE_MEDIDA = UM.ID
LEFT JOIN T_ASSOCIATIVA_COMPRA_ESTOQUE ACE ON ACE.FK_INSUMO = N5.ID
LEFT JOIN T_INSUMOS_ESTOQUE IE ON IE.ID = ACE.FK_INSUMO_ESTOQUE
LEFT JOIN T_UNIDADES_DE_MEDIDAS UM2 ON IE.FK_UNIDADE_MEDIDA = UM2.ID
LEFT JOIN T_EMPRESAS E ON E.ID = CI.FK_EMPRESA
LEFT JOIN (
  SELECT
    DR.COMPETENCIA,
    E.NOME_FANTASIA,
    E.ID AS ID_CASA,
    DRI.FK_INSUMO,
    DRI.QUANTIDADE,
    DRI.VALOR,
    ACE.FK_INSUMO_ESTOQUE,
    ACE.PROPORCAO
  FROM T_DESPESA_RAPIDA_ITEM DRI
  INNER JOIN T_DESPESA_RAPIDA DR ON DR.ID = DRI.FK_DESPESA_RAPIDA
  LEFT JOIN T_ASSOCIATIVA_COMPRA_ESTOQUE ACE ON ACE.FK_INSUMO = DRI.FK_INSUMO
  LEFT JOIN T_EMPRESAS E ON E.ID = DR.FK_LOJA
  WHERE DATE(DR.COMPETENCIA) BETWEEN '{day}' AND '{day2}'
    AND DRI.VALOR > 0
  GROUP BY DRI.ID
) AS DRI ON DRI.FK_INSUMO = N5.ID
WHERE N5.VM_ACTIVE = '1'
  AND (DATE(CI.DATA_CONTAGEM) BETWEEN '{day}' AND '{day2}' OR CI.DATA_CONTAGEM IS NULL)
  AND DRI.NOME_FANTASIA IS NOT NULL
GROUP BY E.ID, N5.ID
ORDER BY N5.DESCRICAO;
""", use_fabrica=True)

@st.cache_data
def item_sold():
  return get_dataframe_from_query(f"""
WITH ULTIMO_VALOR AS (
SELECT 
        IV.PRODUCT_ID,
  			MAX(IV.TRANSACTION_DATE),
        IV.UNIT_VALUE
    FROM T_ITENS_VENDIDOS IV
  	GROUP BY IV.PRODUCT_ID
)
SELECT
    IVC.CASA AS 'EMPRESA',
    AIFT.ID AS 'ID_Assoc',
    IVC.ITEM_VENDIDO AS 'Item Vendido',
    IE.DESCRICAO AS 'Insumo de Estoque',
    UM.UNIDADE_MEDIDA AS 'Unidade Medida',
    AIFT.QUANTIDADE_POR_FICHA AS 'Quantidade na Ficha',
    UV.UNIT_VALUE AS 'VALOR DO ITEM'
FROM T_ASSOCIATIVA_INSUMOS_FICHA_TECNICA AIFT
LEFT JOIN T_FICHAS_TECNICAS FT ON AIFT.FK_FICHA_TECNICA = FT.ID
LEFT JOIN T_VISUALIZACAO_ITENS_VENDIDOS_POR_CASA IVC ON FT.FK_ITEM_VENDIDO_POR_CASA = IVC.ID
LEFT JOIN T_INSUMOS_ESTOQUE IE ON AIFT.FK_ITEM_ESTOQUE = IE.ID
LEFT JOIN T_UNIDADES_DE_MEDIDAS UM ON IE.FK_UNIDADE_MEDIDA = UM.ID
LEFT JOIN ULTIMO_VALOR UV ON UV.PRODUCT_ID = IVC.ID_ZIG_ITEM_VENDIDO
""", use_fabrica=True)
