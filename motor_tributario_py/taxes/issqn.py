from decimal import Decimal
from dataclasses import dataclass
from motor_tributario_py.models import Tributavel
from motor_tributario_py.rules.issqn_rules import ISSQN_BASE_RULE, ISSQN_TAX_RULE
from bkflow_dmn.api import decide_single_table

@dataclass
class ResultadoCalculoIssqn:
    base_calculo: Decimal
    valor: Decimal
    valor_ret_pis: Decimal = Decimal('0')
    valor_ret_cofins: Decimal = Decimal('0')
    valor_ret_csll: Decimal = Decimal('0')
    valor_ret_irrf: Decimal = Decimal('0')
    valor_ret_inss: Decimal = Decimal('0')
    base_calculo_inss: Decimal = Decimal('0')
    base_calculo_irrf: Decimal = Decimal('0')
    base_calculo_pis: Decimal = Decimal('0')
    base_calculo_cofins: Decimal = Decimal('0')
    base_calculo_csll: Decimal = Decimal('0')

class CalculadoraIssqn:
    def __init__(self, tributavel: Tributavel):
        self.tributavel = tributavel

    def calcula(self, calcular_retencoes: bool = False) -> ResultadoCalculoIssqn:
        # Step 1: Calculate Base using Rule
        base_facts = {
            "valor_produto": self.tributavel.valor_produto,
            "quantidade_produto": self.tributavel.quantidade_produto,
            "frete": self.tributavel.frete,
            "seguro": self.tributavel.seguro,
            "outras_despesas": self.tributavel.outras_despesas,
            "tipo_desconto": self.tributavel.tipo_desconto,
            "desconto": self.tributavel.desconto
        }
        
        base_results = decide_single_table(ISSQN_BASE_RULE, base_facts, strict_mode=True)
        if not base_results:
             raise ValueError("No matching ISSQN Base rule found.")
        
        base_calculo = Decimal(str(base_results[0]["base_calculo"]))
        
        # Step 2: Calculate Taxes using Rule with Base
        tax_facts = {
            "base_calculo": base_calculo,
            "calcular_retencoes": calcular_retencoes,
            "percentual_issqn": self.tributavel.percentual_issqn,
            "percentual_ret_pis": self.tributavel.percentual_ret_pis,
            "percentual_ret_cofins": self.tributavel.percentual_ret_cofins,
            "percentual_ret_csll": self.tributavel.percentual_ret_csll,
            "percentual_ret_irrf": self.tributavel.percentual_ret_irrf,
            "percentual_ret_inss": self.tributavel.percentual_ret_inss
        }

        final_results = decide_single_table(ISSQN_TAX_RULE, tax_facts, strict_mode=True)
        if not final_results:
             raise ValueError("No matching ISSQN Tax rule found.")
             
        return ResultadoCalculoIssqn(
            base_calculo=base_calculo,
            valor=Decimal(str(final_results[0]["valor_issqn"])),
            valor_ret_pis=Decimal(str(final_results[0]["valor_ret_pis"])),
            valor_ret_cofins=Decimal(str(final_results[0]["valor_ret_cofins"])),
            valor_ret_csll=Decimal(str(final_results[0]["valor_ret_csll"])),
            valor_ret_irrf=Decimal(str(final_results[0]["valor_ret_irrf"])),
            valor_ret_inss=Decimal(str(final_results[0]["valor_ret_inss"])),
            # C# Test expects BaseCalculoInss, which mirrors BaseCalculo in this context
            base_calculo_inss=base_calculo,
            base_calculo_irrf=base_calculo,
            base_calculo_pis=base_calculo,
            base_calculo_cofins=base_calculo,
            base_calculo_csll=base_calculo
        )
