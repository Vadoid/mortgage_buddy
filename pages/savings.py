import streamlit as st
import pandas as pd
import locale

# Set the locale to the user's default setting (for number formatting)
locale.setlocale(locale.LC_ALL, '')

# Set page layout to wide
st.set_page_config(page_title="Mortgage Buddy", layout="wide")

def calculate_compound_interest(principal, annual_rate, inflation_rate, years):
    data = []
    total_balance = principal
    for year in range(1, years + 1):
        interest_accrued = total_balance * (annual_rate / 100)
        inflation_adjustment = total_balance * (inflation_rate / 100)
        total_balance += (interest_accrued - inflation_adjustment)
        data.append({
            'Year': year,
            'Interest Accrued': round(interest_accrued, 2),
            'Inflation Adjustment': round(inflation_adjustment, 2),
            'Running Balance': round(total_balance, 2)
        })
    return pd.DataFrame(data)

# Initialize session state variables
session_state_defaults = {
    'total_principal_paid_without_additional': 0,
    'total_interest_paid_without_additional': 0,
    'total_principal_paid_with_additional': 0,
    'total_interest_paid_with_additional': 0,
    'additional_repayment': 0,
    'new_rate': 0,
    'new_rate_date': None,
    'end_date_without_additional': None,
    'end_date_with_additional': None,
    'total_monthly_payment_with_additional': 0,
    'lump_sum': 0,
    'years_left': 30,
    'savings_period': 30
}

for key, value in session_state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

st.title("Savings")

col1, col2 = st.columns(2)

with col1:
    st.write("## Savings Calculator")
    savings_amount_input = st.text_input("Amount of Savings", value='1,000')
    try:
        savings_amount = locale.atof(savings_amount_input.replace(',', ''))
    except ValueError:
        st.error("Please enter a valid number for the Amount of Savings.")
        savings_amount = 0

    annual_return_rate = st.number_input("Average Annual Return Rate (%)", min_value=0.0, value=5.0, step=0.1)
    inflation_rate = st.number_input("Average Inflation Prediction (%)", min_value=0.0, value=2.0, step=0.1)
    savings_period = st.number_input("Period of Savings (years)", min_value=1, value=st.session_state['savings_period'], step=1)
    
    use_mortgage_period = st.checkbox("Use Mortgage Period", help="If checked, the period of savings will match the mortgage period.")
    
    if use_mortgage_period:
        savings_period = st.session_state['years_left']
        st.session_state['savings_period'] = savings_period
        st.write(f"Using mortgage period: {savings_period} years")
    
    if st.button("Calculate Savings"):
        st.session_state['savings_period'] = savings_period  # Ensure the period is correctly saved
        savings_data = calculate_compound_interest(savings_amount, annual_return_rate, inflation_rate, savings_period)
        total_interest = savings_data['Interest Accrued'].sum()
        total_balance = savings_data['Running Balance'].iloc[-1]
        st.write(f"Total interest accrued over the period: {total_interest:,.2f}")
        st.write(f"Total balance (savings + interest - inflation adjustment) at the end of the period: {total_balance:,.2f}")
        st.write(savings_data)

with col2:
    st.write("## Mortgage Savings Summary")
    st.write(f"**Total Principal Paid (Old):** {st.session_state['total_principal_paid_without_additional']:,.2f}")
    st.write(f"**Total Interest Paid (Old):** {st.session_state['total_interest_paid_without_additional']:,.2f}")
    st.write(f"**Total Principal Paid (New):** {st.session_state['total_principal_paid_with_additional']:,.2f}")
    st.write(f"**Total Interest Paid (New):** {st.session_state['total_interest_paid_with_additional']:,.2f}")
    st.write(f"**Additional Repayment:** {st.session_state['additional_repayment']:,.2f}")
    st.write(f"**New Rate:** {st.session_state['new_rate']:.2f}%")
    st.write(f"**New Rate Date:** {st.session_state['new_rate_date']}")
    st.write(f"**End Date (Old):** {st.session_state['end_date_without_additional']}")
    st.write(f"**End Date (New):** {st.session_state['end_date_with_additional']}")
    st.write(f"**Monthly Payment (New):** {st.session_state['total_monthly_payment_with_additional']:,.2f}")
    st.write(f"**Lump Sum:** {st.session_state['lump_sum']:,.2f}")
