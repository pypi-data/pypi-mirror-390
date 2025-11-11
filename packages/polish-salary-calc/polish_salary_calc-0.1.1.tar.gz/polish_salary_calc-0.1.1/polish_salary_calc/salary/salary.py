from datetime import datetime
from pathlib import Path

import pandas as pd

from polish_salary_calc.salary.salaryexporter import SalaryExporter
from polish_salary_calc.contract_settings.contract_settings import ContractSettngs
from decimal import Decimal
from enum import Enum

from polish_salary_calc.rates.rates import Rates

from typing import Self, TypedDict, override, Unpack


class SalaryType(Enum):
    GROSS = 1
    NET = 2

class SalaryDict(TypedDict):
    name: str
    created_datetime:datetime
    salary_base: Decimal
    salary_sick_pay: Decimal
    salary_gross: Decimal
    social_security_base: Decimal
    social_security_base_total: Decimal
    pension_insurance: Decimal
    disability_insurance: Decimal
    sickness_insurance: Decimal
    social_insurance_sum: Decimal
    cost: Decimal
    cost_fifty_total: Decimal
    regular_cost: Decimal
    author_rights_cost: Decimal
    health_insurance_base: Decimal
    tax_base: Decimal
    tax_base_total: Decimal
    tax: Decimal
    health_insurance: Decimal
    ppk_tax: Decimal
    tax_advance_payment: Decimal
    salary_deductions: Decimal
    employee_ppk_contribution: Decimal
    net_salary: Decimal
    employer_pension_contribution: Decimal
    employer_disability_contribution: Decimal
    accident_insurance: Decimal
    fp: Decimal
    fgsp: Decimal
    employer_ppk_contribution: Decimal
    total_employer_cost: Decimal
    total_markups: Decimal
    brutto_ratio: Decimal
    net_ratio: Decimal
    total_markups_ratio: Decimal

class Salary[T: ContractSettngs](SalaryExporter):
    def __init__(self, rates: Rates , contract_settings: T ) -> None:

        self.input_salary = Decimal('0')

        self._created_datetime = datetime.now()

        self.rates: Rates = rates
        self.contract_settings: T = contract_settings

        if self.contract_settings.name is None:
            self.name = self._generate_name_from_date()
        else:
            self.name = self.contract_settings.name

        if 0 < self.contract_settings.employer_ppk < Decimal('0.015') or 0 < self.contract_settings.employee_ppk < Decimal('0.02'):
            raise ValueError('Employer or employee PPK rate is too small')


        self.salary_base: Decimal = Decimal('0.0') #płaca podstawowa
        self.salary_sick_pay: Decimal = Decimal('0.0') #chorobowe
        self.salary_gross: Decimal= Decimal('0.0')  #brutto
        self.social_security_base: Decimal= Decimal('0.0') #podst ub społ
        self.social_security_base_total: Decimal= Decimal('0.0')
        self.pension_insurance: Decimal= Decimal('0.0') #ub emeryt
        self.disability_insurance: Decimal= Decimal('0.0') #ub rent
        self.sickness_insurance: Decimal= Decimal('0.0') #chorobowe
        self.social_insurance_sum: Decimal= Decimal('0.0') #uma ub społ
        self.cost: Decimal= Decimal('0.0')
        self.cost_fifty_total: Decimal= Decimal('0.0')
        self.regular_cost: Decimal= Decimal('0.0')
        self.author_rights_cost: Decimal= Decimal('0.0') #koszt praw autorskich (50%)
        self.health_insurance_base: Decimal= Decimal('0.0') #podst zdrowotne
        self.tax_base: Decimal= Decimal('0.0') #podstawa podatku
        self.tax_base_total = Decimal('0.0')
        self.tax: Decimal= Decimal('0.0') # podatek
        self.health_insurance: Decimal= Decimal('0.0')
        #self.ub_zdr_odl: Decimal= Decimal('0.0')
        self.ppk_tax: Decimal= Decimal('0.0')
        self.tax_advance_payment: Decimal= Decimal('0.0') #zaliczka podatku
        self.salary_deductions: Decimal= Decimal('0.0') #potrącenia wypłaty
        self.employee_ppk_contribution: Decimal= Decimal('0.0')
        self.net_salary: Decimal= Decimal('0.0')
        self.employer_pension_contribution: Decimal= Decimal('0.0') #ub emeryt prac
        self.employer_disability_contribution: Decimal= Decimal('0.0') #ub rent prac
        self.accident_insurance: Decimal= Decimal('0.0') #ub wyp prac
        self.fp: Decimal= Decimal('0.0')
        self.fgsp: Decimal= Decimal('0.0')
        self.employer_ppk_contribution: Decimal= Decimal('0.0') #ppk pracodawca
        self.total_employer_cost: Decimal= Decimal('0.0') #brutto brutto

        self.is_calculated: bool = False

        self.salary_compared_contract: Salary | None = None
        self.salary_difference: Salary | None = None
        self.is_compared: bool = False

    def _generate_name_from_date(self) -> str:
        return f'{self.__class__.__name__}{self._created_datetime:%Y_%m_%d_%H%M%S}'

    @property
    def created_datetime(self) -> str:
        return self._created_datetime.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def total_markups(self) -> Decimal:
        return (self.total_employer_cost - self.net_salary).quantize(Decimal('0.01'))

    @property
    def gross_ratio(self) -> Decimal:
        if self.total_employer_cost == 0: return Decimal('0.0')
        return ((self.salary_gross / self.total_employer_cost) * 100).quantize(Decimal('0.01'))

    @property
    def net_ratio(self) -> Decimal:
        if self.total_employer_cost == 0: return Decimal('0.0')
        return ((self.net_salary / self.total_employer_cost) * 100).quantize(Decimal('0.01'))

    @property
    def total_markups_ratio(self) -> Decimal:
        if self.total_employer_cost == 0: return Decimal('0.0')
        return ((self.total_markups / self.total_employer_cost) * 100).quantize(Decimal('0.01'))

    def to_dict(self) -> Unpack[SalaryDict]:
        return {                                  "name": self.name,
                                                  "contract_type": self.get_contract_type(),
                                                  "created_datetime": self.created_datetime,
                                                  "salary_base": self.salary_base,
                                                  "salary_sick_pay": self.salary_sick_pay,
                                                  "salary_gross": self.salary_gross,
                                                  "social_security_base": self.social_security_base,
                                                  # "social_security_base_total": self.social_security_base_total,
                                                  "pension_insurance": self.pension_insurance,
                                                  "disability_insurance": self.disability_insurance,
                                                  "sickness_insurance": self.sickness_insurance,
                                                  "social_insurance_sum": self.social_insurance_sum, "cost": self.cost,
                                                  # "cost_fifty_total": self.cost_fifty_total,
                                                  "regular_cost": self.regular_cost,
                                                  "author_rights_cost": self.author_rights_cost,
                                                  "health_insurance_base": self.health_insurance_base,
                                                  "tax_base": self.tax_base,
                                                  # "tax_base_total": self.tax_base_total,
                                                  "tax": self.tax, "health_insurance": self.health_insurance,
                                                  "ppk_tax": self.ppk_tax,
                                                  "tax_advance_payment": self.tax_advance_payment,
                                                  "salary_deductions": self.salary_deductions,
                                                  "employee_ppk_contribution": self.employee_ppk_contribution,
                                                  "net_salary": self.net_salary,
                                                  "employer_pension_contribution": self.employer_pension_contribution,
                                                  "employer_disability_contribution": self.employer_disability_contribution,
                                                  "accident_insurance": self.accident_insurance, "fp": self.fp,
                                                  "fgsp": self.fgsp,
                                                  "employer_ppk_contribution": self.employer_ppk_contribution,
                                                  "total_employer_cost": self.total_employer_cost,
                                                  "total_markups": self.total_markups,
                                                  # "gross_ratio": self.gross_ratio,
                                                  "net_ratio": self.net_ratio,
                                                  "total_markups_ratio": self.total_markups_ratio}

    @override
    def to_exporter_dict(self, row_name: str | None = None)-> dict[str,dict[str, str | Decimal | bool]]:
        if row_name is None:
            row_name = self.name
        output:  dict[str, dict[str, str | Decimal | bool]] = {row_name:self.to_dict()}
        # if self.is_compared and self.salary_compared_contract is not None and self.salary_difference is not None:
        #     output["COMPARED"] = self.salary_compared_contract.to_dict()
        #     output["DIFFERANCE"] = self.salary_difference.to_dict()
        return output

    def to_compared_dict(self, row_name: str | None = None) ->  dict[str,dict[str, str | Decimal | bool]]:
        if row_name is None:
            row_name = self.name
        output: dict[str, dict[str, str | Decimal | bool]] = {row_name: self.to_dict()}
        if self.is_compared and self.salary_compared_contract is not None and self.salary_difference is not None:
            output["COMPARED"] = self.salary_compared_contract.to_dict()
            output["DIFFERANCE"] = self.salary_difference.to_dict()
        return output

    def to_compared_string(self) -> str:
        return self.to_string(self.to_compared_dict())

    def get_compared_data_frame(self) -> pd.DataFrame:
        return self.get_data_frame(self.to_compared_dict())

    def to_compared_excel(self,path: Path) -> None:
        self.to_excel(path,self.to_compared_dict())

    def to_compared_csv(self,path: Path) -> None:
        self.to_csv(path,self.to_compared_dict())

    def to_compared_json(self,path: Path) -> None:
        self.to_json(path,self.to_compared_dict())

    def get_contract_type(self) -> str:
        return self.__class__.__name__

    def compare_to(self, salary_compared_contract: "Salary") -> "Salary":
        self.salary_compared_contract = salary_compared_contract
        # self.salary_difference = Salary(self.rates,self.contract_settings)
        self.salary_difference = self - self.salary_compared_contract
        self.salary_difference.name = "DIFFERENCE"
        self.is_compared = True
        return self.salary_difference

    def __str__(self) -> str:
        return self.to_string()

    def __eq__(self, other:object) -> bool:
        if not isinstance(other, Salary):
            return NotImplemented
        return self.net_salary == other.net_salary
    def __le__(self, other:object) -> bool:
        if not isinstance(other, Salary):
            return NotImplemented
        return self.net_salary <= other.net_salary
    def __ge__(self, other:object) -> bool:
        if not isinstance(other, Salary):
            return NotImplemented
        return self.net_salary >= other.net_salary

    def __add__(self, other:Self) -> "Salary":
        output:Salary = Salary(self.rates,self.contract_settings)
        output.salary_base = self.salary_base + other.salary_base
        output.salary_sick_pay = self.salary_sick_pay + other.salary_sick_pay
        output.salary_gross = self.salary_gross +other.salary_gross
        output.social_security_base = self.social_security_base + other.social_security_base
        output.social_security_base_total = other.contract_settings.social_security_base_sum + self.social_security_base
        output.pension_insurance = self.pension_insurance + other.pension_insurance
        output.disability_insurance = self.disability_insurance + other.disability_insurance
        output.sickness_insurance = self.sickness_insurance + other.sickness_insurance
        output.social_insurance_sum = self.social_insurance_sum + other.social_insurance_sum
        output.author_rights_cost = self.author_rights_cost + other.author_rights_cost
        output.cost = self.cost + other.cost
        output.cost_fifty_total = other.contract_settings.cost_fifty_sum + self.author_rights_cost
        output.regular_cost = self.regular_cost + other.regular_cost
        output.author_rights_cost = self.author_rights_cost + other.author_rights_cost
        output.health_insurance_base = self.health_insurance_base + other.health_insurance_base
        output.tax_base = self.tax_base + other.tax_base
        output.tax_base_total = other.contract_settings.tax_base_sum + self.tax_base
        output.tax = self.tax + other.tax
        output.health_insurance = self.health_insurance + other.health_insurance
        output.ppk_tax = self.ppk_tax + other.ppk_tax
        output.tax_advance_payment = self.tax_advance_payment + other.tax_advance_payment
        output.salary_deductions = self.salary_deductions + other.salary_deductions
        output.employee_ppk_contribution = self.employee_ppk_contribution + other.employee_ppk_contribution
        output.net_salary = self.net_salary + other.net_salary
        output.employer_pension_contribution = self.employer_pension_contribution + other.employer_pension_contribution
        output.employer_disability_contribution = self.employer_disability_contribution + other.employer_disability_contribution
        output.accident_insurance = self.accident_insurance + other.accident_insurance
        output.fp = self.fp + other.fp
        output.fgsp = self.fgsp + other.fgsp
        output.employer_ppk_contribution = self.employer_ppk_contribution + other.employer_ppk_contribution
        output.total_employer_cost = self.total_employer_cost + other.total_employer_cost
        return output

    def __iadd__(self, other: Self) -> Self:
        self.salary_base = self.salary_base + other.salary_base
        self.salary_sick_pay = self.salary_sick_pay + other.salary_sick_pay
        self.salary_gross = self.salary_gross + other.salary_gross
        self.social_security_base = self.social_security_base + other.social_security_base
        self.social_security_base_total = other.contract_settings.social_security_base_sum + self.social_security_base
        self.pension_insurance = self.pension_insurance + other.pension_insurance
        self.disability_insurance = self.disability_insurance + other.disability_insurance
        self.sickness_insurance = self.sickness_insurance + other.sickness_insurance
        self.social_insurance_sum = self.social_insurance_sum + other.social_insurance_sum
        self.author_rights_cost = self.author_rights_cost + other.author_rights_cost
        self.cost = self.cost + other.cost
        self.cost_fifty_total = other.contract_settings.cost_fifty_sum + self.author_rights_cost
        self.regular_cost = self.regular_cost + other.regular_cost
        self.health_insurance_base = self.health_insurance_base + other.health_insurance_base
        self.tax_base = self.tax_base + other.tax_base
        self.tax_base_total = other.contract_settings.tax_base_sum + self.tax_base
        self.tax = self.tax + other.tax
        self.health_insurance = self.health_insurance + other.health_insurance
        self.ppk_tax = self.ppk_tax + other.ppk_tax
        self.tax_advance_payment = self.tax_advance_payment + other.tax_advance_payment
        self.salary_deductions = self.salary_deductions + other.salary_deductions
        self.employee_ppk_contribution = self.employee_ppk_contribution + other.employee_ppk_contribution
        self.net_salary = self.net_salary + other.net_salary
        self.employer_pension_contribution = self.employer_pension_contribution + other.employer_pension_contribution
        self.employer_disability_contribution = self.employer_disability_contribution + other.employer_disability_contribution
        self.accident_insurance = self.accident_insurance + other.accident_insurance
        self.fp = self.fp + other.fp
        self.fgsp = self.fgsp + other.fgsp
        self.employer_ppk_contribution = self.employer_ppk_contribution + other.employer_ppk_contribution
        self.total_employer_cost = self.total_employer_cost + other.total_employer_cost
        return self

    def __sub__(self, other:Self) -> "Salary":
        output:Salary = Salary(self.rates,self.contract_settings)
        output.salary_base = self.salary_base - other.salary_base
        output.salary_sick_pay = self.salary_sick_pay - other.salary_sick_pay
        output.salary_gross = self.salary_gross - other.salary_gross
        output.social_security_base = self.social_security_base - other.social_security_base
        output.social_security_base_total = other.contract_settings.social_security_base_sum - self.social_security_base
        output.pension_insurance = self.pension_insurance - other.pension_insurance
        output.disability_insurance = self.disability_insurance - other.disability_insurance
        output.sickness_insurance = self.sickness_insurance - other.sickness_insurance
        output.social_insurance_sum = self.social_insurance_sum - other.social_insurance_sum
        output.author_rights_cost = self.author_rights_cost - other.author_rights_cost
        output.cost = self.cost - other.cost
        output.cost_fifty_total = other.contract_settings.cost_fifty_sum - self.author_rights_cost
        output.regular_cost = self.regular_cost - other.regular_cost
        output.author_rights_cost = self.author_rights_cost - other.author_rights_cost
        output.health_insurance_base = self.health_insurance_base - other.health_insurance_base
        output.tax_base = self.tax_base - other.tax_base
        output.tax_base_total = other.contract_settings.tax_base_sum - self.tax_base
        output.tax = self.tax - other.tax
        output.health_insurance = self.health_insurance - other.health_insurance
        output.ppk_tax = self.ppk_tax - other.ppk_tax
        output.tax_advance_payment = self.tax_advance_payment - other.tax_advance_payment
        output.salary_deductions = self.salary_deductions - other.salary_deductions
        output.employee_ppk_contribution = self.employee_ppk_contribution - other.employee_ppk_contribution
        output.net_salary = self.net_salary - other.net_salary
        output.employer_pension_contribution = self.employer_pension_contribution - other.employer_pension_contribution
        output.employer_disability_contribution = self.employer_disability_contribution - other.employer_disability_contribution
        output.accident_insurance = self.accident_insurance - other.accident_insurance
        output.fp = self.fp - other.fp
        output.fgsp = self.fgsp - other.fgsp
        output.employer_ppk_contribution = self.employer_ppk_contribution - other.employer_ppk_contribution
        output.total_employer_cost = self.total_employer_cost - other.total_employer_cost
        return output

    def __isub__(self, other: Self) -> Self:
        self.salary_base = self.salary_base - other.salary_base
        self.salary_sick_pay = self.salary_sick_pay - other.salary_sick_pay
        self.salary_gross = self.salary_gross - other.salary_gross
        self.social_security_base = self.social_security_base - other.social_security_base
        self.social_security_base_total = other.contract_settings.social_security_base_sum - self.social_security_base
        self.pension_insurance = self.pension_insurance - other.pension_insurance
        self.disability_insurance = self.disability_insurance - other.disability_insurance
        self.sickness_insurance = self.sickness_insurance - other.sickness_insurance
        self.social_insurance_sum = self.social_insurance_sum - other.social_insurance_sum
        self.author_rights_cost = self.author_rights_cost - other.author_rights_cost
        self.cost = self.cost - other.cost
        self.cost_fifty_total = other.contract_settings.cost_fifty_sum - self.author_rights_cost
        self.regular_cost = self.regular_cost - other.regular_cost
        self.health_insurance_base = self.health_insurance_base - other.health_insurance_base
        self.tax_base = self.tax_base - other.tax_base
        self.tax_base_total = other.contract_settings.tax_base_sum - self.tax_base
        self.tax = self.tax - other.tax
        self.health_insurance = self.health_insurance - other.health_insurance
        self.ppk_tax = self.ppk_tax - other.ppk_tax
        self.tax_advance_payment = self.tax_advance_payment - other.tax_advance_payment
        self.salary_deductions = self.salary_deductions - other.salary_deductions
        self.employee_ppk_contribution = self.employee_ppk_contribution - other.employee_ppk_contribution
        self.net_salary = self.net_salary - other.net_salary
        self.employer_pension_contribution = self.employer_pension_contribution - other.employer_pension_contribution
        self.employer_disability_contribution = self.employer_disability_contribution - other.employer_disability_contribution
        self.accident_insurance = self.accident_insurance - other.accident_insurance
        self.fp = self.fp - other.fp
        self.fgsp = self.fgsp - other.fgsp
        self.employer_ppk_contribution = self.employer_ppk_contribution - other.employer_ppk_contribution
        self.total_employer_cost = self.total_employer_cost - other.total_employer_cost
        return self
