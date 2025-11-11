from typing import TypedDict, Self, Unpack
from dataclasses import dataclass
from decimal import Decimal

from polish_salary_calc.contract_settings.contract_settings import ContractSettngs


class EmploymentContractDict(TypedDict):
    increased_costs: bool
    cost_fifty_ratio: Decimal
    fp_fgsp: bool
    active_business: bool
    under_26: bool
    sick_pay: Decimal
    current_month_gross_sum: Decimal
    social_security_base_sum: Decimal
    cost_fifty_sum: Decimal
    tax_base_sum: Decimal
    employee_ppk: Decimal
    employer_ppk: Decimal
    accident_insurance_rate: Decimal | None
    salary_deductions: Decimal
    name: str

@dataclass
class EmploymentContractSettings(ContractSettngs):
    increased_costs: bool = False
    cost_fifty_ratio: Decimal = Decimal('0.0')
    fp_fgsp: bool = False
    active_business: bool = False
    under_26: bool = False
    sick_pay: Decimal = Decimal('0.0')
    # current_month_gross_sum: Decimal = Decimal('0.0')
    # social_security_base_sum: Decimal = Decimal('0.0')
    # cost_fifty_sum: Decimal = Decimal('0.0')
    # tax_base_sum: Decimal = Decimal('0.0')
    # employee_ppk: Decimal = Decimal('0.0')
    # employer_ppk: Decimal = Decimal('0.0')
    # accident_insurance_rate: Decimal | None = None

    def to_dict(self) ->Unpack[EmploymentContractDict]:
        return self.__dict__

    @classmethod
    def from_dict(cls, data: EmploymentContractDict) -> Self:
        return cls(**data)

    @classmethod
    def builder(cls) -> 'SettingsBuilder':
        return cls.SettingsBuilder()

    class SettingsBuilder:
        def __init__(self):
            self._options = EmploymentContractSettings()

        def is_increased_costs(self, increased_costs: bool) -> Self:
            self._options.increased_costs = increased_costs
            return self

        def set_cost_fifty_ratio(self, cost_fifty_ratio: Decimal) -> Self:
            self._options.cost_fifty_ratio = cost_fifty_ratio
            return self

        def is_fp_fgsp(self, is_fp_fgsp: bool) -> Self:
            self._options.fp_fgsp = is_fp_fgsp
            return self

        def is_active_business(self, active_business: bool) -> Self:
            self._options.active_business = active_business
            return self

        def is_under_26(self, under_26: bool) -> Self:
            self._options.under_26 = under_26
            return self

        def set_sick_pay(self, sick_pay: Decimal) -> Self:
            self._options.sick_pay = sick_pay
            return self

        def set_current_month_gross_sum(self, current_month_gross_sum: Decimal) -> Self:
            self._options.current_month_gross_sum = current_month_gross_sum
            return self

        def set_social_security_base_sum(self, social_security_base_sum: Decimal) -> Self:
            self._options.social_security_base_sum = social_security_base_sum
            return self

        def set_cost_fifty_sum(self, cost_fifty_sum: Decimal) -> Self:
            self._options.cost_fifty_sum = cost_fifty_sum
            return self

        def set_tax_base_sum(self, tax_base_sum: Decimal) -> Self:
            self._options.tax_base_sum = tax_base_sum
            return self

        def set_employee_ppk(self, employee_ppk: Decimal) -> Self:
            self._options.employee_ppk = employee_ppk
            return self

        def set_employer_ppk(self, employer_ppk: Decimal) -> Self:
            self._options.employer_ppk = employer_ppk
            return self

        def set_accident_insurance_rate(self, accident_insurance_rate: Decimal | None) -> Self:
            self._options.accident_insurance_rate = accident_insurance_rate
            return self

        def set_salary_deductions(self, salary_deductions: Decimal) -> Self:
            self._options.salary_deductions = salary_deductions
            return self

        def set_name(self,name: str) -> Self:
            self._options.name = name
            return self

        def build(self) -> 'EmploymentContractSettings':
            return self._options