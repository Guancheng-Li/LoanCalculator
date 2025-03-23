"""
Copyright 2025. All rights reserved.
Authors: guanchenglichina@qq.com (Guancheng Li)

Meta info for monthly payment.
"""


class MetaInfo:
    def __init__(
        self,
        index,
        date_str,
        monthly_payment,
        monthly_principal_amount,
        monthly_interest_amount,
        left_loan_amount,
    ):
        self.index = index
        self.date_str = date_str
        self.monthly_payment = monthly_payment
        self.monthly_principal_amount = monthly_principal_amount
        self.monthly_interest_amount = monthly_interest_amount
        self.left_loan_amount = left_loan_amount

    def print_info(self):
        info = [
            f"第{self.index}个月还款额: {self.monthly_payment:.2f}",
            f"还款日期: {self.date_str}",
            f"本金: {self.monthly_principal_amount:.2f}",
            f"利息: {self.monthly_interest_amount:.2f}",
            f"剩余本金: {self.left_loan_amount:.2f}",
        ]
        print(", ".join(info))
