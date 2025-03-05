import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static

# Fungsi untuk memuat data dari Google Drive
@st.cache_data
def load_data():
    url = "https://drive.google.com/uc?id=1HCl0uXbbOggLnpNLY0PwSa_AYsTgLuKi"
    df = pd.read_csv(url, parse_dates=['datetime'])
    return df

df = load_data()

# Sidebar untuk filter
st.sidebar.header("Filter Data")
st.sidebar.subheader("Pilih Parameter")
stations = st.sidebar.multiselect("Pilih Stasiun Pemantauan", df["station"].unique(), default=df["station"].unique()[:2])
pollutants = st.sidebar.multiselect("Pilih Polutan", ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3'], default=['PM2.5', 'PM10'])
extra_vars = st.sidebar.multiselect("Pilih Variabel Tambahan", ['TEMP', 'PRES', 'DEWP'], default=['TEMP'])
date_range = st.sidebar.slider("Pilih Rentang Tanggal", 
                               min_value=df['datetime'].min().date(),
                               max_value=df['datetime'].max().date(),
                               value=(df['datetime'].min().date(), df['datetime'].max().date()))

# Filter data berdasarkan pilihan pengguna
df_filtered = df[(df["station"].isin(stations)) & 
                 (df['datetime'].dt.date.between(date_range[0], date_range[1]))]

st.title("📊 Dashboard Kualitas Udara")
st.markdown("#### Analisis polusi udara dan variabel lingkungan dengan perbandingan multi-stasiun dan multi-variabel.")

# Layout Grid 3x3 untuk tampilan lebih optimal
col1, col2, col3 = st.columns([1, 1, 1.5])

# Plot Time Series untuk Polutan
with col1:
    for pollutant in pollutants:
        st.subheader(f"📈 Tren {pollutant}")
        fig, ax = plt.subplots(figsize=(5, 3))
        for station in stations:
            df_station = df_filtered[df_filtered["station"] == station]
            ax.plot(df_station['datetime'], df_station[pollutant], label=f"{pollutant} - {station}")
        ax.set_xlabel("Tanggal")
        ax.set_ylabel(f"Konsentrasi {pollutant}")
        ax.legend()
        st.pyplot(fig)

# Histogram untuk Polutan (ditumpuk berbeda warna)
with col2:
    st.subheader("📊 Distribusi Polutan")
    fig, ax = plt.subplots(figsize=(5, 3))
    for pollutant in pollutants:
        sns.histplot(df_filtered[pollutant], bins=30, kde=True, ax=ax, label=pollutant, alpha=0.5)
    ax.set_xlabel("Konsentrasi Polutan")
    ax.legend()
    st.pyplot(fig)

# Boxplot untuk Polutan (sebelahan dalam satu kotak)
with col1:
    st.subheader("📦 Boxplot Polutan")
    fig, ax = plt.subplots(figsize=(5, 3))
    sns.boxplot(data=df_filtered[pollutants], ax=ax)
    ax.set_ylabel("Konsentrasi Polutan")
    st.pyplot(fig)

# Plot Time Series untuk Variabel Tambahan
with col2:
    for extra_var in extra_vars:
        st.subheader(f"🌡️ Tren {extra_var}")
        fig, ax = plt.subplots(figsize=(5, 3))
        for station in stations:
            df_station = df_filtered[df_filtered["station"] == station]
            ax.plot(df_station['datetime'], df_station[extra_var], label=f"{extra_var} - {station}")
        ax.set_xlabel("Tanggal")
        ax.set_ylabel(extra_var)
        ax.legend()
        st.pyplot(fig)

# Peta Interaktif dengan Heatmap dalam ukuran persegi panjang
with col3:
    st.subheader("🗺️ Peta Kualitas Udara")
    m = folium.Map(location=[df_filtered['latitude'].mean(), df_filtered['longitude'].mean()], zoom_start=10)
    for pollutant in pollutants:
        HeatMap(data=list(zip(df_filtered['latitude'], df_filtered['longitude'], df_filtered[pollutant]))).add_to(m)
    folium_static(m, width=800, height=500)

st.markdown("---")
