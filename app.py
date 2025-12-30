import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import plotly.express as px

# 1. Page Config & Professional Styling
st.set_page_config(page_title="Lease Engine | WestProp & Terrace Africa", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e1e4e8; }
    .advice-box { background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #007bff; }
    .talking-points { background-color: #fff4e6; padding: 15px; border-radius: 10px; border: 1px dashed #fd7e14; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏢 Institutional Lease Negotiation Engine")
st.markdown("Decision Support for **WestProp Holdings** & **Terrace Africa** portfolios.")

# 2. Robust Model Loading
@st.cache_data
def load_and_train():
    try:
        df = pd.read_csv('data/historical_leases.csv')
        df_encoded = pd.get_dummies(df, columns=['Landlord', 'Asset_Class'])
        target = 'Final_Rent_psm'
        features = [col for col in df_encoded.columns if col not in [target, 'Lease_ID', 'NER_psm', 'Property_Name']]
        X = df_encoded[features]
        y = df_encoded[target]
        model = RandomForestRegressor(n_estimators=100, random_state=42).fit(X, y)
        return df, model, features
    except FileNotFoundError:
        st.error("Data file not found. Please run the generator in your notebook first.")
        st.stop()

df, model, feature_names = load_and_train()

# 3. Precision Synchronization Logic (Session State)
if 'rent_val' not in st.session_state: st.session_state.rent_val = 35.0
if 'vac_val' not in st.session_state: st.session_state.vac_val = 12.0

def sync_rent(): st.session_state.rent_val = st.session_state.rent_input
def sync_rent_slider(): st.session_state.rent_input = st.session_state.rent_val
def sync_vac(): st.session_state.vac_val = st.session_state.vac_input
def sync_vac_slider(): st.session_state.vac_input = st.session_state.vac_val

# --- SIDEBAR: PORTFOLIO DYNAMICS ---
st.sidebar.header("📝 Negotiation Parameters")
landlord_choice = st.sidebar.selectbox("Select Landlord", ["WestProp Holdings", "Terrace Africa"])

# PORTFOLIO MAPPING
if landlord_choice == "WestProp Holdings":
    tenant_options = ["Corporate HQ", "Diplomatic/NGO", "Luxury Boutique"]
    cap_rate = 0.075 
    brand_context = "Precinct"
else:
    tenant_options = ["Supermarket Anchor", "Line Shop", "QSR/Restaurant"]
    cap_rate = 0.105 
    brand_context = "Mall"

tenant_type = st.sidebar.selectbox("Tenant Type", tenant_options)
asset_choice = st.sidebar.selectbox("Asset Class", df[df['Landlord'] == landlord_choice]['Asset_Class'].unique())

st.sidebar.markdown("---")
st.sidebar.slider("Target Rent ($/sqm)", 10.0, 60.0, key='rent_val', on_change=sync_rent_slider)
st.sidebar.number_input("Enter Exact Rent:", 10.0, 60.0, key='rent_input', on_change=sync_rent, step=1.0)

st.sidebar.markdown("---")
st.sidebar.slider("Market Vacancy Rate (%)", 0.0, 20.0, key='vac_val', on_change=sync_vac_slider)
st.sidebar.number_input("Enter Exact Vacancy (%):", 0.0, 20.0, key='vac_input', on_change=sync_vac, step=1.0)

credit_in = st.sidebar.number_input("Tenant Credit Score", 300, 850, 750)
term_in = st.sidebar.selectbox("Lease Term (Months)", [12, 24, 36, 60, 120])

# NEW: WALE Meter in Sidebar
st.sidebar.markdown("---")
wale_score = (term_in / 120) 
st.sidebar.write(f"**Deal Stability (WALE Impact):** {term_in} Months")
st.sidebar.progress(min(wale_score, 1.0))

# --- 4. PREDICTION LOGIC WITH PORTFOLIO DIVERGENCE ---
input_df = pd.DataFrame(0, index=[0], columns=feature_names)
input_df['Starting_Ask_psm'] = st.session_state.rent_val * 1.15
input_df['Tenant_Credit'] = credit_in
input_df['Market_Vacancy'] = st.session_state.vac_val / 100
input_df['Lease_Term_Months'] = term_in

if f'Landlord_{landlord_choice}' in feature_names: input_df[f'Landlord_{landlord_choice}'] = 1
if f'Asset_Class_{asset_choice}' in feature_names: input_df[f'Asset_Class_{asset_choice}'] = 1

prediction = model.predict(input_df)[0]

# APPLY BRAND BEHAVIORS
if landlord_choice == "WestProp Holdings":
    prediction = prediction * (1.0 + (st.session_state.vac_val / 250))
    if tenant_type == "Diplomatic/NGO": prediction *= 1.10 
    fit_out_multiplier = 1.0
else:
    prediction = prediction * (1.0 - (st.session_state.vac_val / 150))
    if tenant_type == "Supermarket Anchor": 
        prediction *= 0.85 
        fit_out_multiplier = 2.5 
    else:
        fit_out_multiplier = 1.0

# VALUATION IMPACT
annual_rent = prediction * 12
asset_value_psm = annual_rent / cap_rate
target_value_psm = (st.session_state.rent_val * 12) / cap_rate
value_diff = asset_value_psm - target_value_psm

# --- STRATEGIC CONCESSION LOGIC ---
if credit_in > 750:
    rf_months = 0 if landlord_choice == "WestProp Holdings" else 1
    fit_out = (150 if (landlord_choice == "Terrace Africa") else 50) * fit_out_multiplier
else:
    rf_months = 2 if landlord_choice == "Terrace Africa" else 1
    fit_out = 25 * fit_out_multiplier

ner = ((prediction * (term_in - rf_months)) - fit_out) / term_in

# --- DASHBOARD DISPLAY ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Predicted Closing Rent", f"${prediction:.2f}/sqm", 
              delta=f"{((prediction/st.session_state.rent_val)-1)*100:.1f}% vs Target")
with col2:
    st.metric("Net Effective Rent (NER)", f"${ner:.2f}/sqm")
with col3:
    st.metric("Asset Value Impact", f"${value_diff:,.2f}", 
              delta=f"{'Value Added' if value_diff >= 0 else 'Value Lost'} (psm)")

st.divider()

# --- EXECUTIVE RECOMMENDATION ---
st.subheader("📋 Executive Lease Recommendation")
st.markdown(f"""
<div class="advice-box">
    <strong>Strategic Summary for {landlord_choice} Leasing Committee:</strong><br><br>
    The engine suggests a contract rent of <strong>${prediction:.2f}/sqm</strong> for this <strong>{tenant_type}</strong>. 
    To protect the building valuation of <strong>${asset_value_psm:,.2f}/sqm</strong>, structure the deal with:
    <ul>
        <li><strong>{rf_months} Months Rent-Free</strong></li>
        <li><strong>${fit_out:.2f}/sqm Fit-out Contribution</strong></li>
    </ul>
    <em>Rationale: Securing this {tenant_type} preserves the exit yield of {cap_rate*100}%.</em>
</div>
""", unsafe_allow_html=True)

# --- NEGOTIATION SCRIPT ---
st.markdown("### 🗣️ Negotiation Script")
if landlord_choice == "WestProp Holdings":
    st.info(f"💬 'Our premium positioning at {asset_choice} justifies this rate. We are providing a fit-out allowance to support your move-in while maintaining the {brand_context} integrity.'")
else:
    st.info(f"💬 'We recognize current retail conditions. By offering {rf_months} months of relief, we are investing in your business's launch at our {brand_context}.'")

st.divider()

# --- VISUAL ANALYTICS ---
c1, c2 = st.columns(2)
with c1:
    st.subheader(f"Strategy Sensitivity: {landlord_choice}")
    credits = np.linspace(400, 850, 15)
    sim_results = [model.predict(input_df.assign(Tenant_Credit=c))[0] for c in credits]
    if landlord_choice == "WestProp Holdings":
        sim_results = [r * (1.0 + (st.session_state.vac_val / 250)) for r in sim_results]
    else:
        sim_results = [r * (1.0 - (st.session_state.vac_val / 150)) for r in sim_results]
    sim_df = pd.DataFrame({'Tenant Credit': credits, 'Predicted Rent': sim_results})
    fig = px.line(sim_df, x='Tenant Credit', y='Predicted Rent', template="plotly_white", 
                  color_discrete_sequence=['#1f77b4' if landlord_choice == "WestProp Holdings" else '#ff7f0e'])
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Historical Yield Benchmarking")
    fig2 = px.scatter(df[df['Landlord'] == landlord_choice], x='Tenant_Credit', y='Final_Rent_psm', 
                      color='Asset_Class', trendline="ols", template="plotly_white")
    st.plotly_chart(fig2, use_container_width=True)

# NEW: MARKET STRESS TEST TABLE
st.divider()
st.subheader("📉 Market Stress Test (Vacancy Sensitivity)")
vacancy_steps = [0.0, 0.05, 0.10, 0.15, 0.20]
stress_results = []

for v in vacancy_steps:
    temp_df = input_df.copy()
    temp_df['Market_Vacancy'] = v
    raw_p = model.predict(temp_df)[0]
    if landlord_choice == "WestProp Holdings":
        p = raw_p * (1.0 + (v * 100 / 250))
        if tenant_type == "Diplomatic/NGO": p *= 1.10
    else:
        p = raw_p * (1.0 - (v * 100 / 150))
        if tenant_type == "Supermarket Anchor": p *= 0.85
    stress_results.append({"Vacancy %": f"{int(v*100)}%", "Predicted Rent": f"${p:.2f}"})

stress_df = pd.DataFrame(stress_results)
st.table(stress_df.set_index('Vacancy %').T)