from typing import TypedDict, Unpack, override
from decimal import Decimal
from dataclasses import dataclass
from typing import Self

from polish_salary_calc.salary.salaryexporter import SalaryExporter

class RatesDict(TypedDict):
    description: str
    pension_insurance_rate: Decimal
    disability_insurance_rate: Decimal
    sickness_insurance_rate: Decimal
    income_tax_deduction: tuple[Decimal, Decimal]
    tax_free_amount: Decimal
    income_tax_deduction_20_50: tuple[Decimal, Decimal]
    income_tax: tuple[Decimal, Decimal]
    line_tax_rate: Decimal
    health_insurance_rate: Decimal
    health_insurance_rate_line_tax: Decimal
    se_lump_health_insurance_base: tuple[Decimal, Decimal]
    health_insurance_lump_rate: tuple[Decimal, Decimal,Decimal]
    #ub_zdr_odl: Decimal
    employer_pension_contribution_rate: Decimal
    employer_disability_contribution_rate: Decimal
    accident_insurance_rate: Decimal
    fp_rate: Decimal
    fgsp_rate: Decimal
    minimum_wage: Decimal
    tax_threshold: Decimal #próg podatkowy
    cost_threshold: Decimal
    standard_social_insurance_base: Decimal
    reduced_social_insurance_base: Decimal
    health_insurance_base: Decimal
    social_insurance_cap: Decimal

@dataclass
class Rates(SalaryExporter):

    description: str = 'Default Rates (2025 year second half)'
    pension_insurance_rate: Decimal = Decimal('0.0976')
    disability_insurance_rate: Decimal = Decimal('0.015')
    sickness_insurance_rate: Decimal = Decimal('0.0245')
    income_tax_deduction: tuple[Decimal,Decimal] = (Decimal('250'), Decimal('300'))
    income_tax_deduction_20_50: tuple[Decimal,Decimal] = (Decimal('0.2'), Decimal('0.5'))
    income_tax: tuple[Decimal,Decimal] = (Decimal('0.12'), Decimal('0.32'))
    line_tax_rate: Decimal = Decimal('0.19')
    tax_free_base : Decimal = Decimal('30000')
    health_insurance_rate: Decimal = Decimal('0.09')
    health_insurance_rate_line_tax: Decimal = Decimal('0.049')
    se_lump_health_insurance_cap: tuple[Decimal, Decimal] = (Decimal('60000.0'), Decimal('300000.0'))
    health_insurance_lump_base: tuple[Decimal, Decimal,Decimal] = (Decimal('5129.18'), Decimal('8549.18'), Decimal('15388.52'))
    employer_pension_contribution_rate: Decimal = Decimal('0.0976')
    employer_disability_contribution_rate: Decimal = Decimal('0.0650')
    accident_insurance_rate: Decimal = Decimal('0.0167')
    fp_rate: Decimal = Decimal('0.0245')
    fgsp_rate: Decimal = Decimal('0.001')
    minimum_wage: Decimal = Decimal('4666')
    tax_threshold: Decimal = Decimal('120000')
    cost_threshold: Decimal = Decimal('120000')
    standard_social_insurance_base: Decimal = Decimal('5203.80')
    reduced_social_insurance_base: Decimal = Decimal('1399.80 ')
    health_insurance_base: Decimal = Decimal('3499.50') #also unregistered cap
    unregistered_cap: Decimal = health_insurance_base
    social_insurance_cap: Decimal = Decimal('260190')

    @property
    def tax_free(self) -> Decimal:
        return self.income_tax[0] * self.tax_free_base

    @property
    def month_tax_free(self) -> Decimal:
        return self.tax_free/12

    @classmethod
    def from_dict(cls,data: RatesDict) -> Self:
        return cls(**data)

    def to_dict(self) -> Unpack[RatesDict]:
        return self.__dict__

    @override
    def to_exporter_dict(self) -> dict[str, dict[str, str | Decimal | bool]]:
        return {self.__class__.__name__:self.to_dict()}

    def __getitem__(self, item: str) -> Decimal | str:
        return getattr(self, item)

    def __setitem__(self, key: str, value: Decimal | str) -> None:
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise KeyError(f'Attribute {key} not found.')

    def __str__(self) -> str:
        return self.to_string()