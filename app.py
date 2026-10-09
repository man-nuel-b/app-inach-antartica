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

# Filtros interactivos en la barra lateral
st.sidebar.header("🎛️ Filtros Dinámicos")
etapa_sel = st.sidebar.multiselect(
    "Seleccione Etapa de Deglaciación:", 
    options=df['etapa_deglaciacion'].unique(), 
    default=df['etapa_deglaciacion'].unique()
)
tratamiento_sel = st.sidebar.multiselect(
    "Seleccione Tratamiento:", 
    options=df['treatment_short'].unique(), 
    default=df['treatment_short'].unique()
)

# Filtrar dataframe según selección
df_filtered = df[
    (df['etapa_deglaciacion'].isin(etapa_sel)) & 
    (df['treatment_short'].isin(tratamiento_sel))
]

# Métricas principales
col1, col2, col3 = st.columns(3)
col1.metric("Registros Filtrados", len(df_filtered))
col2.metric("pH Promedio", round(df_filtered['ph_suelo'].mean(), 2) if len(df_filtered) > 0 else 0)
col3.metric("Carbono Total Promedio (g/kg)", round(df_filtered['c_total_gkg'].mean(), 2) if len(df_filtered) > 0 else 0)

st.divider()

# Sección de gráficos interactivos
st.subheader("📊 Gráficos Dinámicos")

c1, c2 = st.columns(2)

with c1:
    st.markdown("### Actividad de $\\beta$-Glucosidasa")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.boxplot(data=df_filtered, x='etapa_deglaciacion', y='beta_glucosidase_nmol_muf_g_h', palette='Set2', ax=ax)
    ax.set_title("Beta-Glucosidasa vs Etapa")
    ax.set_xlabel("Etapa de Deglaciación")
    ax.set_ylabel("nmol MUF g⁻¹ h⁻¹")
    plt.xticks(rotation=15)
    st.pyplot(fig)

with c2:
    st.markdown("### Relación pH vs Carbono Total")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.scatterplot(data=df_filtered, x='ph_suelo', y='c_total_gkg', hue='treatment_short', palette='viridis', ax=ax)
    ax.set_title("pH vs Carbono Total")
    ax.set_xlabel("pH del Suelo")
    ax.set_ylabel("Carbono Total (g kg⁻¹)")
    st.pyplot(fig)

# Tabla de datos
st.subheader("📋 Vista previa de los datos filtrados")
st.dataframe(df_filtered[['r_id', 'etapa_deglaciacion', 'treatment_short', 'ph_suelo', 'c_total_gkg', 'beta_glucosidase_nmol_muf_g_h']].head(15))
