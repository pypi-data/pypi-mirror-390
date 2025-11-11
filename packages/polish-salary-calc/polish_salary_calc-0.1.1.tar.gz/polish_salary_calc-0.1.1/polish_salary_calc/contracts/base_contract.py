from polish_salary_calc.contract_settings.contract_settings import ContractSettngs
from decimal import Decimal, ROUND_UP
from polish_salary_calc.salary.salary import Salary,SalaryType
from polish_salary_calc.rates.rates import Rates
from polish_salary_calc.salary.salary_utilities import SalaryUtilities
from abc import ABC, abstractmethod


class BaseContract[T: ContractSettngs](Salary, ABC):
    def __init__(self, rates: Rates, contract_settings: T) -> None:
        super().__init__(rates,contract_settings)
        self.rates = rates
        self.contract_settings = contract_settings


    def update_rates(self, rates: Rates) -> None:
        self.rates = rates
        self.is_calculated = False

    def update_options(self, options: T) -> None:
        self.contract_settings = options
        if 0 < self.contract_settings.employer_ppk < Decimal('0.015') or 0 < self.contract_settings.employee_ppk < Decimal('0.02'):
            raise ValueError('Employer or employee PPK is too small')
        self.is_calculated = False

    def get_rates(self) -> Rates:
        return self.rates

    def get_options(self) -> ContractSettngs:
        return self.contract_settings

    def calculate_salary_base(self) -> Decimal:
        return self.input_salary

    @abstractmethod
    def calculate_sick_pay(self) -> Decimal:
        pass

    def calculate_salary_gross(self) -> Decimal:
        return self.salary_base+self.salary_sick_pay

    def calculate_social_security_base(self) -> Decimal:
        return self.salary_base

    def calculate_social_security_base_total(self) -> Decimal:
        return self.contract_settings.social_security_base_sum + self.social_security_base

    def calculate_pension_insurance(self) -> Decimal:
        return SalaryUtilities.calculate_pension_or_disability_insurance(
            self.rates.pension_insurance_rate,
            self.social_security_base,
            self.contract_settings.social_security_base_sum,
            self.rates.social_insurance_cap
        )

    def calculate_disability_insurance(self) -> Decimal:
        return SalaryUtilities.calculate_pension_or_disability_insurance(
            self.rates.disability_insurance_rate,
            self.social_security_base,
            self.contract_settings.social_security_base_sum,
            self.rates.social_insurance_cap
        )

    def calculate_sickness_insurance(self) -> Decimal:
        return self.social_security_base * self.rates.sickness_insurance_rate


    def calculate_social_insurance_sum(self) -> Decimal:
        return self.pension_insurance + self.disability_insurance + self.sickness_insurance

    @abstractmethod
    def _calculate_regular_cost(self) -> Decimal:
        pass

    @abstractmethod
    def _calculate_author_rights_cost(self) -> Decimal:
        pass

    def calculate_cost(self) -> Decimal:
        return self.author_rights_cost + self.regular_cost

    def calculate_cost_fifty_total(self) -> Decimal:
        return self.contract_settings.cost_fifty_sum + self.author_rights_cost

    def calculate_health_insurance_base(self) -> Decimal:
        return self.salary_gross - (self.pension_insurance + self.disability_insurance + self.sickness_insurance)

    def calculate_health_insurance(self) -> Decimal:
        return self.health_insurance_base * self.rates.health_insurance_rate

    def calculate_tax_base(self) -> Decimal:
        return self.salary_gross - self.social_insurance_sum - self.cost

    def calculate_tax_base_total(self)  ->Decimal:
        return self.contract_settings.tax_base_sum + self.tax_base

    @abstractmethod
    def calculate_tax(self) -> Decimal:
        pass

    def _add_ppk_tax_and_check_if_is_positive(self,input_tax: Decimal) -> Decimal:
        input_tax += self.ppk_tax
        if input_tax<=0: return Decimal('0.0')
        return input_tax if input_tax > 0 else Decimal('0.0')


    def calculate_ppk_tax(self) -> Decimal:
        return self.social_security_base * self.contract_settings.employer_ppk * self.rates.income_tax[0]


    def calculate_tax_advance_payment(self) -> Decimal:
        return self.tax


    def calculate_salary_deductions(self) -> Decimal:
        return self.contract_settings.salary_deductions

    def calculate_employee_ppk_contribution(self) -> Decimal:
        return self.social_security_base * self.contract_settings.employee_ppk

    def calculate_net_salary(self) -> Decimal:
        return self.salary_gross - (
                self.social_insurance_sum + self.tax_advance_payment + self.employee_ppk_contribution + self.health_insurance + self.salary_deductions)

    def calculate_pension_contribution(self) -> Decimal:
        return SalaryUtilities.calculate_pension_or_disability_insurance(
            self.rates.employer_pension_contribution_rate,
            self.social_security_base,
            self.contract_settings.social_security_base_sum,
            self.rates.social_insurance_cap
        )


    def calculate_disability_contribution(self) -> Decimal:
        return SalaryUtilities.calculate_pension_or_disability_insurance(
            self.rates.employer_disability_contribution_rate,
            self.social_security_base,
            self.contract_settings.social_security_base_sum,
            self.rates.social_insurance_cap
        )


    def calculate_accident_insurance(self) -> Decimal:
        if self.contract_settings.accident_insurance_rate is None:
            return  self.social_security_base * self.rates.accident_insurance_rate
        return self.social_security_base * self.contract_settings.accident_insurance_rate

    def calculate_fp(self) -> Decimal:
        if self.contract_settings.current_month_gross_sum + self.salary_gross >= self.rates.minimum_wage:
            return self.social_security_base * self.rates.fp_rate
        else:
            return Decimal('0')

    def calculate_fgsp(self) -> Decimal:
        return self.social_security_base * self.rates.fgsp_rate

    def calculate_employer_ppk_contribution(self) -> Decimal:
        return self.social_security_base*self.contract_settings.employer_ppk

    def calculate_total_employer_cost(self) -> Decimal:
        return self.salary_gross + self.employer_pension_contribution + self.employer_disability_contribution + self.accident_insurance + self.fp + self.fgsp + self.employer_ppk_contribution


    def calculate(self, salary_base: Decimal, salary_type: SalaryType = SalaryType.GROSS) -> None:
        if self.contract_settings is None:
            raise AttributeError('No contract_settings set to contract, use "update_options" before calculating')
        self.input_salary = salary_base
        if salary_type == SalaryType.GROSS:
            self.calculate_gross()
            self.is_calculated = True
        else:
            self._calculate_net()
            self.is_calculated = True


    def calculate_gross(self) -> None:
        self.salary_base = self.calculate_salary_base().quantize(Decimal('0.01'))
        self.salary_sick_pay = self.calculate_sick_pay().quantize(Decimal('0.01'))
        self.salary_gross= self.calculate_salary_gross().quantize(Decimal('0.01'))
        self.social_security_base = self.calculate_social_security_base().quantize(Decimal('0.01'))
        self.social_security_base_total = self.calculate_social_security_base_total().quantize(Decimal('0.01'))
        self.pension_insurance = self.calculate_pension_insurance().quantize(Decimal('0.01'))
        self.disability_insurance = self.calculate_disability_insurance().quantize(Decimal('0.01'))
        self.sickness_insurance = self.calculate_sickness_insurance().quantize(Decimal('0.01'))
        self.social_insurance_sum = self.calculate_social_insurance_sum().quantize(Decimal('0.01'))
        self.health_insurance_base = self.calculate_health_insurance_base().quantize(Decimal('0.01'))
        self.regular_cost = self._calculate_regular_cost().quantize(Decimal('1'))
        self.author_rights_cost = self._calculate_author_rights_cost().quantize(Decimal('0.01'))
        self.cost = self.calculate_cost().quantize(Decimal('1'))
        self.cost_fifty_total = self.calculate_cost_fifty_total().quantize(Decimal('0.01'))
        self.tax_base = self.calculate_tax_base().quantize(Decimal('1'))
        self.tax_base_total = self.calculate_tax_base_total().quantize(Decimal('0.01'))
        self.ppk_tax = self.calculate_ppk_tax().quantize(Decimal('0.01'))
        self.tax = self._add_ppk_tax_and_check_if_is_positive(self.calculate_tax()).quantize(Decimal('0.01'))
        self.health_insurance = self.calculate_health_insurance().quantize(Decimal('0.01'))
        #self.ub_zdr_odl = self._calculate_ub_zdr_odl()
        self.salary_deductions = self.calculate_salary_deductions().quantize(Decimal('0.01'))
        self.tax_advance_payment = self.calculate_tax_advance_payment().quantize(Decimal('1'), rounding=ROUND_UP)
        self.employee_ppk_contribution = self.calculate_employee_ppk_contribution().quantize(Decimal('0.01'))
        self.employer_pension_contribution = self.calculate_pension_contribution().quantize(Decimal('0.01'))
        self.employer_disability_contribution = self.calculate_disability_contribution().quantize(Decimal('0.01'))
        self.accident_insurance = self.calculate_accident_insurance().quantize(Decimal('0.01'))
        self.fp = self.calculate_fp().quantize(Decimal('0.01'))
        self.fgsp = self.calculate_fgsp().quantize(Decimal('0.01'))
        self.employer_ppk_contribution = self.calculate_employer_ppk_contribution().quantize(Decimal('0.01'))

        self.net_salary = self.calculate_net_salary().quantize(Decimal('0.01'))
        self.total_employer_cost = self.calculate_total_employer_cost().quantize(Decimal('0.01'))


    def _calculate_net(self) -> None:
        wished_netto = self.input_salary #salary_base= brutto_estimate

        while self.net_salary.quantize(Decimal('0.01')) != wished_netto.quantize(Decimal('0.01')) :
            self.input_salary += wished_netto - self.net_salary
            self.calculate_gross()
        self.input_salary = wished_netto




