import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import math
from CoolProp.CoolProp import PropsSI

# ==========================================
# 1. PROFESSIONAL GLOBAL STYLING
# ==========================================
st.set_page_config(page_title="Industrial Thermo-Numerical Suite", layout="wide", page_icon="⚙️")

def apply_pro_styles():
    st.markdown("""
        <style>
        .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #f0f2f6; border: 1px solid #d1d5db; }
        .stButton>button:hover { background-color: #e2e8f0; border-color: #1e3a8a; }
        .stMetric { border: 1px solid #e2e8f0; padding: 15px; border-radius: 10px; background-color: #ffffff; }
        .sidebar .sidebar-content { background-image: linear-gradient(#1e3a8a,#1e3a8a); color: white; }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. SCIENTIFIC CALCULATOR MODULE
# ==========================================
def render_scientific_calculator():
    st.sidebar.markdown("---")
    st.sidebar.subheader("🧮 Scientific Calculator")
    
    # Expression Input
    expr = st.sidebar.text_input("Enter Expression (e.g., sin(0.5)*log(10))", value="sqrt(100) + 5")
    
    # Safe evaluation context with math functions
    calc_context = {
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "log": math.log, "log10": math.log10, "sqrt": math.sqrt,
        "pi": math.pi, "e": math.e, "pow": math.pow, "exp": math.exp
    }
    
    try:
        if expr:
            # Using eval with restricted globals for safety
            result = eval(expr, {"__builtins__": {}}, calc_context)
            st.sidebar.success(f"Result: {result:.6f}")
    except Exception as e:
        st.sidebar.error("Invalid Syntax")

# ==========================================
# 3. THERMODYNAMIC ENGINE
# ==========================================
class IndustrialSolver:
    def __init__(self, fluid):
        self.fluid = fluid

    def get_full_state(self, P, T):
        """Calculates 10+ properties for high-level numerical analysis."""
        try:
            return {
                "Enthalpy (h)": PropsSI('H', 'P', P, 'T', T, self.fluid) / 1000,
                "Entropy (s)": PropsSI('S', 'P', P, 'T', T, self.fluid) / 1000,
                "Internal Energy (u)": PropsSI('U', 'P', P, 'T', T, self.fluid) / 1000,
                "Density (rho)": PropsSI('D', 'P', P, 'T', T, self.fluid),
                "Quality (x)": PropsSI('Q', 'P', P, 'T', T, self.fluid),
                "Speed of Sound": PropsSI('A', 'P', P, 'T', T, self.fluid),
                "Viscosity": PropsSI('V', 'P', P, 'T', T, self.fluid),
            }
        except: return None

    def plot_ts_diagram(self, current_s, current_t):
        t_crit = PropsSI('T_critical', self.fluid)
        t_min = PropsSI('T_triple', self.fluid)
        temps = np.linspace(t_min, t_crit - 0.5, 100)
        s_liq = [PropsSI('S', 'T', t, 'Q', 0, self.fluid)/1000 for t in temps]
        s_vap = [PropsSI('S', 'T', t, 'Q', 1, self.fluid)/1000 for t in temps]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=s_liq, y=temps, name='Sat. Liquid', line=dict(color='#1e3a8a')))
        fig.add_trace(go.Scatter(x=s_vap, y=temps, name='Sat. Vapor', line=dict(color='#dc2626')))
        fig.add_trace(go.Scatter(x=[current_s], y=[current_t], mode='markers+text', 
                                 marker=dict(size=12, color='green'), text=["State Point"], textposition="top center"))
        
        fig.update_layout(title=f"T-s Diagram: {self.fluid}", template="simple_white",
                          xaxis_title="Entropy (kJ/kg-K)", yaxis_title="Temperature (K)")
        return fig

# ==========================================
# 4. MAIN APPLICATION INTERFACE
# ==========================================
def main():
    apply_pro_styles()
    st.title("🛡️ Pro-Grade Thermodynamic Solver")
    
    # Sidebar Navigation
    st.sidebar.header("Main Menu")
    fluid_list = ["Water", "Air", "R134a", "Ammonia", "CO2", "Methane", "Nitrogen"]
    selected_fluid = st.sidebar.selectbox("Select Industrial Fluid", fluid_list)
    
    # Inject Scientific Calculator into Sidebar
    render_scientific_calculator()

    # Layout: Solver & Viz
    solver = IndustrialSolver(selected_fluid)
    
    col_in, col_viz = st.columns([1, 2])
    
    with col_in:
        st.subheader("🛠️ State Inputs")
        p_in = st.number_input("Pressure (Pa)", value=101325.0, step=1000.0, format="%.2f")
        t_in = st.number_input("Temperature (K)", value=300.0, step=1.0, format="%.2f")
        
        if st.button("Solve Complex Numerical"):
            state = solver.get_full_state(p_in, t_in)
            if state:
                for label, val in state.items():
                    st.metric(label, f"{val:.4f}")
            else:
                st.error("State out of fluid bounds.")

    with col_viz:
        try:
            current_s = PropsSI('S', 'P', p_in, 'T', t_in, selected_fluid) / 1000
            st.plotly_chart(solver.plot_ts_diagram(current_s, t_in), use_container_width=True)
        except:
            st.info("Adjust inputs to view the T-s Diagram.")

    # High-Level Numerical Comparison Table
    st.markdown("---")
    st.subheader("📑 Comparative Property Grid")
    temps = [t_in - 10, t_in, t_in + 10]
    comparison_data = []
    for t in temps:
        res = solver.get_full_state(p_in, t)
        if res:
            res['Ref. Temp'] = t
            comparison_data.append(res)
    
    if comparison_data:
        st.table(pd.DataFrame(comparison_data).set_index('Ref. Temp'))

if __name__ == "__main__":
    main()
