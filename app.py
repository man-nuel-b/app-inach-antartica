import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Visor Científico INACH RT_12_21",
    page_icon="❄️",
    layout="wide"
)

# Encabezado principal limpio y profesional
st.title("❄️ Explorador Geoquémico y Enzimático - Antártica")
st.markdown("### Proyecto INACH RT_12_21 | Monitoreo de Suelos y Cronosecuencia de Deglaciación")
st.markdown("---")

# Carga de datos optimizada y cacheada
@st.cache_data
def load_data():
    return pd.read_excel('INACH_RT_12_21_quimica_suelo_enzimas_R_ready.xlsx', sheet_name=0)

try:
    df = load_data()
except Exception as e:
    st.error(f"No se pudo cargar el archivo de datos: {e}")
    st.stop()

# ==========================================
# BARRA LATERAL: FILTROS INTUITIVOS
# ==========================================
st.sidebar.header("🎛️ Panel de Control")
st.sidebar.markdown("Filtre los datos para actualizar en tiempo real todas las vistas y gráficos.")

# Detección segura de columnas clave
col_etapa = 'etapa_deglaciacion' if 'etapa_deglaciacion' in df.columns else df.columns[1]
col_tratamiento = 'treatment_short' if 'treatment_short' in df.columns else df.columns[2]

# Filtro por Etapa de Deglaciación
opciones_etapa = df[col_etapa].dropna().unique()
etapa_sel = st.sidebar.multiselect(
    "1️⃣ Seleccione Etapa de Deglaciación:",
    options=opciones_etapa,
    default=opciones_etapa
)

# Filtro por Tratamiento
opciones_tratamiento = df[col_tratamiento].dropna().unique()
tratamiento_sel = st.sidebar.multiselect(
    "2️⃣ Seleccione Tratamiento:",
    options=opciones_tratamiento,
    default=opciones_tratamiento
)

# Aplicar filtros
df_filtered = df[
    (df[col_etapa].isin(etapa_sel)) & 
    (df[col_tratamiento].isin(tratamiento_sel))
]

st.sidebar.markdown("---")
st.sidebar.caption(f"📊 Mostrando **{len(df_filtered)}** registros de **{len(df)}** totales.")

# ==========================================
# PESTAÑAS PRINCIPALES
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Resumen y Métricas", 
    "🧪 Fisicoquímica (pH y Carbono)", 
    "酶 Actividad Enzimática", 
    "📈 Correlaciones Clave", 
    "📋 Base de Datos"
])

# Identificar columnas numéricas clave de forma segura
ph_col = 'ph_suelo' if 'ph_suelo' in df.columns else [c for c in df.columns if 'ph' in c.lower()][0]
c_col = 'c_total_gkg' if 'c_total_gkg' in df.columns else [c for c in df.columns if 'c_total' in c.lower()][0]
enz_col = 'beta_glucosidase_nmol_muf_g_h' if 'beta_glucosidase_nmol_muf_g_h' in df.columns else [c for c in df.columns if 'glucosidase' in c.lower()][0]

# --- TAB 1: RESUMEN Y MÉTRICAS ---
with tab1:
    st.markdown("### 📊 Indicadores Globales de la Selección")
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Muestras Analizadas", len(df_filtered))
    
    prom_ph = df_filtered[ph_col].mean() if pd.api.types.is_numeric_dtype(df_filtered[ph_col]) else 0
    prom_c = df_filtered[c_col].mean() if pd.api.types.is_numeric_dtype(df_filtered[c_col]) else 0
    prom_enz = df_filtered[enz_col].mean() if pd.api.types.is_numeric_dtype(df_filtered[enz_col]) else 0

    col_m2.metric("pH Promedio", round(prom_ph, 2))
    col_m3.metric("Carbono Total Promedio", f"{round(prom_c, 2)} g/kg")
    col_m4.metric("β-Glucosidasa Promedio", round(prom_enz, 2))

    st.markdown("---")
    st.info(
        "💡 **Guía para la Exposición:** Este panel web interactivo permite explorar cómo evoluciona "
        "la química del suelo y la actividad microbiana a lo largo del retroceso de los glaciares en la Antártica. "
        "**Pase el cursor sobre los gráficos dinámicos** de las siguientes pestañas para ver los detalles de cada muestra."
    )

# --- TAB 2: FISICOQUÍMICA ---
with tab2:
    st.markdown("### 🧪 Dinámica Fisicoquímica del Suelo Antártico (Dinámico)")
    
    c1, c2 = st.columns(2)
    with c1:
        if len(df_filtered) > 0:
            fig1 = px.scatter(
                df_filtered, x=ph_col, y=c_col, color=col_tratamiento,
                title="Relación pH vs Carbono Total",
                labels={ph_col: "pH del Suelo", c_col: "Carbono Total (g/kg)"},
                hover_data=df_filtered.columns[:3]
            )
            fig1.update_layout(template="plotly_white", margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning("No hay datos para mostrar con los filtros actual.")
        st.caption("🔍 **Interactividad:** Coloque el cursor sobre los puntos para inspeccionar muestras individuales.")

    with c2:
        if len(df_filtered) > 0:
            fig2 = px.box(
                df_filtered, x=col_etapa, y=c_col, color=col_etapa,
                title="Carbono Total por Etapa de Deglaciación",
                labels={col_etapa: "Etapa de Deglaciación", c_col: "Carbono Total (g/kg)"}
            )
            fig2.update_layout(template="plotly_white", showlegend=False, margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("No hay datos para mostrar.")
        st.caption("🔍 **Interactividad:** Visualice medianas y dispersión estadística al instante.")

# --- TAB 3: ACTIVIDAD ENZIMÁTICA ---
with tab3:
    st.markdown("### 酶 Actividad Enzimática (Capacidad Microbiana Dinámica)")

    c1, c2 = st.columns(2)
    with c1:
        if len(df_filtered) > 0:
            fig3 = px.box(
                df_filtered, x=col_etapa, y=enz_col, color=col_etapa,
                points="all",
                title="Actividad de β-Glucosidasa por Etapa",
                labels={col_etapa: "Etapa de Deglaciación", enz_col: "β-Glucosidasa (nmol MUF g⁻¹ h⁻¹)"}
            )
            fig3.update_layout(template="plotly_white", showlegend=False, margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.warning("No hay datos disponibles.")
        st.caption("🔍 **Interactividad:** Cada punto representa una muestra real con sus puntos atípicos visibles.")

    with c2:
        if len(df_filtered) > 0:
            fig4 = px.violin(
                df_filtered, x=col_tratamiento, y=enz_col, color=col_tratamiento,
                box=True, points="all",
                title="Distribución Enzimática por Tratamiento",
                labels={col_tratamiento: "Tratamiento", enz_col: "β-Glucosidasa (nmol MUF g⁻¹ h⁻¹)"}
            )
            fig4.update_layout(template="plotly_white", showlegend=False, margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.warning("No hay datos disponibles.")
        st.caption("🔍 **Interactividad:** Compara la densidad de distribución de la enzima por tratamiento.")

# --- TAB 4: CORRELACIONES CLAVE ---
with tab4:
    st.markdown("### 📈 Matriz de Correlación Interactiva")
    st.markdown("Análisis estadístico de las relaciones directas entre propiedades fisicoquímicas y enzimáticas.")

    candidatas_corr = [ph_col, c_col, enz_col, 'n_total_gkg', 'cn_ratio', 'conductivity_us_cm']
    cols_corr = [c for c in candidatas_corr if c in df_filtered.columns and pd.api.types.is_numeric_dtype(df_filtered[c])]
    
    if len(cols_corr) > 1:
        corr_matrix = df_filtered[cols_corr].corr()
        
        fig5 = px.imshow(
            corr_matrix, text_auto=".2f", aspect="auto",
            color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
            title="Matriz de Correlación de Pearson"
        )
        fig5.update_layout(template="plotly_white", margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig5, use_container_width=True)
        st.markdown("🔍 **Nota Didáctica:** Los gráficos de correlación Plotly permiten ver el valor exacto de Pearson al pasar el cursor por cada celda.")
    else:
        st.warning("No hay suficientes columnas numéricas disponibles.")

# --- TAB 5: BASE DE DATOS ---
with tab5:
    st.markdown("### 📋 Explorador y Exportación de Datos")
    st.markdown("Tabla interactiva con los registros filtrados en tiempo real.")
    
    st.dataframe(df_filtered, use_container_width=True)
    
    csv_data = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar datos filtrados (CSV)",
        data=csv_data,
        file_name="datos_inach_filtrados.csv",
        mime="text/csv"
    )
