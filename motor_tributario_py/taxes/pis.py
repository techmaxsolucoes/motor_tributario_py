from decimal import Decimal
from dataclasses import dataclass
from motor_tributario_py.models import Tributavel
from motor_tributario_py.rules.pis_cofins_rules import PIS_COFINS_CALC_RULE 
from motor_tributario_py.taxes.icms import CalculadoraIcms
from bkflow_dmn.api import decide_single_table

@dataclass
class ResultadoCalculoPis:
    base_calculo: Decimal
    valor: Decimal

class CalculadoraPis:
    def __init__(self, tributavel: Tributavel):
        self.tributavel = tributavel

    def calcula(self) -> ResultadoCalculoPis:
        # Dependency: Calculate ICMS if needed
        valor_icms = Decimal('0')
        if self.tributavel.deduz_icms_da_base_de_pis_cofins:
             # This is a dependency, but logic of subtraction is in Rule
             icms_result = CalculadoraIcms(self.tributavel).calcula()
             valor_icms = icms_result.valor.quantize(Decimal('0.01'))

        facts = {
            "valor_produto": self.tributavel.valor_produto,
            "quantidade_produto": self.tributavel.quantidade_produto,
            "frete": self.tributavel.frete,
            "seguro": self.tributavel.seguro,
            "outras_despesas": self.tributavel.outras_despesas,
            "valor_ipi": self.tributavel.valor_ipi,
            "is_ativo": self.tributavel.is_ativo_imobilizado_ou_uso_consumo,
            "valor_icms": valor_icms,
            "deduz_icms": self.tributavel.deduz_icms_da_base_de_pis_cofins,
            "tipo_desconto": self.tributavel.tipo_desconto,
            "desconto": self.tributavel.desconto,
            "percentual_reducao": self.tributavel.percentual_reducao_pis,
            "percentual_tax": self.tributavel.percentual_pis
        }
        
        results = decide_single_table(PIS_COFINS_CALC_RULE, facts, strict_mode=True)
        
        if not results:
             raise ValueError("No matching PIS rule found for inputs.")

        base_calculo = Decimal(str(results[0]["base_calculo"]))
        valor = Decimal(str(results[0]["valor_final"]))
        
        return ResultadoCalculoPis(base_calculo, valor.quantize(Decimal('0.01')))
