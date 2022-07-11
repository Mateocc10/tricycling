import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import plotly.graph_objects as go
import streamlit as st  # pip install streamlit
import datetime as dt
from datetime import date, timedelta
import openpyxl
import numpy as np

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Tri & Cycling", page_icon=":bar_chart:", layout="wide")


# ---- READ EXCEL / fixed ----
@st.cache(suppress_st_warning=True)
def get_data_from_excel():
    df = pd.read_excel("BD.xlsx")

    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    df['order_date'] = pd.to_datetime(df['order_date']).dt.date
    df['order_month'] = pd.to_datetime(df['order_month'], errors='coerce')
    df['order_month'] = pd.to_datetime(df['order_month']).dt.date
    df['order_week'] = pd.to_datetime(df['order_week'], errors='coerce')
    df['order_week'] = pd.to_datetime(df['order_week']).dt.date
    df['ela_date'] = pd.to_datetime(df['ela_date'], errors='coerce')
    df['event_date'] = pd.to_datetime(df['event_date'], errors='coerce')
    df['total'] = df['total'].astype(int)
    df['client_id'] = df['client_id'].astype(int)
    df['client_name'] = df['client_name'].astype(str).str.lower()
    df['center'] = df['center'].astype(str)
    df['product_id'] = df['product_id'].astype(str)
    df['year'] = df['year'].astype(str) 
    df['day'] = df['day'].astype(str)
    df['month'] = df['month'].astype(str) 
    df['order_id'] = df['n_comprobante'].astype(str) + '-' + df['cons'].astype(str)

    return df

df = get_data_from_excel()

#dataframe
df_orders = df[pd.notnull(df['metodo_pago'])]
df_orders = df_orders.groupby(['order_id','client_id','client_name','n_comprobante','email','order_month','order_week','order_date']).agg(total=('total','sum') ,metodos=('metodo_pago','nunique')).sort_values(by='order_date', ascending=False).reset_index()

# ---- SIDEBAR / FILTRS ----
st.sidebar.header("Please Filter Here:")

order_date = df_orders['order_date'].unique().tolist()
date_selection = st.sidebar.slider('Fecha:',
                            min_value= min(order_date),
                            max_value= max(order_date),
                            value=(min(order_date),max(order_date)))

almacen = df_orders['n_comprobante'].unique().tolist()
almacen_1 = almacen
almacen_1.append("todos")
almacen_selection = st.sidebar.selectbox(
                            "Almacen:",
                            almacen_1,
                            index = almacen_1.index("todos"))

cliente = df_orders['client_name'].unique().tolist()
cliente_1 = cliente
cliente_1.append("todos")
cliente_selection = st.sidebar.selectbox(
                            "Nombre de cliente:",
                            options=cliente,
                            index = cliente_1.index("todos"))

#se aplica validacion de los filtros
if 'todos' in almacen_selection and 'todos' in cliente_selection:
    mask = (df_orders['order_date'].between(*date_selection)) & (df_orders['n_comprobante'].isin(almacen)) & (df_orders['client_name'].isin(cliente))
elif 'todos' in almacen_selection and 'todos' not in cliente_selection:
    mask = (df_orders['order_date'].between(*date_selection)) & (df_orders['n_comprobante'].isin(almacen)) & (df_orders['client_name']==cliente_selection)
elif 'todos' in cliente_selection and 'todos' not in almacen_selection:
    mask = (df_orders['order_date'].between(*date_selection)) & (df_orders['n_comprobante']==almacen_selection) & (df_orders['client_name'].isin(cliente))
else:
    mask = (df_orders['order_date'].between(*date_selection)) & (df_orders['n_comprobante']==almacen_selection) & (df_orders['client_name']==cliente_selection)
 
df_selection = df_orders[mask]

# ---- MAINPAGE ----
st.title(":bar_chart: Productos Tri & Cycling")
st.markdown("##")