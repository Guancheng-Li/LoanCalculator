"""
Copyright 2025. All rights reserved.
Authors: guanchenglichina@qq.com (Guancheng Li)

Class for calculating linear.
"""

from datetime import datetime

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
        self.fixed_monthly_principal_amount = self.loan_amount / self.loan_term_by_month

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

    def early_payment_with_term_change(
        self, early_payment_date_str, early_payment_amount
    ):
        """For linear loan with term change, \
            calculator can only keep the monthly principal amount unchanged.
            Because the monthly payment is always changed by interest.
        """
        past_months, left_months = self._get_early_payment_date(early_payment_date_str)
        if not left_months:
            return
        left_principal_amount = self.loan_amount
        if past_months:
            left_principal_amount = self.monthly_meta_info[
                past_months[-1]
            ].left_loan_amount
        # all loan is paid.
        if left_principal_amount <= early_payment_amount:
            for item in left_months:
                del self.monthly_meta_info[item]
            self.monthly_meta_info[early_payment_date_str] = MetaInfo(
                -1,
                early_payment_date_str,
                left_principal_amount,
                0,
                0,
                0,
            )
            return
        # part of loan is paid.
        left_principal_amount_after_paid = left_principal_amount - early_payment_amount
        left_loan_term_by_month = int(
            left_principal_amount_after_paid // self.fixed_monthly_principal_amount
        )
        if (
            left_loan_term_by_month * self.fixed_monthly_principal_amount
            < left_principal_amount_after_paid
        ):
            left_loan_term_by_month += 1
        if not left_months:
            return
        restart_date_str = left_months[0]
        restart_date = datetime.strptime(restart_date_str, "%Y%m%d")
        for item in left_months:
            del self.monthly_meta_info[item]
        monthly_meta_info = self._calculate_impl(
            left_loan_term_by_month,
            left_principal_amount - early_payment_amount,
            self.monthly_interest_rate,
            restart_date,
        )
        self.monthly_meta_info.update(monthly_meta_info)
        self._calculate_total_interest_and_total_payment()
