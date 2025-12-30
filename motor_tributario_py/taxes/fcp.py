from dataclasses import dataclass
from decimal import Decimal
from motor_tributario_py.models import Tributavel
from motor_tributario_py.rules.fcp_rules import FCP_CALC_RULE
from bkflow_dmn.api import decide_single_table

@dataclass
class ResultadoCalculoFcp:
    base_calculo: Decimal
    valor_fcp: Decimal

class CalculadoraFcp:
    def __init__(self, tributavel: Tributavel):
        self.tributavel = tributavel

    def calcula(self, base_calculo_icms: Decimal) -> ResultadoCalculoFcp:
        facts = {
            "dummy": 1,
            "base_calculo_icms": base_calculo_icms,
            "percentual_fcp": self.tributavel.percentual_fcp
        }
        
        results = decide_single_table(FCP_CALC_RULE, facts, strict_mode=True)
        if not results:
             raise ValueError("No matching FCP rule found.")
             
        return ResultadoCalculoFcp(
            base_calculo=base_calculo_icms,
            valor_fcp=Decimal(str(results[0]["valor_fcp"]))
        )
