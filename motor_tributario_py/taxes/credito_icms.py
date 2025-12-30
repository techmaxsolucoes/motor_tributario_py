from dataclasses import dataclass
from decimal import Decimal
from motor_tributario_py.models import Tributavel
from motor_tributario_py.rules.credito_icms_rules import CREDITO_ICMS_CALC_RULE
from bkflow_dmn.api import decide_single_table

@dataclass
class ResultadoCalculoCreditoIcms:
    base_calculo: Decimal
    valor: Decimal

class CalculadoraCreditoIcms:
    def __init__(self, tributavel: Tributavel):
        self.tributavel = tributavel

    def calcula(self, base_calculo: Decimal) -> ResultadoCalculoCreditoIcms:
        facts = {
            "dummy": 1,
            "base_calculo_credito": base_calculo,
            "percentual_credito": self.tributavel.percentual_credito
        }
        
        results = decide_single_table(CREDITO_ICMS_CALC_RULE, facts, strict_mode=True)
        if not results:
             raise ValueError("No matching Credito ICMS rule found.")
             
        return ResultadoCalculoCreditoIcms(
            base_calculo=base_calculo,
            valor=Decimal(str(results[0]["valor_credito_icms"]))
        )
