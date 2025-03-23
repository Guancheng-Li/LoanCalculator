# -*- coding: utf-8 -*-
#!/usr/bin/env python

from core.annuity import AnnuityCalculator


def main():
    annual_interest_rate = 0.036
    loan_amount = 1500000
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
    annuity_info.early_payment("20250322", 200000)
    annuity_info.early_payment("20250722", 200000)
    annuity_info.early_payment("20251122", 200000)
    annuity_info.early_payment("20260322", 200000)
    annuity_info.early_payment("20260722", 200000)
    annuity_info.print_info()


if __name__ == "__main__":
    main()
