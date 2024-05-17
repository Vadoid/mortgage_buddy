import streamlit as st
import locale
from datetime import datetime
from calculations import calculate_mortgage_payments

# Set the locale to the user's default setting (for number formatting)
locale.setlocale(locale.LC_ALL, '')

def display_mortgage_details():
    st.header("Mortgage Details")
    interest_rate = st.number_input('Current Interest Rate (%)', min_value=0.0, value=3.5, step=0.1, help="Your current mortgage rate")
    years_left = st.number_input('Time Left on Mortgage (years)', min_value=1, value=30, step=1)
    st.session_state['years_left'] =  years_left
    balance_input = st.text_input('Current Mortgage Balance', value='250,000')

    # Optional values container
    with st.container():
        st.subheader("Optional values")
        current_value = st.text_input('Current Value of the Property (optional)')
        # Calculate LTV if current value is provided
        if current_value:
            try:
                current_value_num = locale.atof(current_value.replace(',', ''))
                balance = locale.atof(balance_input.replace(',', ''))
                ltv = (balance / current_value_num) * 100
                st.write(f"Loan-to-Value (LTV): **{ltv:.2f}%**")
            except ValueError:
                st.error("Please enter a valid number for the Current Value of the Property.")
        start_date = st.date_input("Calculate from date (optional)", value=None, help="Optional date for calculations")



    if st.button('Calculate Mortgage Details'):
        try:
            balance = locale.atof(balance_input.replace(',', ''))
            if balance > 0:
                schedule, total_principal_paid, total_interest_paid, _ = calculate_mortgage_payments(interest_rate, years_left, balance, 0, 0, start_date)
                st.write('Monthly Mortgage Repayment Schedule:')
                st.dataframe(schedule)

                # Plot the data
                chart_data = schedule.set_index('Date')[['Principal Payment', 'Interest Payment', 'Total Payment']]
                st.line_chart(chart_data)

                st.session_state['years_left'] = years_left  # Save the years_left value in session state

            else:
                st.error("Current Mortgage Balance must be greater than 0.")
        except ValueError:
            st.error("Please enter a valid number for the Current Mortgage Balance.")
