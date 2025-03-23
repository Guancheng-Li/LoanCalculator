"""
Copyright 2025. All rights reserved.
Authors: guanchenglichina@qq.com (Guancheng Li)

Class for calculating annuity.
"""

from datetime import datetime

from numpy_financial import pmt, ppmt, ipmt

from common.date_time_utils import get_date_next_n_month
from common.meta_info import MetaInfo


class AnnuityCalculator:
    def __init__(
        self, annual_interest_rate, loan_amount, loan_term_by_month, start_date_str
    ):
        self.annual_interest_rate = annual_interest_rate
        self.monthly_interest_rate = self.annual_interest_rate / 12
        self.loan_amount = loan_amount
        self.loan_term_by_month = loan_term_by_month
        self.start_date = datetime.strptime(start_date_str, "%Y%m%d")
        self.latest_monthly_payment = None
        self.total_interest_paid = None
        self.total_payment = None
        self.monthly_meta_info = {}
        self.total_payment = None

    def _calculate_monthly_meta_info(
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
        return monthly_payment, monthly_meta_info

    def calculate(self):
        self.latest_monthly_payment, monthly_meta_info = (
            self._calculate_monthly_meta_info(
                self.loan_term_by_month,
                self.loan_amount,
                self.monthly_interest_rate,
                self.start_date,
            )
        )
        self.monthly_meta_info.update(monthly_meta_info)
        self.total_interest_paid = 1.0 * sum(
            [v.monthly_interest_amount for v in monthly_meta_info.values()]
        )
        self.total_payment = 1.0 * sum(
            [v.monthly_payment for v in monthly_meta_info.values()]
        )

    def print_info(self):
        key_list = sorted(list(self.monthly_meta_info.keys()))
        for key in key_list:
            self.monthly_meta_info[key].print_info()
        print(f"总还款额: {self.total_payment:.2f}")
        print(f"总利息: {self.total_interest_paid:.2f}")

    def save_to_csv_file(self, csv_file, with_header=False):
        key_list = sorted(list(self.monthly_meta_info.keys()))
        lines = []
        if with_header:
            lines.append("还款日期,还款额,本金,利息,剩余本金")
        for key in key_list:
            meta = self.monthly_meta_info[key]
            meta_value = [
                meta.date_str,
                f"{meta.monthly_payment:.2f}",
                f"{meta.monthly_principal_amount:.2f}",
                f"{meta.monthly_interest_amount:.2f}",
                f"{meta.left_loan_amount:.2f}",
            ]
            lines.append(",".join(meta_value))
        with open(csv_file, "w") as f:
            f.write("\n".join(lines) + "\n")

    def _get_early_payment_date(self, early_payment_date_str):
        pay_dates = sorted(list(self.monthly_meta_info.keys()))
        past_months = []
        left_months = []
        for pay_date in pay_dates:
            if pay_date <= early_payment_date_str:
                past_months.append(pay_date)
            else:
                left_months.append(pay_date)
        return past_months, left_months

    def early_payment(self, early_payment_date_str, early_payment_amount):
        past_months, left_months = self._get_early_payment_date(early_payment_date_str)
        if not left_months:
            return
        restart_date_str = left_months[0]
        restart_date = datetime.strptime(restart_date_str, "%Y%m%d")
        restart_meta = self.monthly_meta_info.get(restart_date_str)
        if not restart_meta:
            return
        # all loan is paid.
        if restart_meta.left_loan_amount <= early_payment_amount:
            for item in left_months:
                del self.monthly_meta_info[item]
            self.monthly_meta_info[early_payment_date_str] = MetaInfo(
                -1,
                early_payment_date_str,
                restart_meta.left_loan_amount,
                0,
                0,
                0,
            )
            return
        # part of loan is paid.
        self.latest_monthly_payment, monthly_meta_info = (
            self._calculate_monthly_meta_info(
                self.loan_term_by_month - len(past_months),
                restart_meta.left_loan_amount - early_payment_amount,
                self.monthly_interest_rate,
                restart_date,
            )
        )
        self.monthly_meta_info.update(monthly_meta_info)
        self.total_interest_paid = 1.0 * sum(
            [v.monthly_interest_amount for v in monthly_meta_info.values()]
        )
        self.total_payment = 1.0 * sum(
            [v.monthly_payment for v in monthly_meta_info.values()]
        )
