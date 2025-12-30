from decimal import Decimal
from dataclasses import dataclass
from motor_tributario_py.models import Tributavel
from motor_tributario_py.rules.ipi_rules import IPI_CALC_RULE
from bkflow_dmn.api import decide_single_table

@dataclass
class ResultadoCalculoIpi:
    base_calculo: Decimal
    valor: Decimal

class CalculadoraIpi:
    def __init__(self, tributavel: Tributavel):
        self.tributavel = tributavel

    def calcula(self) -> ResultadoCalculoIpi:
        # Prepare Fact Context
        facts = {
            "valor_produto": self.tributavel.valor_produto,
            "quantidade_produto": self.tributavel.quantidade_produto,
            "frete": self.tributavel.frete,
            "seguro": self.tributavel.seguro,
            "outras_despesas": self.tributavel.outras_despesas,
            "tipo_desconto": self.tributavel.tipo_desconto,
            "desconto": self.tributavel.desconto,
            "percentual_ipi": self.tributavel.percentual_ipi
        }
        
        results = decide_single_table(IPI_CALC_RULE, facts, strict_mode=True)
        
        if not results:
             raise ValueError("No matching IPI rule found for inputs.")

        base_calculo = Decimal(str(results[0]["base_calculo"]))
        valor = Decimal(str(results[0]["valor_final"]))
        
        return ResultadoCalculoIpi(base_calculo, valor)
