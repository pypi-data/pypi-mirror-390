
from polish_salary_calc.contract_settings.contract_settings import ContractSettngs
from typing import TypedDict, Self, Unpack
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

class MandateContractType(Enum):
    COMMON = 1
    THE_SAME_COMPANY = 2
    OTHER_COMPANY_MIN_SALARY=3
    UNDER_26_AND_STUDENT =4

class MandateContractOptionsDict(TypedDict):
    mandate_contract_type: MandateContractType
    is_fifty: bool
    fp: bool
    fgsp: bool
    is_a_lump_sum:bool #ryczałt
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
class MandateContractSettings(ContractSettngs):
    mandate_contract_type: MandateContractType = MandateContractType.COMMON
    is_fifty: bool = False
    fp: bool = False
    fgsp: bool = False
    is_a_lump_sum: bool = False
    # current_month_gross_sum: Decimal = Decimal('0.0')
    # social_security_base_sum: Decimal = Decimal('0.0')
    # cost_fifty_sum: Decimal = Decimal('0.0')
    # tax_base_sum: Decimal = Decimal('0.0')
    # employee_ppk: Decimal = Decimal('0.0')
    # employer_ppk: Decimal = Decimal('0.0')
    # accident_insurance_rate: Decimal | None = None

    def to_dict(self) ->Unpack[MandateContractOptionsDict]:
        return self.__dict__

    @classmethod
    def from_dict(cls, data: MandateContractOptionsDict) -> Self:
        return cls(**data)

    @classmethod
    def builder(cls) -> 'SettingsBuilder':
        return cls.SettingsBuilder()

    class SettingsBuilder:
        def __init__(self):
            self._options = MandateContractSettings()

        def set_mandate_contract_type(self, contract_type: MandateContractType) -> Self:
            self._options.mandate_contract_type = contract_type
            return self
        def is_fifty(self, is_fifty: bool) -> Self:
            self._options.is_fifty = is_fifty
            return self
        def is_fp(self, is_fp: bool) -> Self:
            self._options.fp = is_fp
            return self
        def is_fgsp(self, is_fgsp: bool) -> Self:
            self._options.fgsp = is_fgsp
            return self
        def  is_a_lump_sum(self,  is_a_lump_sum: bool) -> Self:
            self._options. is_a_lump_sum =  is_a_lump_sum
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
        def build(self) -> 'MandateContractSettings':
            return self._options