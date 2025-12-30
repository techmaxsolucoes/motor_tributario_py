from decimal import Decimal
from dataclasses import dataclass
from motor_tributario_py.models import Tributavel
from motor_tributario_py.rules.icms_st_rules import ICMS_ST_CALC_RULE
from motor_tributario_py.taxes.icms import CalculadoraIcms
from bkflow_dmn.api import decide_single_table

@dataclass
class ResultadoCalculoIcmsSt:
    base_calculo_operacao_propria: Decimal
    valor_icms_proprio: Decimal
    base_calculo_icms_st: Decimal
    valor_icms_st: Decimal

class CalculadoraIcmsSt:
    def __init__(self, tributavel: Tributavel):
        self.tributavel = tributavel

    def calcula(self) -> ResultadoCalculoIcmsSt:
        # 0. Ensure IPI is calculated if needed
        # ICMS ST base includes IPI, so we need to calculate it first
        if self.tributavel.percentual_ipi > 0 and self.tributavel.valor_ipi == 0:
            from motor_tributario_py.taxes.ipi import CalculadoraIpi
            calc_ipi = CalculadoraIpi(self.tributavel)
            res_ipi = calc_ipi.calcula()
            # Round IPI to 2 decimal places before using in ST Base
            self.tributavel.valor_ipi = res_ipi.valor.quantize(Decimal('0.01'))
        
        # 1. Calculate ICMS Proprio (Dependency)
        # We need both Base and Value of ICMS Proprio
        # C# logic uses CalculoBaseIcmsSemIpi, so we must exclude IPI explicitly
        calc_icms = CalculadoraIcms(self.tributavel)
        res_icms = calc_icms.calcula(ignore_ipi=True)
        
        base_calculo_operacao_propria = res_icms.base_calculo
        valor_icms_proprio = res_icms.valor

        # 2. Prepare Facts for ST Rule
        facts = {
            "valor_produto": self.tributavel.valor_produto,
            "quantidade_produto": self.tributavel.quantidade_produto,
            "frete": self.tributavel.frete,
            "seguro": self.tributavel.seguro,
            "outras_despesas": self.tributavel.outras_despesas,
            "valor_ipi": self.tributavel.valor_ipi,
            "tipo_desconto": self.tributavel.tipo_desconto,
            "desconto": self.tributavel.desconto,
            "percentual_reducao_st": self.tributavel.percentual_reducao_st,
            "percentual_mva": self.tributavel.percentual_mva,
            "percentual_icms_st": self.tributavel.percentual_icms_st,
            "valor_icms_proprio": valor_icms_proprio
        }
        
        results = decide_single_table(ICMS_ST_CALC_RULE, facts, strict_mode=True)
        
        if not results:
             raise ValueError("No matching ICMS ST rule found for inputs.")

        base_calculo_st = Decimal(str(results[0]["base_calculo_st"]))
        valor_icms_st = Decimal(str(results[0]["valor_icms_st"]))
        
        return ResultadoCalculoIcmsSt(
            base_calculo_operacao_propria,
            valor_icms_proprio,
            base_calculo_st,
            valor_icms_st
        )
