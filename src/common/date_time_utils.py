"""
Copyright 2025. All rights reserved.
Authors: guanchenglichina@qq.com (Guancheng Li)

Date time utilities.
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta


def get_date_next_n_month(start_date, n):
    return start_date + relativedelta(months=n)


def get_date_str_next_n_month(start_date_str, n):
    return get_date_next_n_month(
        datetime.strptime(start_date_str, "%Y%m%d"), n
    ).strftime("%Y%m%d")


def rest_loan_term_by_month(loan_term_by_month, start_date_str):
    """Calculate the months between start month and current date."""
    start_date = datetime.strptime(start_date_str, "%Y%m%d")
    current_date = datetime.now()
    past_months = (current_date.year - start_date.year) * 12 + (
        current_date.month - start_date.month
    )
    # 如果当前日期的天数 < 起始日期的天数，减1个月
    if current_date.day < start_date.day:
        past_months -= 1
    left_months = loan_term_by_month - past_months
    return past_months, left_months
