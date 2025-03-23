"""
Copyright 2025. All rights reserved.
Authors: guanchenglichina@qq.com (Guancheng Li)

Class for calculating annuity.
"""

import datetime
import math

from numpy_financial import ipmt, nper, pmt, ppmt

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
        self.fixed_monthly_payment = None

    def _calculate_impl(
        self,
        left_loan_term_by_month,
        left_loan_amount,
        executing_monthly_interest_rate,
        executing_start_date,
    ):
        self.fixed_monthly_payment = pmt(
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
                self.fixed_monthly_payment,
                monthly_principal_amount,
                monthly_interest_amount,
                left_loan_amount,
            )
            monthly_meta_info[paying_date] = meta
        return monthly_meta_info

    def early_payment_with_term_change(
        self, early_payment_date_str, early_payment_amount
    ):
        """For annuity loan with term change, \
            calculator keeps the monthly payment unchanged.
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
        left_loan_term_by_month = math.ceil(
            nper(rate=self.monthly_interest_rate, pmt=self.fixed_monthly_payment, pv=-left_principal_amount_after_paid, fv=0)
        )
        # TODO: keep the shorten the loan term somewhere: `len(left_months) - left_loan_term_by_month`.
        if not left_months:
            return
        for item in left_months:
            del self.monthly_meta_info[item]

        # calculate the new monthly meta info.
        remaining_principal = left_principal_amount_after_paid
        monthly_meta_info = {}
        for i in range(left_loan_term_by_month):
            # monthly interest and principal
            monthly_interest_amount = remaining_principal * self.monthly_interest_rate
            monthly_principal_amount = self.fixed_monthly_payment - monthly_interest_amount

            # last month
            if i == left_loan_term_by_month - 1:
                monthly_principal_amount = remaining_principal
                monthly_interest_amount = self.fixed_monthly_payment - monthly_principal_amount
                remaining_principal = 0
            else:
                remaining_principal -= monthly_principal_amount

            paying_date = left_months[i]
            meta = MetaInfo(
                i + 1,
                paying_date,
                self.fixed_monthly_payment,
                monthly_principal_amount,
                monthly_interest_amount,
                remaining_principal,
            )
            monthly_meta_info[paying_date] = meta
        self.monthly_meta_info.update(monthly_meta_info)
        self._calculate_total_interest_and_total_payment()
