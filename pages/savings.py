import streamlit as st
import pandas as pd
import locale

# Set the locale to the user's default setting (for number formatting)
locale.setlocale(locale.LC_ALL, '')

# Set page layout to wide
st.set_page_config(page_title="Mortgage Buddy", layout="wide")

def add_logo():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(https://raw.githubusercontent.com/Vadoid/mortgage_buddy/main/img/buddy.png);
                background-repeat: no-repeat;
                background-position: right;
                padding-top: 60px;
                background-size: 160px 150px;
                background-position: 20px 20px;
            }
            [data-testid="stSidebarNav"]::before {
                content: "";
                margin-left: 20px;
                margin-top: 20px;
                font-size: 30px;
                position: relative;
                top: 100px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
add_logo()

def calculate_compound_interest(principal, annual_rate, inflation_rate, years):
    data = []
    total_balance = principal
    for year in range(1, years + 1):
        interest_accrued = total_balance * (annual_rate / 100)

        if st.session_state.inflation_status == False:
            inflation_adjustment = 0
        else:
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
    'savings_period': 30,
    'years_left': 30,
    'inflation_status': False
}

for key, value in session_state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

#st.title("Savings")

col1, col2 = st.columns(2)

with col1:
    st.write("## Savings calculator")
    savings_amount_input = st.text_input("Amount of Savings", value='10,000')
    try:
        savings_amount = locale.atof(savings_amount_input.replace(',', ''))
    except ValueError:
        st.error("Please enter a valid number for the Amount of Savings.")
        savings_amount = 0

    annual_return_rate = st.number_input("Average Annual Return Rate (%)", min_value=0.0, value=5.0, step=0.1)
    inflation_rate = st.number_input("Average Inflation Prediction (%)", min_value=0.0, value=2.0, step=0.1)
    # Create a checkbox and update the session state based on its value
    st.session_state.inflation_status = st.checkbox('Include inflation', value=False, help="If checked, the inflationary effect would be used to calculate the 'real monetary value'")
    #savings_period = st.number_input("Period of Savings (years)", min_value=1, value=st.session_state['savings_period'], step=1)
    savings_period = st.number_input("Period of Savings (years)", min_value=1, value=st.session_state['years_left'], step=1)

    if st.button("Calculate Savings"):
        #savings_period = savingsperiod()
        savings_data = calculate_compound_interest(savings_amount, annual_return_rate, inflation_rate, savings_period)
        total_interest = savings_data['Interest Accrued'].sum()
        total_balance = savings_data['Running Balance'].iloc[-1]
        st.write(f"Total interest accrued over the period: {total_interest:,.2f}")
        st.write(f"Total balance (savings + interest - inflation adjustment) at the end of the period: {total_balance:,.2f}")
        st.write(savings_data)

with col2:
    # st.write("## Mortgage Summary")
    # st.write(f"**Total Principal Paid (Old):** {st.session_state['total_principal_paid_without_additional']:,.2f}")
    # st.write(f"**Total Interest Paid (Old):** {st.session_state['total_interest_paid_without_additional']:,.2f}")
    # st.write(f"**Total Principal Paid (New):** {st.session_state['total_principal_paid_with_additional']:,.2f}")
    # st.write(f"**Total Interest Paid (New):** {st.session_state['total_interest_paid_with_additional']:,.2f}")
    # st.write(f"**Additional Repayment:** {st.session_state['additional_repayment']:,.2f}")
    # st.write(f"**New Rate:** {st.session_state['new_rate']:.2f}%")
    # st.write(f"**New Rate Date:** {st.session_state['new_rate_date']}")
    # st.write(f"**End Date (Old):** {st.session_state['end_date_without_additional']}")
    # st.write(f"**End Date (New):** {st.session_state['end_date_with_additional']}")
    # st.write(f"**Monthly Payment (New):** {st.session_state['total_monthly_payment_with_additional']:,.2f}")
    # st.write(f"**Lump Sum:** {st.session_state['lump_sum']:,.2f}")
    st.markdown(
        """
        <div style="background-color: #f9f9f9; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
            <h2 style="color: #4e79a7;">Mortgage Summary</h2>
            <p style="font-size: 16px; color: #333;">
                <strong>Total Principal Paid (Old):</strong> {total_principal_paid_without_additional:,.2f} <br>
                <strong>Total Interest Paid (Old):</strong> {total_interest_paid_without_additional:,.2f} <br>
                <strong>Total Principal Paid (New):</strong> {total_principal_paid_with_additional:,.2f} <br>
                <strong>Total Interest Paid (New):</strong> {total_interest_paid_with_additional:,.2f} <br>
                <strong>Additional Repayment:</strong> {additional_repayment:,.2f} <br>
                <strong>New Rate:</strong> {new_rate:.2f}% <br>
                <strong>New Rate Date:</strong> {new_rate_date} <br>
                <strong>End Date (Old):</strong> {end_date_without_additional} <br>
                <strong>End Date (New):</strong> {end_date_with_additional} <br>
                <strong>Monthly Payment (New):</strong> {total_monthly_payment_with_additional:,.2f} <br>
                <strong>Lump Sum:</strong> {lump_sum:,.2f} <br>
            </p>
        </div>
        """.format(
            total_principal_paid_without_additional=st.session_state['total_principal_paid_without_additional'],
            total_interest_paid_without_additional=st.session_state['total_interest_paid_without_additional'],
            total_principal_paid_with_additional=st.session_state['total_principal_paid_with_additional'],
            total_interest_paid_with_additional=st.session_state['total_interest_paid_with_additional'],
            additional_repayment=st.session_state['additional_repayment'],
            new_rate=st.session_state['new_rate'],
            new_rate_date=st.session_state['new_rate_date'],
            end_date_without_additional=st.session_state['end_date_without_additional'],
            end_date_with_additional=st.session_state['end_date_with_additional'],
            total_monthly_payment_with_additional=st.session_state['total_monthly_payment_with_additional'],
            lump_sum=st.session_state['lump_sum']
        ),
        unsafe_allow_html=True
    )

