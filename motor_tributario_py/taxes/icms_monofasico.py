from dataclasses import dataclass
from decimal import Decimal
from motor_tributario_py.models import Tributavel
from motor_tributario_py.rules.icms_monofasico_rules import ICMS_MONOFASICO_RULE
from bkflow_dmn.api import decide_single_table

@dataclass
class ResultadoCalculoIcmsMonofasico:
    valor_icms_monofasico: Decimal = Decimal('0')
    valor_icms_monofasico_retencao: Decimal = Decimal('0')
    valor_icms_monofasico_operacao: Decimal = Decimal('0')
    valor_icms_monofasico_diferido: Decimal = Decimal('0')
    valor_icms_monofasico_retido_anteriormente: Decimal = Decimal('0')

class CalculadoraIcmsMonofasico:
    def __init__(self, tributavel: Tributavel):
        self.tributavel = tributavel

    def calcula(self) -> ResultadoCalculoIcmsMonofasico:
        # Check if CST is relevant (02, 15, 53, 61)
        if self.tributavel.cst not in ["02", "15", "53", "61"]:
            return ResultadoCalculoIcmsMonofasico()

        facts = {
            "cst": self.tributavel.cst,
            "quantidade_base_calculo_icms_monofasico": self.tributavel.quantidade_base_calculo_icms_monofasico,
            "aliquota_ad_rem_icms": self.tributavel.aliquota_ad_rem_icms,
            "percentual_reducao_aliquota_ad_rem_icms": self.tributavel.percentual_reducao_aliquota_ad_rem_icms,
            "percentual_biodiesel": self.tributavel.percentual_biodiesel,
            "percentual_originario_uf": self.tributavel.percentual_originario_uf,
            "quantidade_base_calculo_icms_monofasico_retido_anteriormente": self.tributavel.quantidade_base_calculo_icms_monofasico_retido_anteriormente,
            "aliquota_ad_rem_icms_retido_anteriormente": self.tributavel.aliquota_ad_rem_icms_retido_anteriormente
        }
        
        results = decide_single_table(ICMS_MONOFASICO_RULE, facts, strict_mode=True)
        if not results:
             raise ValueError(f"No matching ICMS Monofasico rule for CST {self.tributavel.cst}.")
        
        r = results[0]
        return ResultadoCalculoIcmsMonofasico(
            valor_icms_monofasico=Decimal(str(r["valor_icms_monofasico"])),
            valor_icms_monofasico_retencao=Decimal(str(r["valor_icms_monofasico_retencao"])),
            valor_icms_monofasico_operacao=Decimal(str(r["valor_icms_monofasico_operacao"])),
            valor_icms_monofasico_diferido=Decimal(str(r["valor_icms_monofasico_diferido"])),
            valor_icms_monofasico_retido_anteriormente=Decimal(str(r["valor_icms_monofasico_retido_anteriormente"]))
        )
