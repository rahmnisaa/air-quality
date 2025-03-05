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
city = st.sidebar.selectbox("Pilih Stasiun Pemantauan", df["station"].unique())
pollutant = st.sidebar.selectbox("Pilih Polutan", ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3'])
extra_var = st.sidebar.selectbox("Pilih Variabel Tambahan", ['TEMP', 'PRES', 'DEWP'])
date_range = st.sidebar.slider("Pilih Rentang Tanggal", 
                               min_value=df['datetime'].min().date(),
                               max_value=df['datetime'].max().date(),
                               value=(df['datetime'].min().date(), df['datetime'].max().date()))

# Filter data berdasarkan pilihan pengguna
df_filtered = df[(df["station"] == city) & 
                 (df['datetime'].dt.date.between(date_range[0], date_range[1]))]

st.title("📊 Dashboard Kualitas Udara")
st.markdown("### Analisis polusi udara dan variabel lingkungan lainnya dengan layout optimal.")

# Layout Grid 3x2 untuk menampilkan lebih banyak visualisasi
col1, col2, col3 = st.columns(3)

# Plot Time Series
with col1:
    st.subheader(f"📈 Tren {pollutant}")
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot(df_filtered['datetime'], df_filtered[pollutant], label=pollutant, color='red', linewidth=1.5)
    ax.set_xlabel("Tanggal")
    ax.set_ylabel(f"Konsentrasi {pollutant}")
    ax.legend()
    st.pyplot(fig)

# Histogram Polutan
with col2:
    st.subheader(f"📊 Distribusi {pollutant}")
    fig, ax = plt.subplots(figsize=(5, 3))
    sns.histplot(df_filtered[pollutant], bins=30, kde=True, ax=ax, color='blue')
    ax.set_xlabel(f"Konsentrasi {pollutant}")
    st.pyplot(fig)

# Boxplot Polutan
with col3:
    st.subheader(f"📦 Boxplot {pollutant}")
    fig, ax = plt.subplots(figsize=(5, 3))
    sns.boxplot(y=df_filtered[pollutant], ax=ax, color='green')
    ax.set_ylabel(f"Konsentrasi {pollutant}")
    st.pyplot(fig)

# Visualisasi Variabel Tambahan
with col1:
    st.subheader(f"🌡️ Tren {extra_var}")
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot(df_filtered['datetime'], df_filtered[extra_var], label=extra_var, color='orange', linewidth=1.5)
    ax.set_xlabel("Tanggal")
    ax.set_ylabel(extra_var)
    ax.legend()
    st.pyplot(fig)

# Histogram Variabel Tambahan
with col2:
    st.subheader(f"📊 Distribusi {extra_var}")
    fig, ax = plt.subplots(figsize=(5, 3))
    sns.histplot(df_filtered[extra_var], bins=30, kde=True, ax=ax, color='purple')
    ax.set_xlabel(extra_var)
    st.pyplot(fig)

# Peta Interaktif dengan Heatmap
with col3:
    st.subheader("🗺️ Peta Kualitas Udara")
    m = folium.Map(location=[df_filtered['latitude'].mean(), df_filtered['longitude'].mean()], zoom_start=10)
    HeatMap(data=list(zip(df_filtered['latitude'], df_filtered['longitude'], df_filtered[pollutant]))).add_to(m)
    folium_static(m)

st.markdown("---")
