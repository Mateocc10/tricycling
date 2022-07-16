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
df_products = df[df['metodo_pago'].isnull()]
df_products = df_products.groupby(['order_id','product_id','product_name','n_comprobante','client_name']).agg(order_date=('order_date','max'), order_month=('order_month','max'), units=('units','sum'), total=('total','sum')).sort_values(by='order_date', ascending=False).reset_index()

# ---- SIDEBAR / FILTRS ----
st.sidebar.header("Please Filter Here:")

order_date = df_products['order_date'].unique().tolist()
date_selection = st.sidebar.slider('Fecha:',
                            min_value= min(order_date),
                            max_value= max(order_date),
                            value=(min(order_date),max(order_date)))

almacen = df_products['n_comprobante'].unique().tolist()
almacen_1 = almacen
almacen_1.append("todos")
almacen_selection = st.sidebar.selectbox(
                            "Almacen:",
                            almacen_1,
                            index = almacen_1.index("todos"))

producto = df_products['product_name'].unique().tolist()
producto_1 = producto
producto_1.append("todos")
producto_selection = st.sidebar.selectbox(
                            "Nombre de Producto:",
                            options=producto,
                            index = producto_1.index("todos"))

cliente = df_products['client_name'].unique().tolist()
cliente_1 = cliente
cliente_1.append("todos")
cliente_selection = st.sidebar.selectbox(
                            "Nombre de cliente:",
                            options=cliente,
                            index = cliente_1.index("todos"))

#se aplica validacion de los filtros
if 'todos' in almacen_selection and 'todos' in cliente_selection and 'todos' in producto_selection:
    mask = (df_products['order_date'].between(*date_selection)) & (df_products['n_comprobante'].isin(almacen)) & (df_products['client_name'].isin(cliente)) & (df_products['product_name'].isin(producto))

elif 'todos' in almacen_selection and 'todos' in cliente_selection and 'todos' not in producto_selection:
    mask = (df_products['order_date'].between(*date_selection)) & (df_products['n_comprobante'].isin(almacen)) & (df_products['client_name'].isin(cliente)) & (df_products['product_name']==producto_selection)

elif 'todos' in almacen_selection and 'todos' not in cliente_selection and 'todos' in producto_selection:
    mask = (df_products['order_date'].between(*date_selection)) & (df_products['n_comprobante'].isin(almacen)) & (df_products['client_name']==cliente_selection) & (df_products['product_name'].isin(producto))

elif 'todos' not in almacen_selection and 'todos' in cliente_selection and 'todos' in producto_selection:
    mask = (df_products['order_date'].between(*date_selection)) & (df_products['n_comprobante']==almacen_selection) & (df_products['client_name'].isin(cliente)) & (df_products['product_name'].isin(producto))

elif 'todos' in almacen_selection and 'todos' not in cliente_selection and 'todos' not in producto_selection:
    mask = (df_products['order_date'].between(*date_selection)) & (df_products['n_comprobante'].isin(almacen)) & (df_products['client_name']==cliente_selection) & (df_products['product_name']==producto_selection)

elif 'todos' not in almacen_selection and 'todos' not in cliente_selection and 'todos' in producto_selection:
    mask = (df_products['order_date'].between(*date_selection)) & (df_products['n_comprobante']==almacen_selection) & (df_products['client_name']==cliente_selection) & (df_products['product_name'].isin(producto))

elif 'todos' not in almacen_selection and 'todos' in cliente_selection and 'todos' not in producto_selection:
    mask = (df_products['order_date'].between(*date_selection)) & (df_products['n_comprobante']==almacen_selection) & (df_products['client_name'].isin(cliente)) & (df_products['product_name']==producto_selection)

else:
    mask = (df_products['order_date'].between(*date_selection)) & (df_products['n_comprobante']==almacen_selection) & (df_products['client_name']==cliente_selection) & (df_products['product_name']==producto_selection)
 
df_selection = df_products[mask]

# ---- MAINPAGE ----
st.title(":bar_chart: Productos Tri & Cycling")
st.markdown("##")


# TOP KPI's
total_products = int(df_selection["product_id"].nunique())
total_unidades = int(df_selection['units'].sum())
prom_product = int(df_selection['total'].mean())

a_column, b_column, c_column = st.columns(3)
with a_column:
    st.subheader("Productos")
    st.subheader(total_products)
with b_column:
    st.subheader("Unidades")
    st.subheader(total_unidades)
with c_column:
    st.subheader("Prom valor productos")
    st.subheader(f"COP $ {prom_product:,}")

st.markdown("""---""")


#grafico 1
df_grafico1 = df_selection.groupby(['order_month']).agg(productos_vendidos=('product_id','nunique')).sort_values(by='order_month',ascending=False).reset_index()

try:
    fig1 = px.bar(df_grafico1, 
        x="order_month", 
        y="productos_vendidos", 
        #color="client_valido", 
        title="<b>Productos Vendidos</b>"
    )

    fig1.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )
except IndexError:
    fig1 = go.Figure(
        data=[go.Bar(y=[0, 0, 0])],
        layout_title_text="<b>Productos Vendidos</b>"
)

df_grafico2 = df_selection.groupby(['order_month']).agg(unidades_vendidas=('units','sum')).sort_values(by='order_month',ascending=False).reset_index()

try:
    fig2 = px.bar(df_grafico2, 
        x="order_month", 
        y="unidades_vendidas", 
        #color="client_valido", 
        title="<b>Unidades Vendidas</b>"
    )

    fig2.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )
except IndexError:
    fig2 = go.Figure(
        data=[go.Bar(y=[0, 0, 0])],
        layout_title_text="<b>Unidades Vendidas</b>"
)

a_column, b_column = st.columns(2)
a_column.plotly_chart(fig1, use_container_width=True)
b_column.plotly_chart(fig2, use_container_width=True)

#tabla 1
df_tabla1 = df_selection.groupby(['product_name']).agg(ordenes=('order_id','nunique'), ventas=('total','sum'), unidades_vendidos=('units','sum'), promedio_venta=('total','mean')).sort_values(by='ordenes',ascending=False).reset_index()
st.dataframe(df_tabla1)

df_tabla2 = df_selection.groupby(['product_name','order_month']).agg(ordenes=('order_id','nunique')).sort_values(by='ordenes',ascending=False).reset_index()
df_tabla2 = pd.pivot_table(df_tabla2, values='ordenes', index='product_name', columns='order_month', aggfunc=np.sum)
df_tabla2['total'] = df_tabla2.sum(axis=1)
df_tabla2 = df_tabla2.sort_values(by='total', ascending=False)
st.dataframe(df_tabla2)

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
