import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Bettermin ERP", page_icon="🧬", layout="wide")

# Estilos CSS
st.markdown("""
<style>
    .main-header { font-size: 24px; font-weight: bold; color: #2E86C1; }
    .sub-header { font-size: 18px; font-weight: bold; color: #5D6D7E; }
    .metric-box { background-color: #F8F9F9; padding: 15px; border-radius: 10px; border-left: 5px solid #2E86C1; }
</style>
""", unsafe_allow_html=True)

# --- 2. GESTOR DE MONEDAS (SIDEBAR) ---
with st.sidebar:
    st.title("💱 Tipos de Cambio")
    st.info("Define el valor de las divisas para estandarizar todo a Pesos (CLP).")
    
    val_uf = st.number_input("Valor UF", value=39720.0, step=100.0)
    val_usd = st.number_input("Valor Dólar (USD)", value=940.0, step=5.0)
    val_eur = st.number_input("Valor Euro (EUR)", value=1020.0, step=5.0)
    val_gbp = st.number_input("Valor Libra (GBP)", value=1180.0, step=5.0)

    # Diccionario de conversión
    tasas = {"CLP": 1, "UF": val_uf, "USD": val_usd, "EUR": val_eur, "GBP": val_gbp}

# Función auxiliar para convertir a CLP
def convertir_a_clp(monto, moneda):
    return monto * tasas.get(moneda, 1)

def fmt(valor):
    return "${:,.0f}".format(valor).replace(",", ".")

# --- 3. MÓDULOS DE LA APLICACIÓN ---
st.title("🧬 Bettermin | Planificación Financiera Integral")
tab_costos_u, tab_gastos_f, tab_ventas, tab_dashboard = st.tabs([
    "1️⃣ Costo Unitario (La Receta)", 
    "2️⃣ Gastos Fijos (Nómina/Ops)", 
    "3️⃣ Proyección de Ingresos", 
    "4️⃣ Dashboard & Breakeven"
])

# ==========================================
# MÓDULO 1: COSTOS VARIABLES (UNITARIOS)
# ==========================================
with tab_costos_u:
    st.markdown("<div class='main-header'>Definición del Costo por Muestra</div>", unsafe_allow_html=True)
    st.caption("Ingresa aquí los componentes necesarios para procesar 1 sola muestra (Laboratorio, Insumos, Logística).")
    
    # Datos iniciales para la tabla
    data_costos_var = [
        {"Ítem": "Secuenciación (Lab Externo)", "Monto": 3.0, "Moneda": "UF", "Categoría": "Laboratorio"},
        {"Ítem": "Análisis Bioinformático", "Monto": 2.0, "Moneda": "UF", "Categoría": "Software"},
        {"Ítem": "Kit de Toma de Muestra", "Monto": 15.0, "Moneda": "USD", "Categoría": "Insumos"},
        {"Ítem": "Logística (Envío)", "Monto": 10000.0, "Moneda": "CLP", "Categoría": "Logística"},
    ]
    
    df_cv = pd.DataFrame(data_costos_var)
    
    # Editor de Costos Variables
    df_cv_editado = st.data_editor(
        df_cv,
        column_config={
            "Moneda": st.column_config.SelectboxColumn("Divisa", options=["CLP", "UF", "USD", "EUR", "GBP"], required=True),
            "Categoría": st.column_config.SelectboxColumn("Tipo", options=["Laboratorio", "Insumos", "Logística", "Software", "Comisión"]),
            "Monto": st.column_config.NumberColumn("Valor", min_value=0.0, format="%.2f")
        },
        num_rows="dynamic",
        use_container_width=True,
        key="editor_cv"
    )
    
    # Cálculo del Costo Unitario Total en CLP
    df_cv_editado["Total CLP"] = df_cv_editado.apply(lambda x: convertir_a_clp(x["Monto"], x["Moneda"]), axis=1)
    costo_unitario_total_clp = df_cv_editado["Total CLP"].sum()
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    c1.metric("Costo Total por Muestra (CLP)", fmt(costo_unitario_total_clp))
    c1.metric("Equivalente en UF", f"{costo_unitario_total_clp/val_uf:.2f} UF")
    
    with c2:
        fig_pie_cv = px.pie(df_cv_editado, values="Total CLP", names="Categoría", title="Desglose del Costo Variable")
        st.plotly_chart(fig_pie_cv, use_container_width=True)

# ==========================================
# MÓDULO 2: GASTOS FIJOS (OPERACIONALES)
# ==========================================
with tab_gastos_f:
    st.markdown("<div class='main-header'>Gastos Fijos & Nómina</div>", unsafe_allow_html=True)
    st.caption("Gastos recurrentes mensuales que NO dependen de la cantidad de muestras vendidas.")
    
    data_fijos = [
        {"Detalle": "Sueldo CEO", "Persona/Prov": "Fundador 1", "Monto": 2500000, "Moneda": "CLP", "Tipo": "Sueldos"},
        {"Detalle": "Sueldo CTO", "Persona/Prov": "Fundador 2", "Monto": 2500000, "Moneda": "CLP", "Tipo": "Sueldos"},
        {"Detalle": "Arriendo Oficina", "Persona/Prov": "WeWork", "Monto": 35.0, "Moneda": "UF", "Tipo": "Infraestructura"},
        {"Detalle": "Servidores AWS", "Persona/Prov": "Amazon", "Monto": 200.0, "Moneda": "USD", "Tipo": "Software/SaaS"},
        {"Detalle": "Contador", "Persona/Prov": "Estudio X", "Monto": 5.0, "Moneda": "UF", "Tipo": "Administrativo"},
    ]
    
    df_cf = pd.DataFrame(data_fijos)
    
    df_cf_editado = st.data_editor(
        df_cf,
        column_config={
            "Moneda": st.column_config.SelectboxColumn("Divisa", options=["CLP", "UF", "USD", "EUR", "GBP"]),
            "Tipo": st.column_config.SelectboxColumn("Área", options=["Sueldos", "Infraestructura", "Software/SaaS", "Administrativo", "Marketing"]),
            "Monto": st.column_config.NumberColumn("Valor", min_value=0.0)
        },
        num_rows="dynamic",
        use_container_width=True,
        key="editor_cf"
    )
    
    # Cálculo Total Fijos
    df_cf_editado["Total CLP"] = df_cf_editado.apply(lambda x: convertir_a_clp(x["Monto"], x["Moneda"]), axis=1)
    gasto_fijo_mensual_clp = df_cf_editado["Total CLP"].sum()
    
    st.info(f"💰 **Total Gastos Fijos Mensuales:** {fmt(gasto_fijo_mensual_clp)} (Este es tu 'Burn Rate' operativo sin costos de venta).")

# ==========================================
# MÓDULO 3: PROYECCIÓN DE VENTAS
# ==========================================
with tab_ventas:
    st.markdown("<div class='main-header'>Proyección de Ingresos y Crecimiento</div>", unsafe_allow_html=True)
    st.caption("Proyecta tus ventas mes a mes. Puedes ajustar el precio de venta y la cantidad de clientes.")

    col_conf, col_table = st.columns([1, 3])
    
    with col_conf:
        st.subheader("Parámetros de Venta")
        precio_venta_defecto_uf = st.number_input("Precio Base Servicio (UF)", value=15.4)
        precio_saas_defecto_usd = st.number_input("Precio Base Licencia SaaS (USD)", value=500.0)
        
        meses_proyeccion = 18
        lista_meses = [f"Mes {i}" for i in range(1, meses_proyeccion+1)]
    
    with col_table:
        # Estructura base de proyección
        data_proyeccion = {
            "Mes": lista_meses,
            "Cant. Muestras": [20 + (i*5) for i in range(meses_proyeccion)], # Crecimiento ficticio lineal
            "Precio Muestra (UF)": [precio_venta_defecto_uf] * meses_proyeccion,
            "Clientes SaaS (Recurrente)": [0,0,0,1,1,2,2,3,4,5,6,8,10,12,15,18,20,25],
            "Precio SaaS (USD)": [precio_saas_defecto_usd] * meses_proyeccion
        }
        
        df_ventas = pd.DataFrame(data_proyeccion)
        
        df_ventas_editado = st.data_editor(
            df_ventas,
            column_config={
                "Mes": st.column_config.TextColumn("Periodo", disabled=True),
                "Cant. Muestras": st.column_config.NumberColumn("Venta Muestras (Q)", min_value=0, step=1),
                "Clientes SaaS (Recurrente)": st.column_config.NumberColumn("Usuarios SaaS", min_value=0, step=1),
            },
            hide_index=True,
            use_container_width=True,
            height=400
        )

# ==========================================
# MÓDULO 4: CEREBRO FINANCIERO (CÁLCULOS)
# ==========================================

# 1. Calcular Ingresos Totales
df_ventas_editado["Ingresos Servicios (CLP)"] = df_ventas_editado["Cant. Muestras"] * df_ventas_editado["Precio Muestra (UF)"] * val_uf
df_ventas_editado["Ingresos SaaS (CLP)"] = df_ventas_editado["Clientes SaaS (Recurrente)"] * df_ventas_editado["Precio SaaS (USD)"] * val_usd
df_ventas_editado["Total Ingresos"] = df_ventas_editado["Ingresos Servicios (CLP)"] + df_ventas_editado["Ingresos SaaS (CLP)"]

# 2. Calcular Egresos Variables Totales
# Costo Unitario calculado en Modulo 1 * Cantidad Muestras
df_ventas_editado["Total Costo Variable"] = df_ventas_editado["Cant. Muestras"] * costo_unitario_total_clp

# 3. Calcular Egresos Fijos Totales
# Gasto Fijo calculado en Modulo 2 (constante para todos los meses, pero podrías hacerlo variable si quisieras)
df_ventas_editado["Total Costo Fijo"] = gasto_fijo_mensual_clp

# 4. Flujo Neto
df_ventas_editado["Egresos Totales"] = df_ventas_editado["Total Costo Variable"] + df_ventas_editado["Total Costo Fijo"]
df_ventas_editado["Flujo Neto"] = df_ventas_editado["Total Ingresos"] - df_ventas_editado["Egresos Totales"]
df_ventas_editado["Caja Acumulada"] = df_ventas_editado["Flujo Neto"].cumsum()


# ==========================================
# VISUALIZACIÓN DASHBOARD
# ==========================================
with tab_dashboard:
    st.markdown("<div class='main-header'>Tablero de Control y Breakeven</div>", unsafe_allow_html=True)
    
    # --- KPIs SUPERIORES ---
    k1, k2, k3, k4 = st.columns(4)
    
    ventas_totales = df_ventas_editado["Total Ingresos"].sum()
    ganancia_total = df_ventas_editado["Flujo Neto"].sum()
    caja_final = df_ventas_editado["Caja Acumulada"].iloc[-1]
    margen_neto_pct = (ganancia_total / ventas_totales * 100) if ventas_totales > 0 else 0
    
    k1.metric("Ventas Totales Proyectadas", fmt(ventas_totales))
    k2.metric("Flujo de Caja Final", fmt(caja_final), delta_color="normal")
    k3.metric("Margen Neto Global", f"{margen_neto_pct:.1f}%")
    
    # Cálculo Breakeven (Punto de Equilibrio)
    # BEQ = CF / (Precio - CV)
    precio_promedio_clp = precio_venta_defecto_uf * val_uf # Usamos el precio base configurado
    margen_contribucion = precio_promedio_clp - costo_unitario_total_clp
    
    if margen_contribucion > 0:
        beq_unidades = gasto_fijo_mensual_clp / margen_contribucion
        k4.metric("Punto Equilibrio (Mes)", f"{int(beq_unidades)} Muestras")
    else:
        k4.metric("Punto Equilibrio", "N/A (Margen Negativo)")
        st.error("🚨 TU COSTO VARIABLE SUPERA TU PRECIO DE VENTA. Revisa el Módulo 1.")

    st.markdown("---")
    
    # --- GRÁFICOS ---
    c_graf1, c_graf2 = st.columns([2, 1])
    
    with c_graf1:
        st.subheader("🌊 Evolución del Flujo de Caja")
        fig_flow = go.Figure()
        
        # Barras de Ingresos y Egresos
        fig_flow.add_trace(go.Bar(x=df_ventas_editado["Mes"], y=df_ventas_editado["Total Ingresos"], name="Ingresos", marker_color='#2ECC71'))
        fig_flow.add_trace(go.Bar(x=df_ventas_editado["Mes"], y=df_ventas_editado["Egresos Totales"], name="Egresos", marker_color='#E74C3C'))
        
        # Línea de Caja
        fig_flow.add_trace(go.Scatter(x=df_ventas_editado["Mes"], y=df_ventas_editado["Caja Acumulada"], name="Caja Acumulada", yaxis="y2", line=dict(color='#2E86C1', width=3)))
        
        fig_flow.update_layout(
            barmode='group',
            yaxis=dict(title="Flujo Mensual (CLP)"),
            yaxis2=dict(title="Acumulado (CLP)", overlaying="y", side="right"),
            legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig_flow, use_container_width=True)
        
    with c_graf2:
        st.subheader("🎯 Interpretación Breakeven")
        
        # Gráfico Termómetro de Ventas vs Equilibrio
        promedio_ventas_actual = df_ventas_editado["Cant. Muestras"].mean()
        
        fig_guage = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = promedio_ventas_actual,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Promedio Ventas vs Meta"},
            delta = {'reference': beq_unidades, 'increasing': {'color': "green"}},
            gauge = {
                'axis': {'range': [None, beq_unidades * 2], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#2E86C1"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, beq_unidades], 'color': "#FFEBEE"},
                    {'range': [beq_unidades, beq_unidades*2], 'color': "#E8F8F5"}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': beq_unidades}}))
        
        st.plotly_chart(fig_guage, use_container_width=True)
        
        st.info(f"""
        **Análisis:**
        Para cubrir tus costos fijos de **{fmt(gasto_fijo_mensual_clp)}**, necesitas vender **{int(beq_unidades)} muestras** al mes.
        
        Actualmente estás proyectando un promedio de **{int(promedio_ventas_actual)} muestras**.
        """)

    # --- TABLA DE DETALLE ---
    with st.expander("Ver Tabla Financiera Detallada (Descargable)"):
        st.dataframe(df_ventas_editado)
        csv = df_ventas_editado.to_csv(index=False).encode('utf-8')
        st.download_button("Descargar CSV", data=csv, file_name="flujo_bettermin_pro.csv")
        # ... (Tu código anterior termina en tab_dashboard)

# Agregar una nueva pestaña al inicio
tab_costos_u, tab_gastos_f, tab_ventas, tab_dashboard, tab_escenarios = st.tabs([
    "1️⃣ Costo Unitario", 
    "2️⃣ Gastos Fijos", 
    "3️⃣ Proyección", 
    "4️⃣ Dashboard",
    "5️⃣ Simulador de Riesgo" # NUEVO
])

# ... (El código de las pestañas 1 a 4 se mantiene igual) ...

# ==========================================
# MÓDULO 5: SIMULADOR DE ESCENARIOS (RIESGO)
# ==========================================
with tab_escenarios:
    st.markdown("<div class='main-header'>Simulación de Escenarios (Stress Test)</div>", unsafe_allow_html=True)
    st.caption("Compara cómo se comportaría tu caja ante situaciones extremas sin modificar tu plan base.")
    
    col_sim1, col_sim2 = st.columns([1, 3])
    
    with col_sim1:
        st.subheader("Configurar Escenarios")
        
        # Escenario Pesimista
        st.markdown("🔴 **Escenario Pesimista**")
        p_ventas_down = st.slider("Caída de Ventas (%)", 0, 90, 30, help="Vendes X% menos de lo planeado")
        p_costos_up = st.slider("Aumento de Costos (%)", 0, 100, 20, help="Tus costos fijos suben X%")
        
        # Escenario Optimista
        st.markdown("🟢 **Escenario Optimista**")
        o_ventas_up = st.slider("Aumento de Ventas (%)", 0, 200, 50)
        
    with col_sim2:
        # Calcular vectores
        flujo_base = df_ventas_editado["Caja Acumulada"].values
        
        # Pesimista: Ingresos bajan, Egresos Fijos suben
        ingresos_pesimista = df_ventas_editado["Total Ingresos"].values * (1 - p_ventas_down/100)
        egresos_fijos_pesimista = df_ventas_editado["Total Costo Fijo"].values * (1 + p_costos_up/100)
        egresos_totales_pesimista = df_ventas_editado["Total Costo Variable"].values * (1 - p_ventas_down/100) + egresos_fijos_pesimista
        flujo_pesimista = np.cumsum(ingresos_pesimista - egresos_totales_pesimista)
        
        # Optimista: Ingresos suben
        ingresos_optimista = df_ventas_editado["Total Ingresos"].values * (1 + o_ventas_up/100)
        egresos_totales_optimista = df_ventas_editado["Total Costo Variable"].values * (1 + o_ventas_up/100) + df_ventas_editado["Total Costo Fijo"].values
        flujo_optimista = np.cumsum(ingresos_optimista - egresos_totales_optimista)
        
        # Gráfico Comparativo
        fig_scenarios = go.Figure()
        
        # Base
        fig_scenarios.add_trace(go.Scatter(x=df_ventas_editado["Mes"], y=flujo_base, name="Plan Base", line=dict(color='blue', width=4)))
        
        # Pesimista
        fig_scenarios.add_trace(go.Scatter(x=df_ventas_editado["Mes"], y=flujo_pesimista, name=f"Pesimista (Ventas -{p_ventas_down}%)", line=dict(color='red', width=2, dash='dash')))
        
        # Optimista
        fig_scenarios.add_trace(go.Scatter(x=df_ventas_editado["Mes"], y=flujo_optimista, name=f"Optimista (Ventas +{o_ventas_up}%)", line=dict(color='green', width=2, dash='dot')))
        
        # Zona de peligro (Cero)
        fig_scenarios.add_hline(y=0, line_color="black", annotation_text="Quiebra de Caja")
        
        fig_scenarios.update_layout(title="Proyección de Caja: Comparativa de Escenarios", hovermode="x unified")
        st.plotly_chart(fig_scenarios, use_container_width=True)
        
        # Conclusiones Automáticas
        final_pesimista = flujo_pesimista[-1]
        
        if final_pesimista < 0:
            st.error(f"⚠️ **RIESGO ALTO:** En el escenario pesimista, la empresa quiebra. Terminas con deuda de {fmt(final_pesimista)}.")
        else:
            st.success(f"🛡️ **SOLIDEZ:** Incluso en el peor escenario configurado, la empresa sobrevive con {fmt(final_pesimista)} en caja.")