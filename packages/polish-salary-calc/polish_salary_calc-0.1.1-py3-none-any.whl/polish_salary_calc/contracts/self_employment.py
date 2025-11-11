from decimal import Decimal
from typing import override
from polish_salary_calc.rates.rates import Rates
from polish_salary_calc.contract_settings.self_employment_settings import SelfEmploymentSettings, SelfEmploymentType, TaxType, \
    HealthBase, LUMP_RATES_ALLOWED
from polish_salary_calc.contracts.base_contract import BaseContract
from polish_salary_calc.salary.salary_utilities import SalaryUtilities

class SelfEmployment(BaseContract[SelfEmploymentSettings]):
    def __init__(self, rates: Rates, contract_settings: SelfEmploymentSettings) -> None:
        super().__init__(rates, contract_settings)

    @override
    def calculate_salary_base(self) -> Decimal:
        return super().calculate_salary_base()

    @override
    def calculate_sick_pay(self) -> Decimal:
        return Decimal('0.0')

    @override
    def calculate_salary_gross(self) -> Decimal:
        return self.salary_base - self.contract_settings.costs

    @override
    def calculate_social_security_base(self) -> Decimal:
        social_base = Decimal('0.0')

        if self.contract_settings.other_minimum_contract:
            return social_base

        match self.contract_settings.self_employment_type:
            case SelfEmploymentType.COMMON:
                    social_base = self.rates.standard_social_insurance_base
            case SelfEmploymentType.PREFERRED:
                    social_base = self.rates.reduced_social_insurance_base
            case SelfEmploymentType.STARTUP_RELIEF | SelfEmploymentType.UNREGISTERED_BUSINESS:
                    social_base = Decimal('0.0')
            # case SelfEmploymentType.SMALL_ZUS:
            #         social_base = self.contract_settings.average_social_income_previous_year*self.rates.
            case _:
                raise NotImplementedError('Unknown self employment type: ' + self.contract_settings.self_employment_type)

        if self.contract_settings.is_sick_pay and self.contract_settings.sick_pay_days > 0 and self.contract_settings.month_days > 0:
            social_base = social_base * (self.contract_settings.month_days - self.contract_settings.sick_pay_days) / self.contract_settings.month_days

        return social_base

    @override
    def calculate_pension_insurance(self) -> Decimal:
        return SalaryUtilities.calculate_pension_or_disability_insurance(
            self.rates.pension_insurance_rate+self.rates.employer_pension_contribution_rate,
            self.social_security_base,
            self.contract_settings.social_security_base_sum,
            self.rates.social_insurance_cap
        )

    @override
    def calculate_disability_insurance(self) -> Decimal:
        return SalaryUtilities.calculate_pension_or_disability_insurance(
            self.rates.disability_insurance_rate+self.rates.employer_disability_contribution_rate,
            self.social_security_base,
            self.contract_settings.social_security_base_sum,
            self.rates.social_insurance_cap
        )

    @override
    def calculate_sickness_insurance(self) -> Decimal:
        if self.contract_settings.is_sick_pay:
            return super().calculate_sickness_insurance()
        else:
            return Decimal('0.0')

    @override
    def calculate_social_insurance_sum(self) -> Decimal:
        return self.pension_insurance + self.disability_insurance + self.sickness_insurance + self.accident_insurance+self.fp+self.fgsp

    @override
    def calculate_cost(self) -> Decimal:
        return super().calculate_cost()

    @override
    def _calculate_regular_cost(self) -> Decimal:
        return self.contract_settings.costs

    @override
    def _calculate_author_rights_cost(self) -> Decimal:
        return Decimal('0.0')

    @override
    def calculate_health_insurance_base(self) -> Decimal:
        if self.contract_settings.self_employment_type == SelfEmploymentType.UNREGISTERED_BUSINESS:
            return Decimal('0.0')

        if self.contract_settings.tax_type == TaxType.A_LUMP_SUM:
            if self.contract_settings.health_base == HealthBase.NONE:
                cap = Decimal('12')*self.salary_base
                if cap <= self.rates.se_lump_health_insurance_cap[0]:
                    return self.rates.health_insurance_lump_base[0]
                elif cap <= self.rates.se_lump_health_insurance_cap[1]:
                    return self.rates.health_insurance_lump_base[1]
                else:
                    return self.rates.health_insurance_lump_base[2]
            else: return self.rates.health_insurance_lump_base[self.contract_settings.health_base.value - 1]

        min_base = self.rates.health_insurance_base
        output = self.salary_gross - self.social_insurance_sum
        return max(min_base,output)

    @override
    def calculate_health_insurance(self) -> Decimal:
        if self.contract_settings.tax_type == TaxType.LINE_TAX:
            out = self.health_insurance_base * self.rates.health_insurance_rate_line_tax
            min_health_insurance = self.rates.health_insurance_base * self.rates.health_insurance_rate
            return max(min_health_insurance,out)

        return super().calculate_health_insurance()

    @override
    def calculate_tax_base(self) -> Decimal:
        if self.contract_settings.tax_type==TaxType.A_LUMP_SUM:
            return self.salary_base

        return self.salary_gross - self.social_insurance_sum

    @override
    def calculate_tax(self) -> Decimal:
        if self.contract_settings.tax_type == TaxType.STANDARD:
            present_tax_base_sum = self.tax_base + self.contract_settings.tax_base_sum
            if present_tax_base_sum <= self.rates.tax_free_base:
                return Decimal('0.0')
            elif  self.rates.tax_free_base <= present_tax_base_sum <= self.rates.tax_threshold:
                if self.contract_settings.tax_base_sum <= self.rates.tax_free_base:
                    return (present_tax_base_sum-self.rates.tax_free_base)*self.rates.income_tax[0]
                else: return self.tax_base*self.rates.income_tax[0]
            else:
                if self.contract_settings.tax_base_sum <= self.rates.tax_threshold:
                    return ((present_tax_base_sum-self.rates.tax_threshold) * self.rates.income_tax[1] +
                            (self.rates.tax_threshold - self.contract_settings.tax_base_sum) * self.rates.income_tax[0])
                else: return self.tax_base*self.rates.income_tax[1]
        elif self.contract_settings.tax_type == TaxType.LINE_TAX:
            return self.tax_base *self.rates.line_tax_rate
        else:
            if self.contract_settings.tax_lump_rate not in LUMP_RATES_ALLOWED:
                raise ValueError("Lump rate not allowed")
            return self.tax_base * self.contract_settings.tax_lump_rate

    @override
    def calculate_ppk_tax(self) -> Decimal:
        return Decimal('0.0')

    @override
    def calculate_salary_deductions(self) -> Decimal:
        return super().calculate_salary_deductions()

    @override
    def calculate_employee_ppk_contribution(self) -> Decimal:
        return Decimal('0.0')

    @override
    def calculate_net_salary(self) -> Decimal:
        return self.salary_gross - self.social_insurance_sum-self.tax_advance_payment-self.health_insurance

    @override
    def calculate_pension_contribution(self) -> Decimal:
        return Decimal('0.0')

    @override
    def calculate_disability_contribution(self)-> Decimal:
        return Decimal('0.0')


    @override
    def calculate_accident_insurance(self) -> Decimal:
        return super().calculate_accident_insurance()

    @override
    def calculate_fp(self) -> Decimal:
        if not self.contract_settings.is_fp:
            return Decimal('0')
        else:
            if self.social_security_base >self.rates.minimum_wage:
                return self.social_security_base * self.rates.fp_rate
            else:
                return Decimal('0')

    @override
    def calculate_fgsp(self) -> Decimal:
        return Decimal('0.0')

    @override
    def calculate_employer_ppk_contribution(self) -> Decimal:
        return Decimal('0.0')

    @override
    def calculate_total_employer_cost(self) -> Decimal:
        return self.salary_base

    @override
    def calculate_gross(self) -> None:
        self.salary_base = self.calculate_salary_base().quantize(Decimal('0.01'))
        self.salary_sick_pay = self.calculate_sick_pay().quantize(Decimal('0.01'))
        self.salary_gross= self.calculate_salary_gross().quantize(Decimal('0.01'))
        self.social_security_base = self.calculate_social_security_base().quantize(Decimal('0.01'))
        self.social_security_base_total = self.calculate_social_security_base_total().quantize(Decimal('0.01'))
        self.pension_insurance = self.calculate_pension_insurance().quantize(Decimal('0.01'))
        self.disability_insurance = self.calculate_disability_insurance().quantize(Decimal('0.01'))
        self.sickness_insurance = self.calculate_sickness_insurance().quantize(Decimal('0.01'))
        self.regular_cost = self._calculate_regular_cost().quantize(Decimal('0.01'))
        self.author_rights_cost = self._calculate_author_rights_cost().quantize(Decimal('0.01'))
        self.cost = self.calculate_cost().quantize(Decimal('0.01'))
        self.cost_fifty_total = self.calculate_cost_fifty_total().quantize(Decimal('0.01'))
        self.employee_ppk_contribution = self.calculate_employee_ppk_contribution().quantize(Decimal('0.01'))
        self.employer_pension_contribution = self.calculate_pension_contribution().quantize(Decimal('0.01'))
        self.employer_disability_contribution = self.calculate_disability_contribution().quantize(Decimal('0.01'))
        self.accident_insurance = self.calculate_accident_insurance().quantize(Decimal('0.01'))
        self.fp = self.calculate_fp().quantize(Decimal('0.01'))
        self.fgsp = self.calculate_fgsp().quantize(Decimal('0.01'))
        self.social_insurance_sum = self.calculate_social_insurance_sum().quantize(Decimal('0.01'))
        self.tax_base = self.calculate_tax_base().quantize(Decimal('1'))
        self.tax_base_total = self.calculate_tax_base_total().quantize(Decimal('0.01'))
        self.ppk_tax = self.calculate_ppk_tax().quantize(Decimal('0.01'))
        self.tax = self._add_ppk_tax_and_check_if_is_positive(self.calculate_tax()).quantize(Decimal('0.01'))
        self.health_insurance_base = self.calculate_health_insurance_base().quantize(Decimal('0.01'))
        self.health_insurance = self.calculate_health_insurance().quantize(Decimal('0.01'))
        self.salary_deductions = self.calculate_salary_deductions().quantize(Decimal('0.01'))
        self.tax_advance_payment = self.calculate_tax_advance_payment().quantize(Decimal('1'))
        self.employer_ppk_contribution = self.calculate_employer_ppk_contribution().quantize(Decimal('0.01'))
        self.net_salary = self.calculate_net_salary().quantize(Decimal('0.01'))
        self.total_employer_cost = self.calculate_total_employer_cost().quantize(Decimal('0.01'))

        if (self.contract_settings.self_employment_type==SelfEmploymentType.UNREGISTERED_BUSINESS and
            self.salary_base > self.rates.unregistered_cap):
            raise ValueError("Salary base for unregistered business exceeded unregistered business income cap")


