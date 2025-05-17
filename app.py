import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# Config
st.set_page_config(page_title="Dashboard Stock Opname", layout="wide")
st.title("Dashboard Stock Opname")

# File upload
uploaded_file = st.file_uploader("Upload JSON file", type=['json'])
if uploaded_file:
    data = pd.read_json(uploaded_file)

    # Parse currency strings to int
    def parse_money(x):
        if isinstance(x, str):
            s = x.replace('Rp', '').replace(',', '').strip()
            return int(s) if s and s != '0' else 0
        return 0

    data['minus_store_nominal'] = data['Nominal Selisih Minus Store'].apply(parse_money)
    data['plus_store_nominal'] = data['Nominal Selisih Plus Store'].apply(parse_money)
    data['minus_gd_nominal'] = data['Nominal Selsih Minus GD'].apply(parse_money)
    data['plus_gd_nominal'] = data['Nominal Selsih Plus GD'].apply(parse_money)

    # Total per toko/gudang
    totals = pd.DataFrame({
        'Lokasi': ['Store', 'Gudang'],
        'Minus': [data['minus_store_nominal'].sum(), data['minus_gd_nominal'].sum()],
        'Plus': [data['plus_store_nominal'].sum(), data['plus_gd_nominal'].sum()]
    })
    # Melt for grouped bar
    tot_melt = totals.melt(id_vars=['Lokasi'], value_vars=['Minus', 'Plus'], var_name='Tipe', value_name='Nominal')

    # Bar chart
    bar = alt.Chart(tot_melt).mark_bar().encode(
        x=alt.X('Lokasi:N', title='Lokasi'),
        y=alt.Y('Nominal:Q', title='Nominal (Rp)'),
        color='Tipe:N',
        tooltip=['Lokasi', 'Tipe', alt.Tooltip('Nominal:Q', format=',')]
    ).properties(width=350, height=300, title='Total Nominal Minus & Plus per Store dan Gudang')

    # Add text labels
    text = bar.mark_text(
        dy=-5,
        fontSize=12,
        fontWeight='bold'
    ).encode(
        text=alt.Text('Nominal:Q', format='Rp,')
    )

    chart1 = (bar + text).configure_legend(titleFontSize=14, labelFontSize=12)

    # Pie charts for store and gudang based on TGL
    df_store = data.dropna(subset=['TGL Store'])
    df_gd = data.dropna(subset=['TGL GD'])
    def count_status(df, col):
        neg = (df[col] < 0).sum()
        zero = (df[col] == 0).sum()
        pos = (df[col] > 0).sum()
        dfc = pd.DataFrame({
            'Status': ['Minus', 'Sesuai', 'Plus'],
            'Count': [neg, zero, pos]
        })
        dfc['Percent'] = (dfc['Count'] / dfc['Count'].sum() * 100).round(1)
        return dfc
    store_counts = count_status(df_store, 'Selisih Store')
    gd_counts = count_status(df_gd, 'Selisih GD')

    def pie_chart(dfc, title):
        base = alt.Chart(dfc).encode(
            theta=alt.Theta('Count:Q', stack=True),
            color=alt.Color('Status:N', legend=alt.Legend(title='Status'))
        )
        pie = base.mark_arc(innerRadius=50).properties(width=300, height=300, title=title)
        text = base.mark_text(radius=90, fontSize=12, fontWeight='bold').encode(
            text=alt.Text('Percent:Q', format='.1f')
        )
        return (pie + text).configure_title(fontSize=14).configure_legend(labelFontSize=12, titleFontSize=12)

    pie1 = pie_chart(store_counts, 'Item Selisih Store')
    pie2 = pie_chart(gd_counts, 'Item Selisih Gudang')

    # Layout
    col1, col2 = st.columns([1, 1])
    with col1:
        st.altair_chart(chart1, use_container_width=True)
    with col2:
        st.altair_chart(alt.concat(pie1, pie2, columns=2), use_container_width=True)

    # Data table
    st.subheader('Data Opname')
    st.dataframe(data)
else:
    st.info('Please upload a JSON file to view the dashboard.')
