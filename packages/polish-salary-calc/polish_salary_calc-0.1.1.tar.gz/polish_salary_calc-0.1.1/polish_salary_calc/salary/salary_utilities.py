from decimal import Decimal


class SalaryUtilities:
    @staticmethod
    def calculate_pension_or_disability_insurance(
            pension_or_disability_insurance_rate: Decimal,
            social_security_base: Decimal,
            social_security_base_sum: Decimal,
            social_insurance_cap:  Decimal
    ) -> Decimal:
        total_social_security_base_sum = social_security_base_sum + social_security_base
        if total_social_security_base_sum <= social_insurance_cap:
            return social_security_base *pension_or_disability_insurance_rate
        elif total_social_security_base_sum - social_security_base > social_insurance_cap:
            return Decimal('0.0')
        else:
            return (social_security_base - (total_social_security_base_sum - social_insurance_cap))*pension_or_disability_insurance_rate

    @staticmethod
    def calculate_author_rights_cost(
            income_tax_deduction: Decimal,
            cost_ratio: Decimal,
            base: Decimal,
            cost_fifty_sum: Decimal,
            cost_threshold: Decimal
        )-> Decimal:
        #if cost_fifty_ratio>0:
        if base > income_tax_deduction:
            cost_fifty = (base - income_tax_deduction) * cost_ratio
        else:
            cost_fifty = Decimal('0.0')
        total_cost_fifty_sum  = cost_fifty_sum +  cost_fifty
        if total_cost_fifty_sum <= cost_threshold:
            return cost_fifty
        elif total_cost_fifty_sum - cost_fifty < cost_threshold:
            return cost_threshold - (total_cost_fifty_sum -  cost_fifty)
        else:
            return Decimal('0.0')
    #else: return Decimal('0.0')

    @staticmethod
    def calculate_tax(
            income_tax: tuple[Decimal,Decimal],
            tax_base: Decimal,
            tax_base_sum: Decimal,
            tax_threshold: Decimal,
            month_tax_free: Decimal = Decimal('0.0'),
        )-> Decimal:
        tax_base_sum_total = tax_base_sum + tax_base
        if tax_base_sum_total <= tax_threshold:
            out = tax_base * income_tax[0] - month_tax_free
        elif tax_base_sum_total - tax_base <= tax_threshold:
            tax_1 = (tax_threshold - (tax_base_sum_total - tax_base)) * income_tax[0] - month_tax_free
            tax_2 = (tax_base_sum_total - tax_threshold) * income_tax[1]
            out = tax_1 + tax_2
        else:
            out = tax_base * income_tax[1]

        return out if out > 0 else Decimal('0.0')






