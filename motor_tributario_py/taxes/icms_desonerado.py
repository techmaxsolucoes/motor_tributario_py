from dataclasses import dataclass
from decimal import Decimal
from motor_tributario_py.models import Tributavel
from motor_tributario_py.rules.icms_desonerado_rules import ICMS_DESONERADO_CALC_RULE
from bkflow_dmn.api import decide_single_table

@dataclass
class ResultadoCalculoIcmsDesonerado:
    valor_icms_desonerado: Decimal

class CalculadoraIcmsDesonerado:
    def __init__(self, tributavel: Tributavel):
        self.tributavel = tributavel

    def calcula(self, base_calculo_icms: Decimal) -> ResultadoCalculoIcmsDesonerado:
        # Guard: If no calculation type is specified, return 0
        if not self.tributavel.tipo_calculo_icms_desonerado:
             return ResultadoCalculoIcmsDesonerado(Decimal('0'))

        # Determine CST Group for DMN
        cst = self.tributavel.cst
        cst_group = "-"
        if cst in ["20", "70"]:
            cst_group = "GroupA"
        elif cst in ["30", "40"]:
            cst_group = "GroupB"
            
        subtotal_produto = self.tributavel.valor_produto * self.tributavel.quantidade_produto

        if self.tributavel.tipo_calculo_icms_desonerado == "BaseSimples":
            cst_group = "-"

        facts = {
            "base_calculo": base_calculo_icms,
            "subtotal_produto": subtotal_produto,
            "tipo_calculo": self.tributavel.tipo_calculo_icms_desonerado,
            "cst_group": cst_group,
            "percentual_icms": self.tributavel.percentual_icms,
            "percentual_reducao": self.tributavel.percentual_reducao
        }
        
        results = decide_single_table(ICMS_DESONERADO_CALC_RULE, facts, strict_mode=True)
        
        if not results:
             # Default to 0 if no rule matches (though likely should match one)
             return ResultadoCalculoIcmsDesonerado(Decimal('0'))
             
        val = Decimal(str(results[0]["valor_icms_desonerado"]))
        return ResultadoCalculoIcmsDesonerado(
            valor_icms_desonerado=val.quantize(Decimal('0.01'))
        )
