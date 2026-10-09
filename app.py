import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="Visor INACH RT_12_21", layout="wide")

st.title("❄️ Visor Interactivo - Proyecto INACH RT_12_21")
st.markdown("Plataforma interactiva para la exploración geoquímica y enzimática de suelos antárticos.")

# Cargar los datos desde el archivo Excel integrado en el repositorio
@st.cache_data
def load_data():
    return pd.read_excel('INACH_RT_12_21_quimica_suelo_enzimas_R_ready.xlsx', sheet_name=0)

df = load_data()

# Mostrar las columnas disponibles para depurar si fuera necesario
# st.write("Columnas detectadas:", df.columns.tolist())

# Detectar automáticamente las columnas clave de la planilla
col_etapa = 'etapa_deglaciacion' if 'etapa_deglaciacion' in df.columns else df.columns[1]
col_tratamiento = 'treatment_short' if 'treatment_short' in df.columns else (df.columns[2] if len(df.columns) > 2 else df.columns[0])
col_ph = 'ph_suelo' if 'ph_suelo' in df.columns else [c for c in df.columns if 'ph' in c.lower()][0]
col_carb = 'c_total_gkg' if 'c_total_gkg' in df.columns else [c for c in df.columns if 'c_total' in c.lower() or 'carbono' in c.lower()][0]
col_enzima = 'beta_glucosidase_nmol_muf_g_h' if 'beta_glucosidase_nmol_muf_g_h' in df.columns else [c for c in df.columns if 'glucosidase' in c.lower() or 'beta' in c.lower()][0]

# Filtros interactivos en la barra lateral
st.sidebar.header("🎛️ Filtros Dinámicos")

opciones_etapa = df[col_etapa].dropna().unique()
etapa_sel = st.sidebar.multiselect("Seleccione Etapa:", options=opciones_etapa, default=opciones_etapa)

opciones_tratamiento = df[col_tratamiento].dropna().unique()
tratamiento_sel = st.sidebar.multiselect("Seleccione Tratamiento:", options=opciones_tratamiento, default=opciones_tratamiento)

# Filtrar dataframe según selección de manera segura
df_filtered = df[
    (df[col_etapa].isin(etapa_sel)) & 
    (df[col_tratamiento].isin(tratamiento_sel))
]

# Métricas principales
col1, col2, col3 = st.columns(3)
col1.metric("Registros Filtrados", len(df_filtered))
col2.metric("pH Promedio", round(df_filtered[col_ph].mean(), 2) if len(df_filtered) > 0 and pd.api.types.is_numeric_dtype(df_filtered[col_ph]) else 0)
col3.metric("Carbono Total Promedio", round(df_filtered[col_carb].mean(), 2) if len(df_filtered) > 0 and pd.api.types.is_numeric_dtype(df_filtered[col_carb]) else 0)

st.divider()

# Sección de gráficos interactivos
st.subheader("📊 Gráficos Dinámicos")

c1, c2 = st.columns(2)

with c1:
    st.markdown("### Actividad Enzimática vs Etapa")
    fig, ax = plt.subplots(figsize=(6, 4))
    if len(df_filtered) > 0:
        sns.boxplot(data=df_filtered, x=col_etapa, y=col_enzima, palette='Set2', ax=ax)
    ax.set_title("Actividad Enzimática")
    ax.set_xlabel("Etapa")
    ax.set_ylabel("Enzima")
    plt.xticks(rotation=15)
    st.pyplot(fig)

with c2:
    st.markdown("### Relación pH vs Carbono Total")
    fig, ax = plt.subplots(figsize=(6, 4))
    if len(df_filtered) > 0:
        sns.scatterplot(data=df_filtered, x=col_ph, y=col_carb, hue=col_tratamiento, palette='viridis', ax=ax)
    ax.set_title("pH vs Carbono Total")
    ax.set_xlabel("pH")
    ax.set_ylabel("Carbono Total")
    st.pyplot(fig)

# Tabla de datos
st.subheader("📋 Vista previa de los datos filtrados")
st.dataframe(df_filtered.head(15))
