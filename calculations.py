import pandas as pd
from datetime import datetime

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
