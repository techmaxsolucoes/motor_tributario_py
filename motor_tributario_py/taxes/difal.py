from decimal import Decimal
from dataclasses import dataclass
from motor_tributario_py.models import Tributavel
from motor_tributario_py.rules.difal_rules import DIFAL_CALC_RULE
from bkflow_dmn.api import decide_single_table

@dataclass
class ResultadoCalculoDifal:
    base_calculo: Decimal
    fcp: Decimal
    difal: Decimal
    valor_icms_destino: Decimal
    valor_icms_origem: Decimal

class CalculadoraDifal:
    def __init__(self, tributavel: Tributavel):
        self.tributavel = tributavel

    def calcula(self) -> ResultadoCalculoDifal:
        facts = {
            "valor_produto": self.tributavel.valor_produto,
            "quantidade_produto": self.tributavel.quantidade_produto,
            "frete": self.tributavel.frete,
            "seguro": self.tributavel.seguro,
            "outras_despesas": self.tributavel.outras_despesas,
            "valor_ipi": self.tributavel.valor_ipi,
            "is_ativo": self.tributavel.is_ativo_imobilizado_ou_uso_consumo,
            "tipo_desconto": self.tributavel.tipo_desconto,
            "desconto": self.tributavel.desconto,
            "percentual_fcp": self.tributavel.percentual_fcp,
            "percentual_difal_interna": self.tributavel.percentual_difal_interna,
            "percentual_difal_interestadual": self.tributavel.percentual_difal_interestadual
        }
        
        results = decide_single_table(DIFAL_CALC_RULE, facts, strict_mode=True)
        
        if not results:
             raise ValueError("No matching DIFAL rule found for inputs.")

        base_calculo = Decimal(str(results[0]["base_calculo"]))
        valor_fcp = Decimal(str(results[0]["valor_fcp"]))
        valor_difal = Decimal(str(results[0]["valor_difal"]))
        valor_icms_destino = Decimal(str(results[0]["valor_icms_destino"]))
        valor_icms_origem = Decimal(str(results[0]["valor_icms_origem"]))
        
        return ResultadoCalculoDifal(
            base_calculo,
            valor_fcp,
            valor_difal,
            valor_icms_destino,
            valor_icms_origem
        )
