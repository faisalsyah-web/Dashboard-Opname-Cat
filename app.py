import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# Title
st.set_page_config(page_title="Dashboard Stock Opname", layout="wide")
st.title("Dashboard Stock Opname")

# File uploader
uploaded_file = st.file_uploader("Upload JSON file", type=['json'])

if uploaded_file:
    # Load data
    data = pd.read_json(uploaded_file)

    # Parse numeric columns
    def parse_money(x):
        return int(x.replace('Rp','').replace(',','').replace('-','-')) if isinstance(x, str) else 0

    data['minus_store_nominal'] = data['Nominal Selisih Minus Store'].apply(parse_money)
    data['plus_store_nominal'] = data['Nominal Selisih Plus Store'].apply(parse_money)
    data['minus_gd_nominal'] = data['Nominal Selsih Minus GD'].apply(parse_money)
    data['plus_gd_nominal'] = data['Nominal Selsih Plus GD'].apply(parse_money)

    # Calculate totals
    total_minus = data['minus_store_nominal'].sum() + data['minus_gd_nominal'].sum()
    total_plus = data['plus_store_nominal'].sum() + data['plus_gd_nominal'].sum()

    # Bar Chart: Total Nominal
    nominal_df = pd.DataFrame({
        'Category': ['Total Minus', 'Total Plus'],
        'Nominal': [total_minus, total_plus]
    })
    chart1 = alt.Chart(nominal_df).mark_bar().encode(
        x='Category',
        y='Nominal',
        tooltip=['Category', 'Nominal']
    ).properties(width=400, height=300, title='Perbandingan Total Nominal Minus & Plus')

    # Pie Charts for item counts based on TGL
    df_store = data.dropna(subset=['TGL Store'])
    df_gd = data.dropna(subset=['TGL GD'])
    def count_status(df, col):
        neg = (df[col] < 0).sum()
        zero = (df[col] == 0).sum()
        pos = (df[col] > 0).sum()
        return pd.DataFrame({
            'Status': ['Minus', 'Sesuai', 'Plus'],
            'Count': [neg, zero, pos]
        })

    store_counts = count_status(df_store, 'Selisih Store')
    gd_counts = count_status(df_gd, 'Selisih GD')

    pie_store = alt.Chart(store_counts).mark_arc().encode(
        theta=alt.Theta(field="Count", type="quantitative"),
        color=alt.Color(field="Status", type="nominal"),
        tooltip=['Status', 'Count']
    ).properties(width=300, height=300, title="Item Selisih Toko")

    pie_gd = alt.Chart(gd_counts).mark_arc().encode(
        theta=alt.Theta(field="Count", type="quantitative"),
        color=alt.Color(field="Status", type="nominal"),
        tooltip=['Status', 'Count']
    ).properties(width=300, height=300, title="Item Selisih Gudang")

    # Layout
    col1, col2 = st.columns(2)
    with col1:
        st.altair_chart(chart1, use_container_width=True)
    with col2:
        st.altair_chart(alt.hconcat(pie_store, pie_gd).resolve_scale(color='independent'), use_container_width=True)

    # Display data table
    st.markdown("### Data Opname")
    st.dataframe(data)
else:
    st.info("Please upload a JSON file to display the dashboard.")
