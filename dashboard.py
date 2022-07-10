import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
import datetime as dt
import openpyxl

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
    df['client_name'] = df['client_name'].astype(str)
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
almacen_selection = st.sidebar.multiselect(
                            "Almacen:",
                            options=almacen,
                            default=almacen)

mask = (df_orders['order_date'].between(*date_selection)) & (df_orders['n_comprobante'].isin(almacen_selection))
df_selection = df_orders[mask]

# ---- MAINPAGE ----
st.title(":bar_chart: Reporte Tri & Cycling")
st.markdown("##")

# TOP KPI's
total_sales = int(df_selection["total"].sum())
total_orders = int(df_selection["order_id"].nunique())
total_clientes = int(df_selection['client_id'].nunique())
aov = int(total_sales/total_orders)

mystyle = '''
    <style>
        p {
            text-align: justify;
        }
    </style>
    '''

st.columns(mystyle, unsafe_allow_html=True)

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


#grafico numero 1 - ventas mes a mes
sales_by_product_line = (
    df_selection.groupby(['order_month']).agg(orders=('order_id','nunique'), total=('total','sum'),clients=('client_id','nunique')).sort_values(by='order_month', ascending=False)
)

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


left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_product_sales, use_container_width=True)


st.dataframe(df_selection)

# # SALES BY HOUR [BAR CHART]
# sales_by_hour = df_selection.groupby(by=["hour"]).sum()[["Total"]]
# fig_hourly_sales = px.bar(
#     sales_by_hour,
#     x=sales_by_hour.index,
#     y="Total",
#     title="<b>Sales by hour</b>",
#     color_discrete_sequence=["#0083B8"] * len(sales_by_hour),
#     template="plotly_white",
# )
# fig_hourly_sales.update_layout(
#     xaxis=dict(tickmode="linear"),
#     plot_bgcolor="rgba(0,0,0,0)",
#     yaxis=(dict(showgrid=False)),
# )



# right_column.plotly_chart(fig_product_sales, use_container_width=True)


# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
