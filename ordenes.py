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
st.title(":bar_chart: Ordenes Tri & Cycling")
st.markdown("##")

# TOP KPI's
total_sales = int(df_selection["total"].sum())
total_orders = int(df_selection["order_id"].nunique())
total_clientes = int(df_selection['client_id'].nunique())
try:
    aov = int(total_sales/total_orders)
except ZeroDivisionError:
    aov = 0

a_column, b_column, c_column, d_column = st.columns(4)
with a_column:
    st.subheader("Ventas:")
    st.subheader(f"COP $ {total_sales:,}")
with b_column:
    st.subheader("Ordenes")
    st.subheader(total_orders)
with c_column:
    st.subheader("Clientes")
    st.subheader(total_clientes)
with d_column:
    st.subheader("valor por orden")
    st.subheader(f"COP $ {aov:,}")

st.markdown("""---""")


#grafico 1
sales_by_product_line = (
    df_selection.groupby(['order_month']).agg(orders=('order_id','nunique'), total=('total','sum'),clients=('client_id','nunique')).sort_values(by='order_month', ascending=False)
)

try:
    fig_product_sales = px.bar(
        sales_by_product_line,
        x=sales_by_product_line.index,
        y="total",
        orientation="v",
        title="<b>Ventas por mes</b>",
        color_discrete_sequence=["#0083B8"] * len(sales_by_product_line),
        template="plotly_white",
    )
    fig_product_sales.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )
except IndexError:
    fig4 = go.Figure(
        data=[go.Bar(y=[0, 0, 0])],
        layout_title_text="<b>Ventas por mes</b>"
)



#grafico 2
df_grafico2 = df_selection.groupby(['order_month']).agg(orders=('order_id','nunique'), total=('total','sum'),clients=('client_id','nunique')).sort_values(by='order_month', ascending=False).reset_index()
df_grafico2['aov'] = df_grafico2['total']/df_grafico2['orders']
df_grafico2['aov'] = df_grafico2['aov'].astype(int)
sales_by_hour = (
    df_grafico2.groupby(by=["order_month"]).sum()[["aov"]]
)

try:
    fig_hourly_sales = px.bar(
        sales_by_hour,
        x=sales_by_hour.index,
        y="aov",
        title="<b>Valor promedio por orden</b>",
        color_discrete_sequence=["#0083B8"] * len(sales_by_hour),
        template="plotly_white",
    )
    fig_hourly_sales.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )
except IndexError:
    fig4 = go.Figure(
        data=[go.Bar(y=[0, 0, 0])],
        layout_title_text="<b>Valor promedio por orden</b>"
)


#grafico 3
df_grafico3 = df_selection.groupby(['order_month','client_name']).agg(orders=('order_id','nunique'), total=('total','sum')).sort_values(by=['order_month','orders'], ascending=False).reset_index()
df_grafico3['client_name'] = df_grafico3['client_name'].str.lower()
df_grafico3['client_valido'] = np.where(df_grafico3['client_name']=='cuantias menores', 'no','yes')
df_grafico3 = df_grafico3.groupby(['order_month','client_valido']).agg(total=('total','sum')).sort_values(by=['order_month','total'], ascending=False).reset_index()

try:
    fig3 = px.bar(df_grafico3, 
        x="order_month", 
        y="total", 
        color="client_valido", 
        title="<b>Ventas clientes validos o no</b>"
    )

    fig3.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )
except IndexError:
    fig4 = go.Figure(
        data=[go.Bar(y=[0, 0, 0])],
        layout_title_text="<b>Ventas clientes validos o no</b>"
)

#base para graficos 4, 5 , 6 y tabla
df_selection['client_name'] = df_selection['client_name'].str.lower()
df_selection['client_valido'] = np.where(df_selection['client_name']=='cuantias menores', 'no','yes')
df_base = df_selection[df_selection['client_valido']=='yes']
df_base = df_base[['order_id','client_name','total','order_date','order_week','order_month']]
#base para los graficos 4
df_base['rank'] = df_base.groupby(['client_name'])['order_date'].rank(method='first').astype(int)
df_base_1 = df_base.sort_values(by='rank', ascending=False)
df_base_1['rank_1'] = df_base_1['rank'] + 1
df_base_1 = df_base_1[['client_name','rank_1','order_date']]
df_base_2 = df_base.merge(df_base_1, left_on = ['client_name','rank'], right_on=['client_name','rank_1'])
df_base_2['order_date_x'] = pd.to_datetime(df_base_2['order_date_x'], errors='coerce')
df_base_2['order_date_y'] = pd.to_datetime(df_base_2['order_date_y'], errors='coerce')
df_base_2['day_diff'] = (df_base_2['order_date_x'] - df_base_2['order_date_y']).dt.days

#grafico 4
df_grafico4 = df_base_2.groupby(['order_month']).agg(dias_promedio=('day_diff','mean')).round(0).sort_values(by='order_month', ascending=False).reset_index()

try:
    fig4 = px.bar(df_grafico4, 
        x="order_month", 
        y="dias_promedio", 
        title="<b>Clientes validos, tiempo prom proxima compra</b>",
        color_discrete_sequence=["#0083B8"] * len(df_grafico4)
    )

    fig4.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )
except IndexError:
    fig4 = go.Figure(
        data=[go.Bar(y=[0, 0, 0])],
        layout_title_text="<b>Clientes validos, tiempo prom proxima compra</b>"
)


#grafico 5
df_grafico5 = df_base.groupby(['order_month']).agg(clients=('client_name','nunique'), orders=('order_id','nunique')).reset_index()
df_grafico5['ordenes/clientes'] = (df_grafico5['orders']/df_grafico5['clients']).round(1)
df_grafico5 = df_grafico5.sort_values(by='order_month', ascending=False)

try:
    fig5 = px.bar(df_grafico5, 
        x="order_month", 
        y="ordenes/clientes", 
        title="<b>Clientes validos, ordenes / clientes</b>",
        color_discrete_sequence=["#0083B8"] * len(df_grafico5)
    )

    fig5.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )
except IndexError:
    fig5 = go.Figure(
        data=[go.Bar(y=[0, 0, 0])],
        layout_title_text="<b>Clientes validos, ordenes / clientes</b>"
)

#grafico 6
df_grafico6 = df_base.groupby(['rank']).agg(clientes=('client_name','nunique')).sort_values(by='rank', ascending = False).reset_index()
df_grafico6 = df_grafico6[df_grafico6['rank']<=25]

try:
    fig6 = px.bar(df_grafico6, 
        x="rank", 
        y="clientes", 
        title="<b>Nº ordenes clientes unicos</b>",
        color_discrete_sequence=["#0083B8"] * len(df_grafico5)
    )

    fig6.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )
except IndexError:
    fig6 = go.Figure(
        data=[go.Bar(y=[0, 0, 0])],
        layout_title_text="<b>Nº ordenes clientes unicos</b>"
)

#agregar las graficas
a_column, b_column = st.columns(2)
a_column.plotly_chart(fig_product_sales, use_container_width=True)
b_column.plotly_chart(fig_hourly_sales, use_container_width=True)

c_column, d_column = st.columns(2)
c_column.plotly_chart(fig3, use_container_width=True)
d_column.plotly_chart(fig4, use_container_width=True)

e_column, f_column = st.columns(2)
e_column.plotly_chart(fig5, use_container_width=True)
f_column.plotly_chart(fig6, use_container_width=True)


#table 1
# try:
df_clientes = df_base.groupby(['client_name']).agg(ordenes=('order_id','nunique'), compras =('total','sum'), primera_orden=('order_date','min'),ultima_orden=('order_date','max')).sort_values(by='compras', ascending = False).reset_index()
df_clientes['dias_con_nosotros']  = (dt.datetime.now().date() - df_clientes['primera_orden']).dt.days
df_clientes['valor_prom'] = df_clientes['compras'] / df_clientes['ordenes']
df_clientes['valor_prom'] = df_clientes['valor_prom'].astype(int)
st.dataframe(df_clientes)
# except AttributeError:
#     st.table([])

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)