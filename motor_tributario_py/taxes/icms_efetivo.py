from dataclasses import dataclass
from decimal import Decimal
from motor_tributario_py.models import Tributavel
from motor_tributario_py.rules.icms_efetivo_rules import ICMS_EFETIVO_BASE_RULE, ICMS_EFETIVO_CALC_RULE
from bkflow_dmn.api import decide_single_table

@dataclass
class ResultadoCalculoIcmsEfetivo:
    base_calculo: Decimal
    valor_icms_efetivo: Decimal

class CalculadoraIcmsEfetivo:
    def __init__(self, tributavel: Tributavel):
        self.tributavel = tributavel

    def calcula(self) -> ResultadoCalculoIcmsEfetivo:
        if self.tributavel.percentual_icms_efetivo <= 0:
            return ResultadoCalculoIcmsEfetivo(Decimal('0'), Decimal('0'))

        # Prepare base components
        # If active asset, include IPI in other_expenses component or separate?
        # Rule expects standard components.
        # We can adjust "outras_despesas" passed to rule to include IPI if needed, or pass IPI and let rule sum properly?
        # The Rule currently does: (Val * Qty + Frete + Seg + Outras) ...
        # So we can just add IPI to Outras if needed for this calculation, or modify rule input.
        # I'll modify the input facts.
        
        extra_add = Decimal('0')
        if self.tributavel.is_ativo_imobilizado_ou_uso_consumo:
             extra_add = self.tributavel.valor_ipi
        
        facts = {
            "valor_produto": self.tributavel.valor_produto,
            "quantidade_produto": self.tributavel.quantidade_produto,
            "frete": self.tributavel.frete,
            "seguro": self.tributavel.seguro,
            "outras_despesas": self.tributavel.outras_despesas + extra_add, # Adding IPI here if applicable
            "desconto": self.tributavel.desconto,
            "tipo_desconto": self.tributavel.tipo_desconto,
            "percentual_reducao_icms_efetivo": self.tributavel.percentual_reducao_icms_efetivo
        }
        
        base_results = decide_single_table(ICMS_EFETIVO_BASE_RULE, facts, strict_mode=True)
        if not base_results:
             raise ValueError("No matching ICMS Efetivo Base rule.")
             
        base_calculo = Decimal(str(base_results[0]["base_calculo_efetivo"]))
        
        # Calculate Value
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
