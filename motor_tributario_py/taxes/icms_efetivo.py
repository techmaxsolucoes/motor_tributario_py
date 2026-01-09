from dataclasses import dataclass
from decimal import Decimal
from motor_tributario_py.models import Tributavel
from motor_tributario_py.rules.icms_efetivo_rules import (
    ICMS_EFETIVO_PREPROCESSING_RULE,
    ICMS_EFETIVO_BASE_RULE,
    ICMS_EFETIVO_CALC_RULE
)
from bkflow_dmn.api import decide_single_table

@dataclass
class ResultadoCalculoIcmsEfetivo:
    base_calculo: Decimal
    valor_icms_efetivo: Decimal

class CalculadoraIcmsEfetivo:
    def __init__(self, tributavel: Tributavel):
        self.tributavel = tributavel

    def calcula(self) -> ResultadoCalculoIcmsEfetivo:
        # Use DMN to determine if calculation should proceed and handle IPI logic
        preprocessing_facts = {
            "percentual_icms_efetivo": self.tributavel.percentual_icms_efetivo,
            "is_ativo": self.tributavel.is_ativo_imobilizado_ou_uso_consumo
        }
        
        preprocessing_result = decide_single_table(
            ICMS_EFETIVO_PREPROCESSING_RULE,
            preprocessing_facts,
            strict_mode=True
        )
        
        if not preprocessing_result or not preprocessing_result[0]["should_calculate"]:
            return ResultadoCalculoIcmsEfetivo(Decimal('0'), Decimal('0'))
        
        # Apply IPI adjustment based on DMN decision
        outras_despesas_adjusted = self.tributavel.outras_despesas
        if preprocessing_result[0]["ipi_adjustment"] == "add_to_outras_despesas":
            outras_despesas_adjusted = self.tributavel.outras_despesas + self.tributavel.valor_ipi
        
        # Calculate base using DMN
        facts = {
            "valor_produto": self.tributavel.valor_produto,
            "quantidade_produto": self.tributavel.quantidade_produto,
            "frete": self.tributavel.frete,
            "seguro": self.tributavel.seguro,
            "outras_despesas": outras_despesas_adjusted,
            "desconto": self.tributavel.desconto,
            "tipo_desconto": self.tributavel.tipo_desconto,
            "percentual_reducao_icms_efetivo": self.tributavel.percentual_reducao_icms_efetivo
        }
        
        base_results = decide_single_table(ICMS_EFETIVO_BASE_RULE, facts, strict_mode=True)
        if not base_results:
             raise ValueError("No matching ICMS Efetivo Base rule.")
             
        base_calculo = Decimal(str(base_results[0]["base_calculo_efetivo"]))
        
        # Calculate value using DMN
        calc_facts = {
            "dummy": 1,
            "base_calculo_efetivo": base_calculo,
            "percentual_icms_efetivo": self.tributavel.percentual_icms_efetivo
        }
        
        val_results = decide_single_table(ICMS_EFETIVO_CALC_RULE, calc_facts, strict_mode=True)
        if not val_results:
             raise ValueError("No matching ICMS Efetivo Value rule.")
             
        return ResultadoCalculoIcmsEfetivo(
            base_calculo=base_calculo,
            valor_icms_efetivo=Decimal(str(val_results[0]["valor_icms_efetivo"]))
        )
