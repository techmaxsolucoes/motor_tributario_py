from dataclasses import dataclass
from decimal import Decimal
from motor_tributario_py.models import Tributavel
from motor_tributario_py.rules.ibpt_rules import IBPT_CALC_RULE
from bkflow_dmn.api import decide_single_table

@dataclass
class ResultadoCalculoIbpt:
    base_calculo: Decimal
    tributacao_federal: Decimal
    tributacao_estadual: Decimal
    tributacao_municipal: Decimal
    tributacao_federal_importados: Decimal

class CalculadoraIbpt:
    def __init__(self, tributavel: Tributavel):
        self.tributavel = tributavel

    def calcula(self) -> ResultadoCalculoIbpt:
        facts = {
            "dummy": 1,
            "valor_produto": self.tributavel.valor_produto,
            "quantidade_produto": self.tributavel.quantidade_produto,
            "desconto": self.tributavel.desconto,
            "percentual_federal": self.tributavel.percentual_federal,
            "percentual_estadual": self.tributavel.percentual_estadual,
            "percentual_municipal": self.tributavel.percentual_municipal,
            "percentual_federal_importados": self.tributavel.percentual_federal_importados
        }
        
        results = decide_single_table(IBPT_CALC_RULE, facts, strict_mode=True)
        
        if not results:
             raise ValueError("No matching IBPT rule found.")
             
        # Extract values
        base_calculo = Decimal(str(results[0]["base_calculo"]))
        val_fed = Decimal(str(results[0]["valor_federal"]))
        val_est = Decimal(str(results[0]["valor_estadual"]))
        val_mun = Decimal(str(results[0]["valor_municipal"]))
        val_imp = Decimal(str(results[0]["valor_federal_importados"]))
        
        return ResultadoCalculoIbpt(
            base_calculo=base_calculo,
            tributacao_federal=val_fed,
            tributacao_estadual=val_est,
            tributacao_municipal=val_mun,
            tributacao_federal_importados=val_imp
        )
