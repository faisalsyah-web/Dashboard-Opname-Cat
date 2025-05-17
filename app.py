import streamlit as st
import pandas as pd
import altair as alt

# Streamlit page config
st.set_page_config(page_title="Dashboard Stock Opname", layout="wide")
st.title("Dashboard Stock Opname")

# File uploader
uploaded_file = st.file_uploader("Upload JSON file", type=['json'])

if uploaded_file:
    # Load JSON into DataFrame
    data = pd.read_json(uploaded_file)

    # Currency parser
    def parse_money(x):
        if isinstance(x, str):
            s = x.replace('Rp', '').replace(',', '').strip()
            return int(s) if s and s != '0' else 0
        return 0

    # Add numeric columns
    cols = {
        'minus_store_nominal': 'Nominal Selisih Minus Store',
        'plus_store_nominal': 'Nominal Selisih Plus Store',
        'minus_gd_nominal': 'Nominal Selsih Minus GD',
        'plus_gd_nominal': 'Nominal Selsih Plus GD'
    }
    for new_col, raw_col in cols.items():
        data[new_col] = data[raw_col].apply(parse_money)

    # Prepare totals for bar chart
    totals = pd.DataFrame({
        'Lokasi': ['Store', 'Gudang'],
        'Minus': [data['minus_store_nominal'].sum(), data['minus_gd_nominal'].sum()],
        'Plus':  [data['plus_store_nominal'].sum(),  data['plus_gd_nominal'].sum()]
    })
    bar_data = totals.melt(id_vars=['Lokasi'], var_name='Tipe', value_name='Nominal')

    # Bar chart with labels
    def make_bar_chart(df):
        base = alt.Chart(df).encode(
            x=alt.X('Lokasi:N', title='Lokasi'),
            y=alt.Y('Nominal:Q', title='Nominal (Rp)'),
            color='Tipe:N',
            tooltip=[alt.Tooltip('Tipe:N'), alt.Tooltip('Nominal:Q', format=',')]
        )
        bars = base.mark_bar().properties(width=300, height=300)
        labels = bars.mark_text(dy=-5, fontSize=12, fontWeight='bold').encode(
            text=alt.Text('Nominal:Q', format='Rp,')
        )
        return (bars + labels).configure_legend(titleFontSize=14, labelFontSize=12)

    chart_bar = make_bar_chart(bar_data).properties(title='Total Nominal Minus & Plus per Store dan Gudang')

    # Function to count status and percent
    def prepare_pie_data(df, col):
        neg = (df[col] < 0).sum()
        zero = (df[col] == 0).sum()
        pos = (df[col] > 0).sum()
        dfc = pd.DataFrame({
            'Status': ['Minus', 'Sesuai', 'Plus'],
            'Count': [neg, zero, pos]
        })
        dfc['Percent'] = (dfc['Count'] / dfc['Count'].sum() * 100).round(1)
        return dfc

    # Filter by opname date
    df_store = data[data['TGL Store'].notnull()]
    df_gd = data[data['TGL GD'].notnull()]

    pie_store_data = prepare_pie_data(df_store, 'Selisih Store')
    pie_gd_data = prepare_pie_data(df_gd, 'Selisih GD')

    # Pie chart with percent labels
    def make_pie_chart(df, title):
        base = alt.Chart(df).encode(
            theta=alt.Theta('Count:Q', stack=True),
            color=alt.Color('Status:N', legend=alt.Legend(title='Status'))
        )
        pie = base.mark_arc(innerRadius=50).properties(width=300, height=300, title=title)
        text = base.mark_text(radius=90, fontSize=12, fontWeight='bold').encode(
            text=alt.Text('Percent:Q', format='.1f')
        )
        return (pie + text).configure_title(fontSize=14).configure_legend(labelFontSize=12, titleFontSize=12)

    chart_pie_store = make_pie_chart(pie_store_data, 'Item Selisih Store')
    chart_pie_gd = make_pie_chart(pie_gd_data, 'Item Selisih Gudang')

    # Layout: two columns
    col1, col2 = st.columns(2)
    with col1:
        st.altair_chart(chart_bar, use_container_width=True)
    with col2:
        st.altair_chart(alt.hconcat(chart_pie_store, chart_pie_gd).resolve_scale(color='independent'), use_container_width=True)

    # Display full data table
    st.subheader('Data Opname')
    st.dataframe(data, use_container_width=True)
else:
    st.info('Silakan upload file JSON untuk melihat dashboard.')
