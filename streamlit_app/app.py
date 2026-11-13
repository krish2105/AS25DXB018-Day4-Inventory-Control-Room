"""Inventory Control Room – Streamlit dashboard (Krishna Mathur · AS25DXB018 · MAIB Sept 2025).
Run:  streamlit run streamlit_app/app.py        (from the repository root)
"""
import streamlit as st

from common import footer, header, load, setup

setup("Inventory Control Room")
d = load()

nav = st.navigation(
    [
        st.Page("pages/overview.py", title="Overview", icon=":material/dashboard:", default=True),
        st.Page("pages/abc_analysis.py", title="ABC Analysis", icon=":material/bar_chart:"),
        st.Page("pages/ai_models.py", title="AI Models", icon=":material/psychology:"),
        st.Page("pages/safety_stock.py", title="Safety Stock", icon=":material/shield:"),
        st.Page("pages/simulator.py", title="Service-Level Simulator", icon=":material/tune:"),
        st.Page("pages/before_after.py", title="Before vs After AI", icon=":material/compare_arrows:"),
    ]
)
header(d)
nav.run()
footer(d)
