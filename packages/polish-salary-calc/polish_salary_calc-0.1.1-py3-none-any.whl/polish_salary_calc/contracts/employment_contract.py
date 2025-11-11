from decimal import Decimal
from typing import override
from polish_salary_calc.rates.rates import Rates
from polish_salary_calc.contract_settings.employment_contract_settings import EmploymentContractSettings
from polish_salary_calc.contracts.base_contract import BaseContract
from polish_salary_calc.salary.salary_utilities import SalaryUtilities

class EmploymentContract(BaseContract[EmploymentContractSettings]):
    def __init__(self, rates: Rates, contract_settings: EmploymentContractSettings) -> None:
        super().__init__(rates, contract_settings)

    @override
    def calculate_salary_base(self) -> Decimal:
        return super().calculate_salary_base()

    @override
    def calculate_sick_pay(self) -> Decimal:
        return self.contract_settings.sick_pay

    @override
    def calculate_salary_gross(self) -> Decimal:
        return super().calculate_salary_gross()

    @override
    def calculate_social_security_base(self) -> Decimal:
        return super().calculate_social_security_base()

    @override
    def calculate_pension_insurance(self) -> Decimal:
        return super().calculate_pension_insurance()

    @override
    def calculate_disability_insurance(self) -> Decimal:
        return super().calculate_disability_insurance()

    @override
    def calculate_sickness_insurance(self) -> Decimal:
        return super().calculate_sickness_insurance()

    @override
    def calculate_cost(self) -> Decimal:
        return super().calculate_cost()

    @override
    def _calculate_regular_cost(self) -> Decimal:
        if self.contract_settings.increased_costs:
            return self.rates.income_tax_deduction[1]
        else:
            return self.rates.income_tax_deduction[0]

    @override
    def _calculate_author_rights_cost(self) -> Decimal:
        return SalaryUtilities.calculate_author_rights_cost(
            self.regular_cost,
            self.contract_settings.cost_fifty_ratio,
            self.health_insurance_base,
            self.contract_settings.cost_fifty_sum,
            self.rates.cost_threshold
        )

    @override
    def calculate_health_insurance_base(self) -> Decimal:
        return super().calculate_health_insurance_base()

    @override
    def calculate_health_insurance(self) -> Decimal:
        return super().calculate_health_insurance()

    @override
    def calculate_tax_base(self) -> Decimal:
        return super().calculate_tax_base()

    @override
    def calculate_tax(self) -> Decimal:
        if self.contract_settings.under_26: return Decimal('0.0')
        if not self.contract_settings.active_business:
            out = SalaryUtilities.calculate_tax(
                self.rates.income_tax,
                self.tax_base,
                self.contract_settings.tax_base_sum,
                self.rates.tax_threshold,
                self.rates.month_tax_free
            )
        else:
            out = SalaryUtilities.calculate_tax(
                self.rates.income_tax,
                self.tax_base,
                self.contract_settings.tax_base_sum,
                self.rates.tax_threshold
            )
        return out

    @override
    def calculate_ppk_tax(self) -> Decimal:
        if self.contract_settings.under_26: return Decimal('0.0')
        return super().calculate_ppk_tax()

    @override
    def calculate_salary_deductions(self) -> Decimal:
        return super().calculate_salary_deductions()

    @override
    def calculate_employee_ppk_contribution(self) -> Decimal:
        return super().calculate_employee_ppk_contribution()

    @override
    def calculate_net_salary(self) -> Decimal:
        return super().calculate_net_salary()
    @override
    def calculate_pension_contribution(self) -> Decimal:
        return super().calculate_pension_contribution()

    @override
    def calculate_disability_contribution(self)-> Decimal:
        return super().calculate_disability_contribution()

    @override
    def calculate_accident_insurance(self) -> Decimal:
        return super().calculate_accident_insurance()

    @override
    def calculate_fp(self) -> Decimal:
        if not self.contract_settings.fp_fgsp:
            return Decimal('0')
        else:
            return super().calculate_fp()

    @override
    def calculate_fgsp(self) -> Decimal:
        if not self.contract_settings.fp_fgsp:
            return Decimal('0')
        else:
            return super().calculate_fgsp()