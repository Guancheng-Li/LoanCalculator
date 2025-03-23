"""
Copyright 2025. All rights reserved.
Authors: guanchenglichina@qq.com (Guancheng Li)

Class for calculating linear.
"""

from common.date_time_utils import get_date_next_n_month
from common.meta_info import MetaInfo
from core.base_calculator import BaseCalculator


class LinearCalculator(BaseCalculator):
    def __init__(
        self, annual_interest_rate, loan_amount, loan_term_by_month, start_date_str
    ):
        super().__init__(
            annual_interest_rate, loan_amount, loan_term_by_month, start_date_str
        )

    def _calculate_impl(
        self,
        left_loan_term_by_month,
        left_loan_amount,
        executing_monthly_interest_rate,
        executing_start_date,
    ):
        monthly_meta_info = {}
        monthly_principal_amount = left_loan_amount / left_loan_term_by_month
        for i in range(left_loan_term_by_month):
            monthly_interest_amount = (
                left_loan_amount - i * monthly_principal_amount
            ) * executing_monthly_interest_rate
            monthly_payment = monthly_principal_amount + monthly_interest_amount
            paying_date = get_date_next_n_month(executing_start_date, i).strftime(
                "%Y%m%d"
            )
            unpaid_loan_amount = left_loan_amount - (i + 1) * monthly_principal_amount
            meta = MetaInfo(
                i + 1,
                paying_date,
                monthly_payment,
                monthly_principal_amount,
                monthly_interest_amount,
                unpaid_loan_amount,
            )
            monthly_meta_info[paying_date] = meta
        return monthly_meta_info
