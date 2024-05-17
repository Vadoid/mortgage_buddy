import streamlit as st
import pandas as pd
import locale
from datetime import datetime, timedelta

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
# Function to calculate mortgage repayments
def calculate_mortgage_payments(interest_rate, years_left, balance, additional_repayment=0, lump_sum=0, start_date=None, new_rate=None, new_rate_date=None):
    monthly_rate = interest_rate / 100 / 12  # Monthly interest rate
    num_payments = years_left * 12  # Total number of payments (months)

    if lump_sum > 0:
        balance -= lump_sum  # Apply lump sum payment

    if balance <= 0:
        raise ValueError("Lump sum payment exceeds mortgage balance.")

    if monthly_rate != 0:
        monthly_payment = balance * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
    else:
        monthly_payment = balance / num_payments
    total_monthly_payment = monthly_payment + additional_repayment

    schedule = []
    remaining_balance = balance

    if start_date is None:
        current_date = datetime.today()
    else:
        current_date = datetime.combine(start_date, datetime.min.time())

    total_principal_paid = 0
    total_interest_paid = 0

    if new_rate_date:
        new_rate_date = datetime.combine(new_rate_date, datetime.min.time())  # Ensure new_rate_date is datetime

    while remaining_balance > 0 and len(schedule) < num_payments:
        # Check if the new rate should be applied
        if new_rate and new_rate_date and current_date >= new_rate_date:
            monthly_rate = new_rate / 100 / 12
            remaining_months = num_payments - len(schedule)
            if remaining_months > 0:
                if monthly_rate != 0:
                    monthly_payment = remaining_balance * (monthly_rate * (1 + monthly_rate) ** remaining_months) / ((1 + monthly_rate) ** remaining_months - 1)
                else:
                    monthly_payment = remaining_balance / remaining_months
                total_monthly_payment = monthly_payment + additional_repayment

        interest_payment = remaining_balance * monthly_rate
        principal_payment = total_monthly_payment - interest_payment
        remaining_balance -= principal_payment

        if remaining_balance < 0:
            principal_payment += remaining_balance  # Adjust the principal payment to not exceed the remaining balance
            remaining_balance = 0

        total_principal_paid += principal_payment
        total_interest_paid += interest_payment

        schedule.append({
            'Date': current_date.strftime('%Y-%m'),
            'Principal Payment': round(principal_payment, 2),
            'Interest Payment': round(interest_payment, 2),
            'Total Payment': round(total_monthly_payment, 2),
            'Remaining Balance': round(remaining_balance, 2)
        })

        # Increment the month
        next_month = current_date.month + 1
        if next_month > 12:
            next_month = 1
            current_date = current_date.replace(year=current_date.year + 1)
        current_date = current_date.replace(month=next_month)

    return pd.DataFrame(schedule), total_principal_paid, total_interest_paid, total_monthly_payment

# Initialize session state variables
if 'total_principal_paid_without_additional' not in st.session_state:
    st.session_state['total_principal_paid_without_additional'] = 0
if 'total_interest_paid_without_additional' not in st.session_state:
    st.session_state['total_interest_paid_without_additional'] = 0
if 'total_principal_paid_with_additional' not in st.session_state:
    st.session_state['total_principal_paid_with_additional'] = 0
if 'total_interest_paid_with_additional' not in st.session_state:
    st.session_state['total_interest_paid_with_additional'] = 0
if 'additional_repayment' not in st.session_state:
    st.session_state['additional_repayment'] = 0
if 'new_rate' not in st.session_state:
    st.session_state['new_rate'] = 0
if 'new_rate_date' not in st.session_state:
    st.session_state['new_rate_date'] = None
if 'end_date_without_additional' not in st.session_state:
    st.session_state['end_date_without_additional'] = None
if 'end_date_with_additional' not in st.session_state:
    st.session_state['end_date_with_additional'] = None
if 'total_monthly_payment_with_additional' not in st.session_state:
    st.session_state['total_monthly_payment_with_additional'] = 0
if 'lump_sum' not in st.session_state:
    st.session_state['lump_sum'] = 0
if 'years_left' not in st.session_state:
    st.session_state['years_left'] = 30

st.title('Mortgage Repayment Calculator')

# Create tabs
tab1, tab2 = st.tabs(["Mortgage Details", "Simulation and Analysis"])

# Inputs tab
with tab1:
    st.header("Mortgage Details")
    interest_rate = st.number_input('Current Interest Rate (%)', min_value=0.0, value=3.5, step=0.1, help="Your current mortgage rate")
    years_left = st.number_input('Time Left on Mortgage (years)', min_value=1, value=30, step=1)
    st.session_state['years_left'] =  years_left
    balance_input = st.text_input('Current Mortgage Balance', value='250,000')
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

# Simulation and Analysis tab


# Example date formatting function
def format_date(date_str):
    if date_str is None:
        return "N/A"
    date = pd.to_datetime(date_str)
    return date.strftime('%B %Y')

with tab2:
    col1, col2 = st.columns(2)

    with col1:
        st.header("Simulation")
        additional_repayment = st.number_input('Additional Monthly Repayment', min_value=0.0, value=0.0, step=100.0, help="Additional monthly payment increase")
        lump_sum = st.number_input('One Time Lump Sum (optional)', min_value=0.0, value=0.0, step=1000.0, help="If you were to pay in a one off lump sum")
        balance = locale.atof(balance_input.replace(',', ''))

        if lump_sum > balance:
            st.warning("Lump sum payment exceeds the mortgage balance.")

        # Container for the new rate and date fields
        with st.container():
            new_rate = st.number_input('New Mortgage Rate (%) (optional)', min_value=0.0, value=0.0, step=0.1, help="New mortgage rate")
            new_rate_date = st.date_input("Date for New Rate to Kick In (optional)", value=None, help="Date from which new rate is effective")

        # Validation for new rate and date fields
        if (new_rate > 0 and not new_rate_date) or (new_rate_date and new_rate == 0.0):
            st.warning("Both the new mortgage rate and the date it kicks in must be provided together.")

        if st.button('Run Simulation'):
            if (new_rate > 0 and not new_rate_date) or (new_rate_date and new_rate == 0.0):
                st.warning("Both the new mortgage rate and the date it kicks in must be provided together.")
            else:
                try:
                    if balance > 0:
                        schedule_without_additional, total_principal_paid_without_additional, total_interest_paid_without_additional, _ = calculate_mortgage_payments(interest_rate, years_left, balance, 0, 0, start_date)
                        schedule_with_additional, total_principal_paid_with_additional, total_interest_paid_with_additional, total_monthly_payment_with_additional = calculate_mortgage_payments(
                            interest_rate, years_left, balance, additional_repayment, lump_sum, start_date, 
                            new_rate if new_rate > 0 else None, new_rate_date if new_rate_date else None
                        )

                        st.write('Monthly Mortgage Repayment Schedule (Old parameters):')
                        st.dataframe(schedule_without_additional)
                        st.write('Monthly Mortgage Repayment Schedule (New parameters):')
                        st.dataframe(schedule_with_additional)

                        # Plot the data
                        chart_data = pd.DataFrame({
                            'Date': schedule_without_additional['Date'],
                            'Old Parameters': schedule_without_additional['Remaining Balance'],
                            'New Parameters': schedule_with_additional['Remaining Balance']
                        }).set_index('Date')
                        st.line_chart(chart_data)

                        # Calculate end dates
                        end_date_without_additional = schedule_without_additional['Date'].iloc[-1]
                        end_date_with_additional = schedule_with_additional['Date'].iloc[-1]

                        # Save values to session state
                        st.session_state['total_principal_paid_without_additional'] = total_principal_paid_without_additional
                        st.session_state['total_interest_paid_without_additional'] = total_interest_paid_without_additional
                        st.session_state['total_principal_paid_with_additional'] = total_principal_paid_with_additional
                        st.session_state['total_interest_paid_with_additional'] = total_interest_paid_with_additional
                        st.session_state['additional_repayment'] = additional_repayment
                        st.session_state['new_rate'] = new_rate
                        st.session_state['new_rate_date'] = new_rate_date
                        st.session_state['end_date_without_additional'] = end_date_without_additional
                        st.session_state['end_date_with_additional'] = end_date_with_additional
                        st.session_state['total_monthly_payment_with_additional'] = total_monthly_payment_with_additional
                        st.session_state['lump_sum'] = lump_sum
                        st.session_state['years_left'] = years_left

                        # Formatting the dates
                        new_rate_date = format_date(st.session_state['new_rate_date'])
                        end_date_without_additional = format_date(st.session_state['end_date_without_additional'])
                        end_date_with_additional = format_date(st.session_state['end_date_with_additional'])

                        # Display the summary in the right column
                        with col2:
                            st.header("Summary")
                            interest_savings = total_interest_paid_without_additional - total_interest_paid_with_additional
                            total_sum_old = total_principal_paid_without_additional + total_interest_paid_without_additional
                            total_sum_new = total_principal_paid_with_additional + total_interest_paid_with_additional
                            lump_sum_savings = total_interest_paid_without_additional - total_interest_paid_with_additional

                            # Generating the summary text with bold variables
                            if new_rate > 0 and additional_repayment > 0 and lump_sum > 0:
                                summary_text = (
                                    f"With the increased rate of **{new_rate:.2f}%** from **{new_rate_date}**, you will finish your mortgage at **{end_date_with_additional}** and your average monthly mortgage payment will be **{total_monthly_payment_with_additional:,.2f}**, "
                                    f"the total mortgage principal during this time would be **{total_principal_paid_with_additional:,.2f}** and the interest will be **{total_interest_paid_with_additional:,.2f}**, "
                                    f"which would mean the total sum of **{total_principal_paid_with_additional:,.2f} + {total_interest_paid_with_additional:,.2f} = {total_sum_new:,.2f}**.\n\n"
                                    f"By having an additional repayment of **{additional_repayment:,.2f}**, and a lump sum of **{lump_sum:,.2f}**, you can mitigate the impact of the rate change, making the total interest **{total_interest_paid_with_additional:,.2f}** instead of **{total_interest_paid_without_additional:,.2f}** "
                                    f"and the total sum repaid would be **{total_principal_paid_with_additional:,.2f} + {total_interest_paid_with_additional:,.2f} = {total_sum_new:,.2f}** instead of **{total_principal_paid_without_additional:,.2f} + {total_interest_paid_without_additional:,.2f} = {total_sum_old:,.2f}**.\n\n"
                                    f"The lump sum payment of **{lump_sum:,.2f}** saves you **{lump_sum_savings:,.2f}** in interest over the period of the mortgage."
                                )
                            elif additional_repayment > 0 and lump_sum > 0:
                                summary_text = (
                                    f"With an additional monthly repayment of **{additional_repayment:,.2f}**, and a lump sum of **{lump_sum:,.2f}**, the end date would be **{end_date_with_additional}** instead of **{end_date_without_additional}**, "
                                    f"making the total interest **{total_interest_paid_with_additional:,.2f}** instead of **{total_interest_paid_without_additional:,.2f}** "
                                    f"and the total sum repaid would be **{total_principal_paid_with_additional:,.2f} + {total_interest_paid_with_additional:,.2f} = {total_sum_new:,.2f}** instead of **{total_principal_paid_without_additional:,.2f} + {total_interest_paid_without_additional:,.2f} = {total_sum_old:,.2f}**.\n\n"
                                    f"The lump sum payment of **{lump_sum:,.2f}** saves you **{lump_sum_savings:,.2f}** in interest over the period of the mortgage."
                                )
                            elif new_rate > 0 and lump_sum > 0:
                                summary_text = (
                                    f"With the increased rate of **{new_rate:.2f}%** from **{new_rate_date}**, you will finish your mortgage at **{end_date_with_additional}** and your average monthly mortgage payment will be **{total_monthly_payment_with_additional:,.2f}**, "
                                    f"the total mortgage principal during this time would be **{total_principal_paid_with_additional:,.2f}** and the interest will be **{total_interest_paid_with_additional:,.2f}**, "
                                    f"which would mean the total sum of **{total_principal_paid_with_additional:,.2f} + {total_interest_paid_with_additional:,.2f} = {total_sum_new:,.2f}**.\n\n"
                                    f"The lump sum payment of **{lump_sum:,.2f}** saves you **{lump_sum_savings:,.2f}** in interest over the period of the mortgage."
                                )
                            elif additional_repayment > 0:
                                summary_text = (
                                    f"With an additional monthly repayment of **{additional_repayment:,.2f}**, the end date would be **{end_date_with_additional}** instead of **{end_date_without_additional}**, "
                                    f"making the total interest **{total_interest_paid_with_additional:,.2f}** instead of **{total_interest_paid_without_additional:,.2f}** "
                                    f"and the total sum repaid would be **{total_principal_paid_with_additional:,.2f} + {total_interest_paid_with_additional:,.2f} = {total_sum_new:,.2f}** instead of **{total_principal_paid_without_additional:,.2f} + {total_interest_paid_without_additional:,.2f} = {total_sum_old:,.2f}**."
                                )
                            elif new_rate > 0:
                                summary_text = (
                                    f"With the increased rate of **{new_rate:.2f}%** from **{new_rate_date}**, you will finish your mortgage at **{end_date_with_additional}** and your average monthly mortgage payment will be **{total_monthly_payment_with_additional:,.2f}**, "
                                    f"the total mortgage principal during this time would be **{total_principal_paid_with_additional:,.2f}** and the interest will be **{total_interest_paid_with_additional:,.2f}**, "
                                    f"which would mean the total sum of **{total_principal_paid_with_additional:,.2f} + {total_interest_paid_with_additional:,.2f} = {total_sum_new:,.2f}**."
                                )
                            elif lump_sum > 0:
                                summary_text = (
                                    f"By making a one-time lump sum payment of **{lump_sum:,.2f}**, the total interest would be **{total_interest_paid_with_additional:,.2f}** instead of **{total_interest_paid_without_additional:,.2f}**, "
                                    f"saving you **{lump_sum_savings:,.2f}** in interest over the period of the mortgage."
                                )
                            else:
                                summary_text = (
                                    f"Without any changes, you will pay off your mortgage by **{end_date_without_additional}** with no interest savings."
                                )

                            st.markdown(summary_text, unsafe_allow_html=True)

                    else:
                        st.error("Current Mortgage Balance must be greater than 0.")
                except ValueError:
                    st.error("Please enter a valid number for the Current Mortgage Balance.")
