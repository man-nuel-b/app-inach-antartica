import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Configuración de la página en modo ancho (wide)
st.set_page_config(
    page_title="Visor Científico INACH RT_12_21",
    page_icon="❄️",
    layout="wide"
)

# Estilo visual general para los gráficos
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.sans-serif': 'Arial', 'font.size': 11})

# Título principal y contexto institucional
st.title("❄️ Proyecto INACH RT_12_21: Exploración Geoquímica y Enzimática en Suelos Antárticos")
st.markdown("Plataforma interactiva para la divulgación científica, análisis edáfico y evaluación de la cronosecuencia de deglaciación.")

# Carga de datos optimizada y cacheada
@st.cache_data
def load_data():
    # Carga el archivo Excel principal ubicado en el repositorio
    df = pd.read_excel('INACH_RT_12_21_quimica_suelo_enzimas_R_ready.xlsx', sheet_name=0)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error al cargar el archivo de datos: {e}")
    st.stop()

# ==========================================
# BARRA LATERAL: FILTROS DINÁMICOS
# ==========================================
st.sidebar.header("🎛️ Panel de Control y Filtros")

# Detección segura de columnas clave
col_etapa = 'etapa_deglaciacion' if 'etapa_deglaciacion' in df.columns else df.columns[1]
col_tratamiento = 'treatment_short' if 'treatment_short' in df.columns else df.columns[2]

# Filtro por Etapa de Deglaciación
opciones_etapa = df[col_etapa].dropna().unique()
etapa_sel = st.sidebar.multiselect(
    "Seleccione Etapa(s) de Deglaciación:",
    options=opciones_etapa,
    default=opciones_etapa
)

# Filtro por Tratamiento
opciones_tratamiento = df[col_tratamiento].dropna().unique()
tratamiento_sel = st.sidebar.multiselect(
    "Seleccione Tratamiento(s):",
    options=opciones_tratamiento,
    default=opciones_tratamiento
)

# Aplicar filtros al DataFrame
df_filtered = df[
    (df[col_etapa].isin(etapa_sel)) & 
    (df[col_tratamiento].isin(tratamiento_sel))
]

st.sidebar.markdown("---")
st.sidebar.info(f"Mostrando **{len(df_filtered)}** de **{len(df)}** registros totales.")

# ==========================================
# PESTAÑAS DE ANÁLISIS CIENTÍFICO
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Resumen General", 
    "🧪 Fisicoquímica (pH y C)", 
    "酶 Actividad Enzimática", 
    "📈 Correlaciones Estadísticas", 
    "📋 Tabla de Datos"
])

# --- TAB 1: RESUMEN GENERAL ---
with tab1:
    st.subheader("Indicadores Clave del Subconjunto Seleccionado")
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Muestras Analizadas", len(df_filtered))
    
    ph_col = 'ph_suelo' if 'ph_suelo' in df_filtered.columns else [c for c in df_filtered.columns if 'ph' in c.lower()][0]
    c_col = 'c_total_gkg' if 'c_total_gkg' in df_filtered.columns else [c for c in df_filtered.columns if 'c_total' in c.lower()][0]
    enz_col = 'beta_glucosidase_nmol_muf_g_h' if 'beta_glucosidase_nmol_muf_g_h' in df_filtered.columns else [c for c in df_filtered.columns if 'glucosidase' in c.lower()][0]

    prom_ph = df_filtered[ph_col].mean() if pd.api.types.is_numeric_dtype(df_filtered[ph_col]) else 0
    prom_c = df_filtered[c_col].mean() if pd.api.types.is_numeric_dtype(df_filtered[c_col]) else 0
    prom_enz = df_filtered[enz_col].mean() if pd.api.types.is_numeric_dtype(df_filtered[enz_col]) else 0

    col_m2.metric("pH Promedio", round(prom_ph, 2))
    col_m3.metric("Carbono Total Promedio (g/kg)", round(prom_c, 2))
    col_m4.metric("β-Glucosidasa Promedio", round(prom_enz, 2))

    st.divider()
    
    st.markdown("### 🗺️ Contexto del Proyecto")
    st.write(
        "Este panel interactivo recopila los resultados geoquímicos y enzimáticos de suelos antárticos "
        "evaluados en el marco del proyecto INACH RT_12_21. Utilice el panel lateral para aislar etapas "
        "de deglaciación específicas y contrastar los efectos de los tratamientos experimentales."
    )

# --- TAB 2: FISICOQUÍMICA ---
with tab2:
    st.subheader("Relación Fisicoquímica: pH y Carbono Total")
    
    c1, c2 = st.columns(2)
    with c1:
        fig, ax = plt.subplots(figsize=(7, 5))
        sns.scatterplot(
            data=df_filtered, x=ph_col, y=c_col, hue=col_tratamiento,
            palette='viridis', s=90, alpha=0.85, ax=ax
        )
        sns.regplot(
            data=df_filtered, x=ph_col, y=c_col, scatter=False,
            color='gray', line_kws={'linestyle':'--', 'linewidth':1.5}, ax=ax
        )
        ax.set_title("pH vs Carbono Total por Tratamiento", fontsize=12, fontweight='bold')
        ax.set_xlabel("pH del Suelo", fontsize=10, fontweight='bold')
        ax.set_ylabel("Carbono Total (g kg⁻¹)", fontsize=10, fontweight='bold')
        ax.legend(title='Tratamiento', bbox_to_anchor=(1.02, 1), loc='upper left')
        plt.tight_layout()
        st.pyplot(fig)

    with c2:
        fig, ax = plt.subplots(figsize=(7, 5))
        sns.boxplot(
            data=df_filtered, x=col_etapa, y=c_col, palette='Blues', ax=ax
        )
        ax.set_title("Distribución de Carbono Total por Etapa de Deglaciación", fontsize=12, fontweight='bold')
        ax.set_xlabel("Etapa de Deglaciación", fontsize=10, fontweight='bold')
        ax.set_ylabel("Carbono Total (g kg⁻¹)", fontsize=10, fontweight='bold')
        plt.xticks(rotation=15)
        plt.tight_layout()
        st.pyplot(fig)

# --- TAB 3: ACTIVIDAD ENZIMÁTICA ---
with tab3:
    st.subheader("Dinámica de Enzimas Edáficas en la Cronosecuencia")

    c1, c2 = st.columns(2)
    with c1:
        fig, ax = plt.subplots(figsize=(7, 5))
        sns.boxplot(
            data=df_filtered, x=col_etapa, y=enz_col, palette='Set2', ax=ax
        )
        sns.stripplot(
            data=df_filtered, x=col_etapa, y=enz_col, color='darkblue', alpha=0.5, jitter=0.2, size=5, ax=ax
        )
        ax.set_title("Actividad de β-Glucosidasa vs Etapa", fontsize=12, fontweight='bold')
        ax.set_xlabel("Etapa de Deglaciación", fontsize=10, fontweight='bold')
        ax.set_ylabel("β-Glucosidasa (nmol MUF g⁻¹ h⁻¹)", fontsize=10, fontweight='bold')
        plt.xticks(rotation=15)
        plt.tight_layout()
        st.pyplot(fig)

    with c2:
        fig, ax = plt.subplots(figsize=(7, 5))
        sns.violinplot(
            data=df_filtered, x=col_tratamiento, y=enz_col, palette='muted', inner='quartile', ax=ax
        )
        ax.set_title("Distribución Enzimática según Tratamiento", fontsize=12, fontweight='bold')
        ax.set_xlabel("Tratamiento", fontsize=10, fontweight='bold')
        ax.set_ylabel("β-Glucosidasa (nmol MUF g⁻¹ h⁻¹)", fontsize=10, fontweight='bold')
        plt.xticks(rotation=15)
        plt.tight_layout()
        st.pyplot(fig)

# --- TAB 4: CORRELACIONES ESTADÍSTICAS ---
with tab4:
    st.subheader("Matriz de Correlación Multivariada")
    st.write("Análisis estadístico de Pearson entre las principales variables fisicoquímicas y enzimáticas del estudio.")

    # Seleccionar solo columnas numéricas relevantes
    cols_num = df_filtered.select_dtypes(include=['float64', 'int64']).columns
    if len(cols_num) > 1:
        corr_matrix = df_filtered[cols_num].corr()
        
        fig, ax = plt.subplots(figsize=(9, 7))
        sns.heatmap(
            corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', vmin=-1, vmax=1,
            linewidths=0.5, cbar_kws={'label': 'Coeficiente de Correlación'}, ax=ax
        )
        ax.set_title("Matriz de Correlación de Pearson", fontsize=13, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.warning("No hay suficientes columnas numéricas para calcular la matriz de correlación con los filtros actuales.")

# --- TAB 5: TABLA DE DATOS ---
with tab5:
    st.subheader("Explorador de Datos Filtrados")
    st.write("Visualice y descargue la tabla de datos procesados según los criterios seleccionados en el panel lateral.")
    
    st.dataframe(df_filtered, use_container_width=True)
    
    # Botón de descarga en CSV
    csv_data = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar datos filtrados en formato CSV",
        data=csv_data,
        file_name="datos_inach_filtrados.csv",
        mime="text/csv"
    )
