import streamlit as st
import pandas as pd
import altair as alt

# Config
st.set_page_config(page_title="Dashboard Stock Opname", layout="wide")
st.title("Dashboard Stock Opname")

# Uploader
uploaded_file = st.file_uploader("Upload JSON file", type=['json'])
if uploaded_file:
    data = pd.read_json(uploaded_file)

    # Parser currency
    def parse_money(x):
        if isinstance(x, str):
            s = x.replace('Rp', '').replace(',', '').strip()
            return int(s) if s else 0
        return 0

    # Numeric columns
    data['minus_store_nominal'] = data['Nominal Selisih Minus Store'].apply(parse_money)
    data['plus_store_nominal']  = data['Nominal Selisih Plus Store'].apply(parse_money)
    data['minus_gd_nominal']    = data['Nominal Selsih Minus GD'].apply(parse_money)
    data['plus_gd_nominal']     = data['Nominal Selsih Plus GD'].apply(parse_money)

    # Grouped bar: separate Store/Gudang minus & plus
    bar_df = pd.DataFrame({
        'Lokasi': ['Store','Store','Gudang','Gudang'],
        'Tipe': ['Minus','Plus','Minus','Plus'],
        'Nominal': [data['minus_store_nominal'].sum(), data['plus_store_nominal'].sum(),
                    data['minus_gd_nominal'].sum(),   data['plus_gd_nominal'].sum()]
    })
    base = alt.Chart(bar_df).encode(
        x=alt.X('Lokasi:N', title='Lokasi'),
        y=alt.Y('Nominal:Q', title='Nominal (Rp)'),
        color=alt.Color('Tipe:N', legend=alt.Legend(title='Tipe')),
        column=alt.Column('Tipe:N', title=None)
    )
    bars = base.mark_bar().properties(height=300)
    labels = base.mark_text(dy=-5, fontSize=12, fontWeight='bold').encode(
        text=alt.Text('Nominal:Q', format='Rp,')
    )
    bar_chart = (bars + labels).configure_title(fontSize=16)

    # Pie data
    def count_status(df, col):
        neg = (df[col]<0).sum(); eq = (df[col]==0).sum(); pos = (df[col]>0).sum()
        dfc = pd.DataFrame({'Status':['Minus','Sesuai','Plus'],'Count':[neg,eq,pos]})
        dfc['Percent'] = (dfc['Count']/dfc['Count'].sum()*100).round(1)
        return dfc
    df_store = data[data['TGL Store'].notnull()]
    df_gd    = data[data['TGL GD'].notnull()]
    pie_store = count_status(df_store,'Selisih Store')
    pie_gd    = count_status(df_gd,'Selisih GD')

    def make_pie(dfc, title):
        chart = alt.Chart(dfc).encode(
            theta=alt.Theta('Count:Q', stack=True),
            color=alt.Color('Status:N', legend=alt.Legend(title='Status'))
        )
        pie = chart.mark_arc(innerRadius=50).properties(width=250, height=250, title=title)
        text = chart.mark_text(radius=80, fontSize=12, fontWeight='bold').encode(
            text=alt.Text('Percent:Q', format='.1f')
        )
        return (pie + text).configure_title(fontSize=14).configure_legend(labelFontSize=12)
    pie_chart_store = make_pie(pie_store,'Item Selisih Store')
    pie_chart_gd    = make_pie(pie_gd,   'Item Selisih Gudang')

    # Layout
    st.subheader('Total Nominal per Tipe & Lokasi')
    st.altair_chart(bar_chart, use_container_width=True)
    st.subheader('Distribusi Item Selisih')
    col1,col2 = st.columns(2)
    with col1:
        st.altair_chart(pie_chart_store, use_container_width=True)
    with col2:
        st.altair_chart(pie_chart_gd, use_container_width=True)

    # Data table with all columns
    st.subheader('Data Opname Lengkap')
    st.dataframe(data, use_container_width=True)
else:
    st.info('Silakan upload file JSON.')
