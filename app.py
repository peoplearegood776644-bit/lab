import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from CoolProp.CoolProp import PropsSI

# ==========================================
# 1. CORE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(page_title="Pro-Thermo Engine", layout="wide")

def local_css():
    st.markdown("""
        <style>
        .stMetric { background-color: #ffffff; border: 1px solid #e0e0e0; padding: 15px; border-radius: 8px; }
        h1, h2 { color: #1e3a8a; }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. THERMODYNAMIC ENGINE CLASS
# ==========================================
class ThermodynamicEngine:
    """Industrial-grade engine for state and cycle numerical solving."""
    
    def __init__(self, fluid):
        self.fluid = fluid

    @st.cache_data
    def compute_state(_self, p, t):
        """High-precision lookup using CoolProp [1]."""
        try:
            return {
                "Pressure (Pa)": p, "Temperature (K)": t,
                "Enthalpy (J/kg)": PropsSI('H', 'P', p, 'T', t, _self.fluid),
                "Entropy (J/kgK)": PropsSI('S', 'P', p, 'T', t, _self.fluid),
                "Density (kg/m3)": PropsSI('D', 'P', p, 'T', t, _self.fluid)
            }
        except Exception as e:
            return {"Error": str(e)}

    def generate_saturation_dome(self):
        """Generates T-s coordinates for the fluid."""
        t_crit = PropsSI('T_critical', self.fluid)
        t_min = PropsSI('T_triple', self.fluid)
        t_range = np.linspace(t_min, t_crit - 0.1, 100)
        s_liq = [PropsSI('S', 'T', t, 'Q', 0, self.fluid)/1000 for t in t_range]
        s_vap = [PropsSI('S', 'T', t, 'Q', 1, self.fluid)/1000 for t in t_range]
        return t_range, s_liq, s_vap

# ==========================================
# 3. INTERACTIVE MODULES & UI
# ==========================================
def main():
    local_css()
    st.sidebar.title("🎛️ Analysis Controls")
    fluid = st.sidebar.selectbox("Fluid", ["Water", "Air", "CO2", "R134a"])
    engine = ThermodynamicEngine(fluid)
    
    st.header(f"📈 {fluid} Analysis")
    
    # State Solver
    st.subheader("📍 State Solver")
    col1, col2 = st.columns(2)
    p = col1.number_input("Pressure (Pa)", value=101325.0)
    t = col2.number_input("Temperature (K)", value=300.0)
    
    if st.button("Solve State"):
        result = engine.compute_state(p, t)
        st.json(result)

    # Visualization
    st.subheader("📊 Phase Envelope")
    t_dome, s_liq, s_vap = engine.generate_saturation_dome()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=s_liq, y=t_dome, name="Saturated Liquid"))
    fig.add_trace(go.Scatter(x=s_vap, y=t_dome, name="Saturated Vapor"))
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
