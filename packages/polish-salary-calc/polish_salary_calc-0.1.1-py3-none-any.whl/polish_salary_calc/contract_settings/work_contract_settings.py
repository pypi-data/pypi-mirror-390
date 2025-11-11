
from polish_salary_calc.contract_settings.contract_settings import ContractSettngs
from typing import TypedDict, Self, Unpack
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

class WorkContractType(Enum):
    COMMON = 0
    THE_SAME_COMPANY = 1
class WorkContractOptionsDict(TypedDict):
    work_contract_type: WorkContractType
    is_fifty: bool
    is_a_lump_sum:bool #ryczałt
    # current_month_gross_sum: Decimal
    social_security_base_sum: Decimal
    cost_fifty_sum: Decimal
    tax_base_sum: Decimal
    employee_ppk: Decimal
    employer_ppk: Decimal
    #accident_insurance_rate: Decimal | None
    salary_deductions: Decimal
    name:str

@dataclass
class WorkContractSettings(ContractSettngs):
    work_contract_type: WorkContractType = WorkContractType.COMMON
    is_fifty: bool = False
    is_a_lump_sum: bool = False

    def to_dict(self) ->Unpack[WorkContractOptionsDict]:
        return self.__dict__

    @classmethod
    def from_dict(cls, data: WorkContractOptionsDict) -> Self:
        return cls(**data)

    @classmethod
    def builder(cls) -> 'SettingsBuilder':
        return cls.SettingsBuilder()

    class SettingsBuilder:
        def __init__(self):
            self._options = WorkContractSettings()

        def set_work_contract_type(self, work_contract_type: WorkContractType) -> Self:
            self._options.work_contract_type = work_contract_type
            return self

        def is_fifty(self, is_fifty: bool) -> Self:
            self._options.is_fifty = is_fifty
            return self

        def  is_a_lump_sum(self,  is_a_lump_sum: bool) -> Self:
            self._options. is_a_lump_sum =  is_a_lump_sum
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

        def set_salary_deductions(self, salary_deductions: Decimal) -> Self:
            self._options.salary_deductions = salary_deductions
            return self

        def set_name(self,name: str) -> Self:
            self._options.name = name
            return self

        def build(self) -> 'WorkContractSettings':
            return self._options