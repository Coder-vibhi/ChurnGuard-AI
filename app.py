import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. Page Setup
st.set_page_config(page_title="ChurnGuard AI", layout="wide")

# 2. Title & Header
st.title("📊 ChurnGuard AI: Customer Retention Intelligence")
st.markdown("---")

# 3. Data Loading & "AI Engine" Simulation
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('churn_data.csv')
        
        # --- PRE-PROCESSING & DUMMY LOCATIONS ---
        us_states = ['CA', 'TX', 'FL', 'NY', 'PA', 'IL', 'OH', 'GA', 'NC', 'MI']
        np.random.seed(42) 
        df['State_Code'] = np.random.choice(us_states, size=len(df))
        
        # Convert Churn to Numeric
        if 'Churn' in df.columns:
            df['Churn_Value'] = df['Churn'].apply(lambda x: 1 if x == 'Yes' else 0)

        # --- AI RISK SCORING (Simulated Logic for Demo) ---
        # Hum ek 'Risk Score' generate kar rahe hain (0 se 100)
        # Real world mein ye Machine Learning model se aata hai.
        # Logic: Agar Monthly Bill high hai aur Tenure kam hai, toh Risk high hai.
        
        df['Risk_Score'] = np.random.randint(10, 99, size=len(df))
        
        # Assign Risk Category based on Score
        def get_risk_category(score):
            if score > 80: return "High Risk 🔴"
            elif score > 50: return "Medium Risk 🟡"
            else: return "Low Risk 🟢"
            
        df['Risk_Category'] = df['Risk_Score'].apply(get_risk_category)
            
        return df
        
    except FileNotFoundError:
        return None

# Load Data
df = load_data()

if df is not None:
    
    # --- DASHBOARD SECTION 1: EXECUTIVE SUMMARY ---
    st.subheader("📉 Executive Summary")
    
    total_customers = len(df)
    churn_rate = (df['Churn_Value'].sum() / total_customers) * 100
    revenue_at_risk = df[df['Churn'] == 'Yes']['MonthlyCharges'].sum()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Gauge Chart
        fig_gauge = px.pie(values=[churn_rate, 100-churn_rate], names=["Churn", "Safe"], hole=0.7,
                           color_discrete_sequence=['red', 'lightgreen'], title="Overall Churn Rate %")
        fig_gauge.update_layout(showlegend=False, margin=dict(t=30, b=0, l=0, r=0), height=150)
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col2:
        # Big Numbers
        st.metric(label="🔥 Revenue at Risk", value=f"${revenue_at_risk:,.2f}")
        st.metric(label="Total Customers", value=f"{total_customers}")

    with col3:
        # Donut Chart
        churn_by_payment = df[df['Churn']=='Yes'].groupby('PaymentMethod').size().reset_index(name='Count')
        fig_donut = px.pie(churn_by_payment, values='Count', names='PaymentMethod', 
                           title="High Risk Payment Methods", hole=0.6)
        st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown("---")

    # --- DASHBOARD SECTION 2: GEOGRAPHIC MAP ---
    st.subheader("🗺️ Geographic Churn Hotspots (USA)")
    
    state_churn = df.groupby('State_Code')['Churn_Value'].mean().reset_index()
    state_churn.columns = ['State_Code', 'Churn_Rate']
    
    fig_map = px.choropleth(state_churn, 
                            locations='State_Code', 
                            locationmode="USA-states", 
                            color='Churn_Rate',
                            scope="usa",
                            color_continuous_scale="Reds",
                            title="Churn Intensity by State")
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("---")

    # --- DASHBOARD SECTION 3: AI DRILL-DOWN LIST (New Feature) ---
    st.subheader("📋 Customer Retention Action List")
    st.info("Select a Risk Category to see which customers need immediate attention.")

    # Filter Setup
    risk_filter = st.selectbox("Select Risk Level:", ["High Risk 🔴", "Medium Risk 🟡", "Low Risk 🟢"])
    
    # Filter Data based on selection
    filtered_df = df[df['Risk_Category'] == risk_filter]
    
    # Show only important columns
    display_columns = ['customerID', 'Risk_Category', 'Risk_Score', 'MonthlyCharges', 'Contract', 'PaymentMethod', 'State_Code']
    
    st.dataframe(filtered_df[display_columns], use_container_width=True)
    
    st.success(f"Showing {len(filtered_df)} customers in {risk_filter} category.")

else:
    st.error("🚨 Error: 'churn_data.csv' file not found.")