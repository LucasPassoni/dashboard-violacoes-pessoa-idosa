import pandas as pd
import numpy as np
import unicodedata



def resumo(dados):
    
    seg = dados.copy()    
    """
    Retorna um resumo de nulos, tipos de dados e estatísticas básicas.
    """
    print("--- Formato ---")
    print(seg.shape)
    print("\n--- Tipos de Dados ---")
    print(seg.dtypes)
    print("\n--- Valores Nulos ---")
    print(seg.isnull().sum())
    print("\n--- Resumo Estatístico ---")
    return seg.describe()


def verificar_categorias(df):
    # Seleciona apenas colunas do tipo object ou category
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    
    # Cria um dicionário mostrando o array de valores únicos para cada coluna
    unicos = {col: df[col].unique() for col in cat_cols}
    return unicos

def padronizar_colunas(df):
    """
    Padroniza os nomes das colunas de um DataFrame.
    Converte para minúsculo, remove espaços extras e substitui espaços internos por '_'.
    """
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_", regex=False)
    return df

