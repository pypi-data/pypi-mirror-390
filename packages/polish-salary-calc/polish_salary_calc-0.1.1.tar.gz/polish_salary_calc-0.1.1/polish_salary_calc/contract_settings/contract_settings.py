from dataclasses import dataclass
from decimal import Decimal
from abc import ABC, abstractmethod
from typing import override

from polish_salary_calc.salary.salaryexporter import SalaryExporter,SalaryExporterDict


@dataclass
class ContractSettngs(SalaryExporter,ABC):
    name: str | None = None
    current_month_gross_sum: Decimal = Decimal('0.0')
    social_security_base_sum: Decimal = Decimal('0.0')
    cost_fifty_sum: Decimal = Decimal('0.0')
    tax_base_sum: Decimal = Decimal('0.0')
    employee_ppk: Decimal = Decimal('0.0')
    employer_ppk: Decimal = Decimal('0.0')
    accident_insurance_rate: Decimal | None = None
    salary_deductions: Decimal = Decimal('0.0')

    def __str__(self) -> str:
        return self.to_string()

    @override
    def to_exporter_dict(self) -> SalaryExporterDict:
        return {self.__class__.__name__:self.__dict__}

    @abstractmethod
    def to_dict(self) -> dict[str, str | Decimal | bool]:
        pass

    def options_type(self):
        return self.__class__.__name__