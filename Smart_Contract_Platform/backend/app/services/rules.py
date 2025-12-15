from dataclasses import dataclass

@dataclass
class PaymentCalc:
    approved_budget: float
    completion_ratio: float
    paid_total: float

    @property
    def payable_limit(self) -> float:
        return max(0.0, self.approved_budget * self.completion_ratio)

    @property
    def max_apply(self) -> float:
        return max(0.0, self.payable_limit - self.paid_total)

def calc_payment(approved_budget: float, completion_ratio: float, paid_total: float) -> PaymentCalc:
    return PaymentCalc(approved_budget=approved_budget, completion_ratio=completion_ratio, paid_total=paid_total)

def performance_bond(tender_price: float) -> float:
    return round(tender_price * 0.10, 2)

def enforce_contract_price_equals_tender(tender_price: float, contract_price: float) -> None:
    if abs(tender_price - contract_price) > 1e-6:
        raise ValueError("合同价必须与中标价一致（刚性规则）")
