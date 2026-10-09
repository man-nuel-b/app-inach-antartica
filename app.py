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

# Detección segura de columnas clave
col_etapa = 'etapa_deglaciacion' if 'etapa_deglaciacion' in df.columns else df.columns[1]
col_tratamiento = 'treatment_short' if 'treatment_short' in df.columns else df.columns[2]

ph_col = 'ph_suelo' if 'ph_suelo' in df.columns else [c for c in df.columns if 'ph' in c.lower()][0]
c_col = 'c_total_gkg' if 'c_total_gkg' in df.columns else [c for c in df.columns if 'c_total' in c.lower()][0]
enz_col = 'beta_glucosidase_nmol_muf_g_h' if 'beta_glucosidase_nmol_muf_g_h' in df.columns else [c for c in df.columns if 'glucosidase' in c.lower()][0]

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

# --- TAB 1: RESUMEN Y MÉTRICAS ---
with tab1:
    st.markdown("### 📊 Indicadores Globales del Proyecto")
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Muestras Totales", len(df))
    
    prom_ph = df[ph_col].mean() if pd.api.types.is_numeric_dtype(df[ph_col]) else 0
    prom_c = df[c_col].mean() if pd.api.types.is_numeric_dtype(df[c_col]) else 0
    prom_enz = df[enz_col].mean() if pd.api.types.is_numeric_dtype(df[enz_col]) else 0

    col_m2.metric("pH Promedio", round(prom_ph, 2))
    col_m3.metric("Carbono Total Promedio", f"{round(prom_c, 2)} g/kg")
    col_m4.metric("β-Glucosidasa Promedio", round(prom_enz, 2))

    st.markdown("---")
    st.info(
        "💡 **Guía de Exposición:** Este panel presenta la totalidad de los datos geoquímicos y enzimáticos "
        "del proyecto INACH RT_12_21. Utilice las pestañas superiores para navegar entre los gráficos interactivos de la presentación."
    )

# --- TAB 2: FISICOQUÍMICA ---
with tab2:
    st.markdown("### 🧪 Dinámica Fisicoquímica del Suelo Antártico")
    
    c1, c2 = st.columns(2)
    with c1:
        fig1 = px.scatter(
            df, x=ph_col, y=c_col, color=col_tratamiento,
            title="Relación pH vs Carbono Total",
            labels={ph_col: "pH del Suelo", c_col: "Carbono Total (g/kg)"}
        )
        fig1.update_layout(template="plotly_white", margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        fig2 = px.box(
            df, x=col_etapa, y=c_col, color=col_etapa,
            title="Carbono Total por Etapa de Deglaciación",
            labels={col_etapa: "Etapa de Deglaciación", c_col: "Carbono Total (g/kg)"}
        )
        fig2.update_layout(template="plotly_white", showlegend=False, margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig2, use_container_width=True)

# --- TAB 3: ACTIVIDAD ENZIMÁTICA ---
with tab3:
    st.markdown("### 酶 Actividad Enzimática (Capacidad Microbiana)")

    c1, c2 = st.columns(2)
    with c1:
        fig3 = px.box(
            df, x=col_etapa, y=enz_col, color=col_etapa,
            points="all",
            title="Actividad de β-Glucosidasa por Etapa",
            labels={col_etapa: "Etapa de Deglaciación", enz_col: "β-Glucosidasa (nmol MUF g⁻¹ h⁻¹)"}
        )
        fig3.update_layout(template="plotly_white", showlegend=False, margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig3, use_container_width=True)

    with c2:
        fig4 = px.violin(
            df, x=col_tratamiento, y=enz_col, color=col_tratamiento,
            box=True, points="all",
            title="Distribución Enzimática por Tratamiento",
            labels={col_tratamiento: "Tratamiento", enz_col: "β-Glucosidasa (nmol MUF g⁻¹ h⁻¹)"}
        )
        fig4.update_layout(template="plotly_white", showlegend=False, margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig4, use_container_width=True)

# --- TAB 4: CORRELACIONES CLAVE ---
with tab4:
    st.markdown("### 📈 Matriz de Correlación de Variables Esenciales")
    
    candidatas_corr = [ph_col, c_col, enz_col, 'n_total_gkg', 'cn_ratio', 'conductivity_us_cm']
    cols_corr = [c for c in candidatas_corr if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
    
    if len(cols_corr) > 1:
        corr_matrix = df[cols_corr].corr()
        
        fig5 = px.imshow(
            corr_matrix, text_auto=".2f", aspect="auto",
            color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
            title="Matriz de Correlación de Pearson"
        )
        fig5.update_layout(template="plotly_white", margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig5, use_container_width=True)

# --- TAB 5: BASE DE DATOS ---
with tab5:
    st.markdown("### 📋 Base de Datos Completa y Exportación")
    st.dataframe(df, use_container_width=True)
    
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar base de datos completa (CSV)",
        data=csv_data,
        file_name="datos_inach_completo.csv",
        mime="text/csv"
    )
