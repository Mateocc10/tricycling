import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
import datetime as dt

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Tri & Cycling", page_icon=":bar_chart:", layout="wide")

# ---- READ EXCEL ----
df = pd.read_excel('BD.xlsx')
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


df_orders = df[pd.notnull(df['metodo_pago'])]
df_orders = df_orders.groupby(['order_id','client_id','client_name','n_comprobante','email','order_month','order_week','order_date']).agg(total=('total','sum') ,event_date=('event_date','max') ,metodos=('metodo_pago','nunique')).sort_values(by='order_date', ascending=False).reset_index()

# ---- SIDEBAR ----
st.sidebar.header("Please Filter Here:")
order_date = df_orders['order_date'].unique().tolist()

date_selection = st.sidebar.slider('date:',
                            min_value= min(order_date),
                            max_value= max(order_date),
                            value=(min(order_date),max(order_date)))


# df_selection = df.query(
#     "date == @city & Customer_type ==@customer_type & Gender == @gender"
# )

# ---- MAINPAGE ----
st.title(":bar_chart: Reporte Tri & Cycling")
st.markdown("##")

st.dataframe(df_orders)

# # TOP KPI's
# total_sales = int(df_selection["Total"].sum())
# average_rating = round(df_selection["Rating"].mean(), 1)
# star_rating = ":star:" * int(round(average_rating, 0))
# average_sale_by_transaction = round(df_selection["Total"].mean(), 2)

# left_column, middle_column, right_column = st.columns(3)
# with left_column:
#     st.subheader("Total Sales:")
#     st.subheader(f"US $ {total_sales:,}")
# with middle_column:
#     st.subheader("Average Rating:")
#     st.subheader(f"{average_rating} {star_rating}")
# with right_column:
#     st.subheader("Average Sales Per Transaction:")
#     st.subheader(f"US $ {average_sale_by_transaction}")

# st.markdown("""---""")

# # SALES BY PRODUCT LINE [BAR CHART]
# sales_by_product_line = (
#     df_selection.groupby(by=["Product line"]).sum()[["Total"]].sort_values(by="Total")
# )
# fig_product_sales = px.bar(
#     sales_by_product_line,
#     x="Total",
#     y=sales_by_product_line.index,
#     orientation="h",
#     title="<b>Sales by Product Line</b>",
#     color_discrete_sequence=["#0083B8"] * len(sales_by_product_line),
#     template="plotly_white",
# )
# fig_product_sales.update_layout(
#     plot_bgcolor="rgba(0,0,0,0)",
#     xaxis=(dict(showgrid=False))
# )

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


# left_column, right_column = st.columns(2)
# left_column.plotly_chart(fig_hourly_sales, use_container_width=True)
# right_column.plotly_chart(fig_product_sales, use_container_width=True)


# # ---- HIDE STREAMLIT STYLE ----
# hide_st_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             header {visibility: hidden;}
#             </style>
#             """
# st.markdown(hide_st_style, unsafe_allow_html=True)
