import streamlit as st
import locale
import pandas as pd
from calculations import calculate_mortgage_payments

# Set the locale to the user's default setting (for number formatting)
locale.setlocale(locale.LC_ALL, '')

# Example date formatting function
def format_date(date_str):
    if date_str is None:
        return "N/A"
    date = pd.to_datetime(date_str)
    return date.strftime('%B %Y')

def display_simulation_and_analysis():
    col1, col2 = st.columns(2)

    with col1:
        st.header("Simulation")
        additional_repayment = st.number_input('Additional Monthly Repayment', min_value=0.0, value=0.0, step=100.0, help="Additional monthly payment increase")
        lump_sum = st.number_input('One Time Lump Sum (optional)', min_value=0.0, value=0.0, step=1000.0, help="If you were to pay in a one off lump sum")
        balance_input = st.text_input('Current Mortgage Balance (for simulation)', value='250,000')
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
                        interest_rate = st.session_state.get('interest_rate', 3.5)
                        years_left = st.session_state.get('years_left', 30)
                        start_date = st.session_state.get('start_date', None)

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
