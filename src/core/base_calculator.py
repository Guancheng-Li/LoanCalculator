"""
Copyright 2025. All rights reserved.
Authors: guanchenglichina@qq.com (Guancheng Li)

Interface for loan calculator.
"""

from datetime import datetime

from common.meta_info import MetaInfo


class BaseCalculator:
    def __init__(
        self, annual_interest_rate, loan_amount, loan_term_by_month, start_date_str
    ):
        self.annual_interest_rate = annual_interest_rate
        self.monthly_interest_rate = self.annual_interest_rate / 12
        self.loan_amount = loan_amount
        self.loan_term_by_month = loan_term_by_month
        self.start_date = datetime.strptime(start_date_str, "%Y%m%d")
        self.total_interest = None
        self.total_payment = None
        self.monthly_meta_info = {}

    def _calculate_impl(
        self,
        left_loan_term_by_month,
        left_loan_amount,
        executing_monthly_interest_rate,
        executing_start_date,
    ):
        raise NotImplementedError

    def _calculate_total_interest_and_total_payment(self):
        self.total_interest = 1.0 * sum(
            [v.monthly_interest_amount for v in self.monthly_meta_info.values()]
        )
        self.total_payment = 1.0 * sum(
            [v.monthly_payment for v in self.monthly_meta_info.values()]
        )

    def calculate(self):
        monthly_meta_info = self._calculate_impl(
            self.loan_term_by_month,
            self.loan_amount,
            self.monthly_interest_rate,
            self.start_date,
        )
        self.monthly_meta_info.update(monthly_meta_info)
        self._calculate_total_interest_and_total_payment()

    def print_info(self, print_montly_info=False):
        if print_montly_info:
            key_list = sorted(list(self.monthly_meta_info.keys()))
            for key in key_list:
                self.monthly_meta_info[key].print_info()
        print("-" * 20)
        print(f"贷款总额: {self.loan_amount:.2f}")
        print(f"贷款期限（月）: {self.loan_term_by_month}")
        print(f"执行年利率: {100 * self.annual_interest_rate:.2f}%")
        print(f"总还款额: {self.total_payment:.2f}")
        print(f"总利息: {self.total_interest:.2f}")

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

    def early_payment_without_term_change(
        self, early_payment_date_str, early_payment_amount
    ):
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
        if not left_months:
            return
        restart_date_str = left_months[0]
        restart_date = datetime.strptime(restart_date_str, "%Y%m%d")
        monthly_meta_info = self._calculate_impl(
            len(left_months),
            left_principal_amount - early_payment_amount,
            self.monthly_interest_rate,
            restart_date,
        )
        self.monthly_meta_info.update(monthly_meta_info)
        self._calculate_total_interest_and_total_payment()

    def early_payment_with_term_change(
        self, early_payment_date_str, early_payment_amount
    ):
        raise NotImplementedError
