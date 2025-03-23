# -*- coding: utf-8 -*-
#!/usr/bin/env python

from core.annuity_calculator import AnnuityCalculator
from core.linear_calculator import LinearCalculator


def test_annuity():
    annual_interest_rate = 0.036
    loan_amount = 150 * 10000
    loan_term_by_month = 360
    start_date_str = "20250420"

    annuity_info = AnnuityCalculator(
        annual_interest_rate,
        loan_amount,
        loan_term_by_month,
        start_date_str,
    )
    annuity_info.calculate()
    annuity_info.print_info()
    annuity_info.save_to_csv_file("/tmp/annuity_info.csv", with_header=True)
    annuity_info.early_payment_without_term_change("20250322", 200000)
    annuity_info.early_payment_without_term_change("20250722", 200000)
    annuity_info.early_payment_without_term_change("20251122", 200000)
    annuity_info.early_payment_without_term_change("20260322", 200000)
    annuity_info.early_payment_without_term_change("20260722", 200000)
    annuity_info.print_info()


def test_linear():
    annual_interest_rate = 0.036
    loan_amount = 250 * 10000
    loan_term_by_month = 360
    start_date_str = "20250420"

    annuity_info = LinearCalculator(
        annual_interest_rate,
        loan_amount,
        loan_term_by_month,
        start_date_str,
    )
    annuity_info.calculate()
    annuity_info.print_info()
    annuity_info.save_to_csv_file("/tmp/linear_info.csv", with_header=True)
    annuity_info.early_payment_without_term_change("20250709", 200000)
    annuity_info.early_payment_without_term_change("20251109", 200000)
    annuity_info.early_payment_without_term_change("20260309", 200000)
    annuity_info.early_payment_without_term_change("20260709", 200000)
    annuity_info.print_info()


def main():
    test_annuity()
    test_linear()


if __name__ == "__main__":
    main()
