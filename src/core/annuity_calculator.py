"""
Copyright 2025. All rights reserved.
Authors: guanchenglichina@qq.com (Guancheng Li)

Class for calculating annuity.
"""

from numpy_financial import pmt, ppmt, ipmt

from common.date_time_utils import get_date_next_n_month
from common.meta_info import MetaInfo
from core.base_calculator import BaseCalculator


class AnnuityCalculator(BaseCalculator):
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
        monthly_payment = pmt(
            executing_monthly_interest_rate, left_loan_term_by_month, -left_loan_amount
        )
        monthly_meta_info = {}
        unpaid_loan_amount = left_loan_amount
        for i in range(left_loan_term_by_month):
            monthly_principal_amount = ppmt(
                executing_monthly_interest_rate,
                i + 1,
                left_loan_term_by_month,
                -unpaid_loan_amount,
            )
            monthly_interest_amount = ipmt(
                executing_monthly_interest_rate,
                i + 1,
                left_loan_term_by_month,
                -unpaid_loan_amount,
            )
            unpaid_loan_amount -= monthly_principal_amount
            # TODO(guancheng): fix i start from the real index in meta info.
            paying_date = get_date_next_n_month(executing_start_date, i).strftime(
                "%Y%m%d"
            )
            meta = MetaInfo(
                i + 1,
                paying_date,
                monthly_payment,
                monthly_principal_amount,
                monthly_interest_amount,
                left_loan_amount,
            )
            monthly_meta_info[paying_date] = meta
        return monthly_meta_info
