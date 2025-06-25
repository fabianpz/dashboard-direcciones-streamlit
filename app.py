import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Direcciones",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🗺️ Dashboard de Direcciones")
st.markdown("---")

# Sidebar para cargar archivo
st.sidebar.header("📁 Cargar Datos")
uploaded_file = st.sidebar.file_uploader(
    "Sube tu archivo Excel",
    type=['xlsx', 'xls'],
    help="Sube un archivo Excel con las direcciones"
)

# Función para cargar datos
@st.cache_data
def load_data(file):
    try:
        df = pd.read_excel(file)
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return None

# Función para procesar direcciones
def process_addresses(df):
    if df is None:
        return None
    
    # Detectar columnas que podrían contener direcciones
    address_columns = []
    for col in df.columns:
        if any(word in col.lower() for word in ['direccion', 'address', 'ubicacion', 'domicilio', 'calle']):
            address_columns.append(col)
    
    return address_columns

# Función para análisis de datos
def analyze_data(df):
    if df is None:
        return None
    
    analysis = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'columns': list(df.columns),
        'missing_values': df.isnull().sum().to_dict(),
        'data_types': df.dtypes.to_dict()
    }
    
    return analysis

# Main content
if uploaded_file is not None:
    # Cargar datos
    df = load_data(uploaded_file)
    
    if df is not None:
        # Tabs principales
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumen", "🗺️ Análisis Geográfico", "📈 Visualizaciones", "📋 Datos"])
        
        with tab1:
            st.header("📊 Resumen de Datos")
            
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total de Registros", f"{len(df):,}")
            
            with col2:
                st.metric("Columnas", len(df.columns))
            
            with col3:
                missing_count = df.isnull().sum().sum()
                st.metric("Datos Faltantes", f"{missing_count:,}")
            
            with col4:
                if len(df) > 0:
                    completeness = (1 - missing_count / (len(df) * len(df.columns))) * 100
                    st.metric("Completitud", f"{completeness:.1f}%")
            
            st.markdown("---")
            
            # Información de columnas
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📋 Información de Columnas")
                column_info = pd.DataFrame({
                    'Columna': df.columns,
                    'Tipo': df.dtypes.astype(str),
                    'Valores Únicos': [df[col].nunique() for col in df.columns],
                    'Valores Nulos': [df[col].isnull().sum() for col in df.columns]
                })
                st.dataframe(column_info, use_container_width=True)
            
            with col2:
                st.subheader("🔍 Posibles Columnas de Direcciones")
                address_cols = process_addresses(df)
                if address_cols:
                    for col in address_cols:
                        st.write(f"✅ **{col}**")
                        if len(df[col].dropna()) > 0:
                            st.write(f"   Ejemplo: {df[col].dropna().iloc[0]}")
                else:
                    st.write("No se detectaron columnas de direcciones automáticamente.")
                    st.write("Puedes seleccionar manualmente en la siguiente sección.")
        
        with tab2:
            st.header("🗺️ Análisis Geográfico")
            
            # Selector de columna de dirección
            address_columns = st.multiselect(
                "Selecciona las columnas que contienen direcciones:",
                options=df.columns.tolist(),
                default=process_addresses(df) if process_addresses(df) else []
            )
            
            if address_columns:
                for col in address_columns:
                    st.subheader(f"📍 Análisis de: {col}")
                    
                    # Estadísticas de la columna
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        total = len(df[col].dropna())
                        st.metric("Direcciones Válidas", total)
                    
                    with col2:
                        unique = df[col].nunique()
                        st.metric("Direcciones Únicas", unique)
                    
                    with col3:
                        duplicates = total - unique
                        st.metric("Direcciones Duplicadas", duplicates)
                    
                    # Análisis de patrones
                    st.write("**Análisis de Patrones:**")
                    
                    # Palabras más comunes
                    all_text = ' '.join(df[col].dropna().astype(str).str.lower())
                    common_words = pd.Series(all_text.split()).value_counts().head(10)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Palabras más comunes:**")
                        for word, count in common_words.items():
                            if len(word) > 2:  # Filtrar palabras muy cortas
                                st.write(f"- {word}: {count} veces")
                    
                    with col2:
                        # Gráfico de palabras comunes
                        fig = px.bar(
                            x=common_words.values[:5],
                            y=common_words.index[:5],
                            orientation='h',
                            title=f"Top 5 Palabras en {col}",
                            labels={'x': 'Frecuencia', 'y': 'Palabra'}
                        )
                        fig.update_layout(height=300)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Muestra de direcciones
                    st.write("**Muestra de direcciones:**")
                    sample_addresses = df[col].dropna().head(10)
                    for i, addr in enumerate(sample_addresses, 1):
                        st.write(f"{i}. {addr}")
                    
                    st.markdown("---")
            else:
                st.info("👆 Selecciona al menos una columna de direcciones para comenzar el análisis.")
        
        with tab3:
            st.header("📈 Visualizaciones")
            
            # Selector de columnas para visualizar
            numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
            categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
            
            if numeric_columns:
                st.subheader("📊 Datos Numéricos")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    selected_numeric = st.selectbox("Selecciona columna numérica:", numeric_columns)
                
                with col2:
                    chart_type = st.selectbox("Tipo de gráfico:", ["Histograma", "Box Plot", "Estadísticas"])
                
                if selected_numeric:
                    if chart_type == "Histograma":
                        fig = px.histogram(df, x=selected_numeric, title=f"Distribución de {selected_numeric}")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif chart_type == "Box Plot":
                        fig = px.box(df, y=selected_numeric, title=f"Box Plot de {selected_numeric}")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif chart_type == "Estadísticas":
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Estadísticas Descriptivas:**")
                            stats = df[selected_numeric].describe()
                            st.write(stats)
                        
                        with col2:
                            st.write("**Información Adicional:**")
                            st.write(f"- Valores únicos: {df[selected_numeric].nunique():,}")
                            st.write(f"- Valores nulos: {df[selected_numeric].isnull().sum():,}")
                            st.write(f"- Tipo de dato: {df[selected_numeric].dtype}")
            
            if categorical_columns:
                st.subheader("📋 Datos Categóricos")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    selected_categorical = st.selectbox("Selecciona columna categórica:", categorical_columns)
                
                with col2:
                    cat_chart_type = st.selectbox("Tipo de gráfico:", ["Barras", "Pie", "Tabla de Frecuencias"])
                
                if selected_categorical:
                    # Obtener frecuencias (limitando a top 20 para evitar gráficos muy grandes)
                    value_counts = df[selected_categorical].value_counts().head(20)
                    
                    if cat_chart_type == "Barras":
                        fig = px.bar(
                            x=value_counts.index,
                            y=value_counts.values,
                            title=f"Frecuencia de {selected_categorical}",
                            labels={'x': selected_categorical, 'y': 'Frecuencia'}
                        )
                        fig.update_xaxes(tickangle=45)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif cat_chart_type == "Pie":
                        fig = px.pie(
                            values=value_counts.values,
                            names=value_counts.index,
                            title=f"Distribución de {selected_categorical}"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif cat_chart_type == "Tabla de Frecuencias":
                        freq_table = pd.DataFrame({
                            selected_categorical: value_counts.index,
                            'Frecuencia': value_counts.values,
                            'Porcentaje': (value_counts.values / len(df) * 100).round(2)
                        })
                        st.dataframe(freq_table, use_container_width=True)
        
        with tab4:
            st.header("📋 Vista de Datos")
            
            # Opciones de filtrado
            st.subheader("🔍 Filtros")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                show_rows = st.slider("Número de filas a mostrar:", 10, len(df), min(100, len(df)))
            
            with col2:
                columns_to_show = st.multiselect(
                    "Columnas a mostrar:",
                    options=df.columns.tolist(),
                    default=df.columns.tolist()[:5]  # Mostrar primeras 5 por defecto
                )
            
            with col3:
                search_term = st.text_input("Buscar en los datos:")
            
            # Aplicar filtros
            display_df = df.copy()
            
            if columns_to_show:
                display_df = display_df[columns_to_show]
            
            if search_term:
                # Buscar en todas las columnas de texto
                mask = False
                for col in display_df.select_dtypes(include=['object']).columns:
                    mask |= display_df[col].astype(str).str.contains(search_term, case=False, na=False)
                display_df = display_df[mask]
            
            # Mostrar datos
            st.dataframe(display_df.head(show_rows), use_container_width=True)
            
            # Opción de descarga
            if st.button("📥 Descargar datos filtrados"):
                # Convertir a CSV
                csv = display_df.to_csv(index=False)
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv,
                    file_name=f"datos_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

else:
    # Página de inicio cuando no hay archivo cargado
    st.info("👆 **Sube un archivo Excel** en la barra lateral para comenzar el análisis.")
    
    # Instrucciones
    st.markdown("""
    ## 🚀 ¿Cómo usar este dashboard?
    
    1. **📁 Sube tu archivo Excel** usando el botón en la barra lateral
    2. **📊 Explora el resumen** de tus datos en la primera pestaña
    3. **🗺️ Analiza las direcciones** en la segunda pestaña
    4. **📈 Crea visualizaciones** en la tercera pestaña
    5. **📋 Revisa los datos** en la cuarta pestaña
    
    ## 📋 Formato recomendado para el archivo Excel:
    
    - Incluye headers/encabezados en la primera fila
    - Las columnas de direcciones pueden llamarse: `Dirección`, `Direccion`, `Address`, `Ubicación`, etc.
    - Guarda el archivo en formato `.xlsx` o `.xls`
    
    ## ✨ Características:
    
    - 📊 **Análisis automático** de datos
    - 🗺️ **Detección de direcciones**
    - 📈 **Visualizaciones interactivas**
    - 🔍 **Filtros y búsqueda**
    - 📥 **Descarga de resultados**
    """)

# Footer
st.markdown("---")
st.markdown("📊 **Dashboard de Direcciones** | Desarrollado con ❤️ usando Streamlit")
