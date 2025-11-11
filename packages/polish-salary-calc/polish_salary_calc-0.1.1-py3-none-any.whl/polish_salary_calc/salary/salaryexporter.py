from decimal import Decimal
from pathlib import Path
from abc import ABC, abstractmethod

import pandas as pd

SalaryExporterDict = dict[str, dict[str, str | Decimal | bool]]

class SalaryExporter(ABC):

    @abstractmethod
    def to_exporter_dict(self) -> SalaryExporterDict:
        pass

    def to_string(self, input_data: SalaryExporterDict | None = None) -> str:
        if input_data is None: input_data = self.to_exporter_dict()
        if len(input_data.keys()) <= 1:
            return SalaryExporter.print_dict(input_data)
        else:
            return str(self.get_data_frame(input_data, columns = [
            "salary_gross", "social_insurance_sum", "cost", "health_insurance", "tax_advance_payment",
            "net_salary", "employer_pension_contribution", "employer_disability_contribution",
            "accident_insurance", "fp", "fgsp", "total_employer_cost"]))

    def get_data_frame(self,
                       input_data: SalaryExporterDict | None = None,
                       rows: list[str] | None = None, columns: list[str] | None = None
                       ) -> pd.DataFrame:
        if input_data is None:
            input_data = self.to_exporter_dict()
        if rows is not None:
            input_data = {k:v for k,v in input_data.items() if k in rows}
        return SalaryExporter._generate_data_frame_from_contract_summary(input_data, columns)

    def to_excel(self, path: Path, input_data: SalaryExporterDict | None = None)->None:
        if input_data is None: input_data = self.to_exporter_dict()
        first_items = list(input_data.items())[0][0] #or {'contract_type':"None"}
        self.get_data_frame(input_data).to_excel(path,sheet_name=first_items)

    def to_json(self, path: Path, input_data: SalaryExporterDict | None = None)->None:
        if input_data is None: input_data = self.to_exporter_dict()
        self.get_data_frame(input_data).to_json(path, indent=4, index=True,orient="index")

    def to_csv(self, path: Path, input_data: SalaryExporterDict | None = None)->None:
        if input_data is None: input_data = self.to_exporter_dict()
        self.get_data_frame(input_data).to_csv(path,sep=";", index=True)

    @staticmethod
    def _generate_data_frame_from_contract_summary(
                                                contract_summary_dict: dict[str, dict[str, str | Decimal | bool]],
                                                columns: list | None = None
                                              ) -> pd.DataFrame:

        first_key = list(contract_summary_dict.keys())[0]
        if columns is None:
            columns = list(contract_summary_dict.get(first_key).keys())
        data = list(contract_summary_dict.values())
        index = list(contract_summary_dict.keys())

        df = pd.DataFrame(data,index=index,columns=columns)
        return df

    @staticmethod
    def print_dict(input_dict: dict) -> str:
        if input_dict is None:
            raise ValueError("Input data to show onscreen is None!")
        first_key = list(input_dict.keys())[0]
        out = [first_key]
        max_len = 0
        for key, value in input_dict.get(first_key).items():
            if isinstance(value,tuple):
                value = "  ".join(str(v) for v in value)
            max_len = max(max_len, len(key)+len(str(value)))

        for key, value in input_dict.get(first_key).items():
            if isinstance(value,tuple):
                value =" ".join(str(v) for v in value)
                value = "("+value+")"
            key = key.upper().replace("_", " ")

            out.append(f"{key}{"":.>{max_len-len(key)-len(str(value))+2}}{str(value)}")
        return "\n".join(out)