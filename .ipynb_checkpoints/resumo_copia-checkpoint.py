import pandas as pd
import numpy as np



def resumo_copia(df):
    """
    Salva o df em cópia
    """
    df = pd.read_excel("denuncias-2025.xlsx")
    seg = df.copy() 
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