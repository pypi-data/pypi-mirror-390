from decimal import Decimal
from typing import override

from polish_salary_calc.rates.rates import Rates
from polish_salary_calc.contract_settings.mandate_contract_settings import MandateContractSettings, MandateContractType
from polish_salary_calc.contracts.base_contract import BaseContract
from polish_salary_calc.salary.salary_utilities import SalaryUtilities


class MandateContract(BaseContract[MandateContractSettings]):
    def __init__(self, rates: Rates, contract_settings: MandateContractSettings) -> None:
        super().__init__(rates, contract_settings)

    @override
    def calculate_salary_base(self) -> Decimal:
        return super().calculate_salary_base()

    @override
    def calculate_sick_pay(self) -> Decimal:
        return Decimal('0.0')

    @override
    def calculate_salary_gross(self) -> Decimal:
        return super().calculate_salary_gross()

    @override
    def calculate_social_security_base(self) -> Decimal:
        match self.contract_settings.mandate_contract_type:
            case MandateContractType.UNDER_26_AND_STUDENT | MandateContractType.OTHER_COMPANY_MIN_SALARY:
                return Decimal('0.0')
            case MandateContractType.COMMON | MandateContractType.THE_SAME_COMPANY:
                return super().calculate_social_security_base()
            case _: raise NotImplementedError(f'Unknown mandate contract type:  {self.contract_settings.mandate_contract_type}')

    @override
    def calculate_pension_insurance(self) -> Decimal:
        match self.contract_settings.mandate_contract_type:
            case MandateContractType.UNDER_26_AND_STUDENT | MandateContractType.OTHER_COMPANY_MIN_SALARY:
                return Decimal('0.0')
            case MandateContractType.COMMON | MandateContractType.THE_SAME_COMPANY:
                return super().calculate_pension_insurance()
            case _:
                raise NotImplementedError(f'Unknown mandate contract type:  {self.contract_settings.mandate_contract_type}')

    @override
    def calculate_disability_insurance(self) -> Decimal:
        match self.contract_settings.mandate_contract_type:
            case MandateContractType.UNDER_26_AND_STUDENT | MandateContractType.OTHER_COMPANY_MIN_SALARY:
                return Decimal('0.0')
            case MandateContractType.COMMON | MandateContractType.THE_SAME_COMPANY:
                return super().calculate_disability_insurance()
            case _:
                raise NotImplementedError(f'Unknown mandate contract type:  {self.contract_settings.mandate_contract_type}')

    @override
    def calculate_sickness_insurance(self) -> Decimal:
        match self.contract_settings.mandate_contract_type:
            case MandateContractType.UNDER_26_AND_STUDENT | MandateContractType.OTHER_COMPANY_MIN_SALARY | MandateContractType.COMMON:
                return Decimal('0.0')
            case  MandateContractType.THE_SAME_COMPANY:
                return super().calculate_sickness_insurance()
            case _:
                raise NotImplementedError(f'Unknown mandate contract type:  {self.contract_settings.mandate_contract_type}')

    @override
    def calculate_cost(self) -> Decimal:
        if self.contract_settings.mandate_contract_type == MandateContractType.UNDER_26_AND_STUDENT:
            return Decimal('0')
        else:
            return super().calculate_cost()

    @override
    def _calculate_regular_cost(self) -> Decimal:
        if self.contract_settings.is_a_lump_sum and self.salary_gross<=Decimal('200'): return Decimal('0.0')
        if not self.contract_settings.is_fifty:
            return self.health_insurance_base * self.rates.income_tax_deduction_20_50[0]
        else:
            return Decimal('0.0')

    @override
    def _calculate_author_rights_cost(self) -> Decimal:
        if not self.contract_settings.is_fifty: return Decimal('0.0')
        if self.contract_settings.is_a_lump_sum and self.salary_gross<=Decimal('200'): return Decimal('0.0')
        return SalaryUtilities.calculate_author_rights_cost(
                Decimal('0'),
                self.rates.income_tax_deduction_20_50[1],
                self.health_insurance_base,
                self.contract_settings.cost_fifty_sum,
                self.rates.cost_threshold
                )

    @override
    def calculate_health_insurance_base(self) -> Decimal:
        if self.contract_settings.mandate_contract_type == MandateContractType.UNDER_26_AND_STUDENT:
            return Decimal('0.0')
        return super().calculate_health_insurance_base()

    @override
    def calculate_health_insurance(self) -> Decimal:
        return super().calculate_health_insurance()

    @override
    def calculate_tax_base(self) -> Decimal:
        return super().calculate_tax_base()

    @override
    def calculate_tax(self) -> Decimal:
        if self.contract_settings.mandate_contract_type == MandateContractType.UNDER_26_AND_STUDENT: return Decimal('0.0')

        if (self.contract_settings.is_a_lump_sum
                and self.salary_gross<= Decimal('200')
                and self.contract_settings.mandate_contract_type!=MandateContractType.THE_SAME_COMPANY):
            return self.salary_gross*self.rates.income_tax[0]

        out = self.tax_base * self.rates.income_tax[0]- self.rates.month_tax_free
        return out if out>Decimal('0.0') else Decimal('0.0')

    @override
    def calculate_ppk_tax(self) -> Decimal:
        if self.contract_settings.mandate_contract_type == (MandateContractType.UNDER_26_AND_STUDENT or MandateContractType.OTHER_COMPANY_MIN_SALARY):
            return Decimal('0.0')
        return super().calculate_ppk_tax()

    @override
    def calculate_salary_deductions(self) -> Decimal:
        return super().calculate_salary_deductions()

    @override
    def calculate_employee_ppk_contribution(self) -> Decimal:
        if (self.contract_settings.mandate_contract_type ==
                (MandateContractType.UNDER_26_AND_STUDENT or MandateContractType.OTHER_COMPANY_MIN_SALARY)):
            return Decimal('0.0')
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
        if not self.contract_settings.fp:
            return Decimal('0')
        else:
            return super().calculate_fp()

    @override
    def calculate_fgsp(self) -> Decimal:
        if not self.contract_settings.fgsp:
            return Decimal('0')
        else:
            return super().calculate_fgsp()

    @override
    def calculate_employer_ppk_contribution(self) -> Decimal:
        if self.contract_settings.mandate_contract_type == (MandateContractType.UNDER_26_AND_STUDENT or MandateContractType.OTHER_COMPANY_MIN_SALARY):
            return Decimal('0.0')
        return super().calculate_employer_ppk_contribution()

    @override
    def calculate_total_employer_cost(self) -> Decimal:
        return super().calculate_total_employer_cost()
