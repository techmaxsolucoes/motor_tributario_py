from dataclasses import dataclass
from decimal import Decimal
from motor_tributario_py.models import Tributavel
from motor_tributario_py.rules.ibs_cbs_rules import IBS_CBS_BASE_RULE, IBS_CALC_RULE, CBS_CALC_RULE, IBS_MUNICIPAL_CALC_RULE
from bkflow_dmn.api import decide_single_table

@dataclass
class ResultadoCalculoIbs:
    base_calculo: Decimal
    valor: Decimal

@dataclass
class ResultadoCalculoCbs:
    base_calculo: Decimal
    valor: Decimal

class CalculadoraBaseIbsCbs:
    """Helper to calculate the common base for IBS and CBS"""
    def __init__(self, tributavel: Tributavel):
        self.tributavel = tributavel

    def calcula_base(self, valor_pis: Decimal, valor_cofins: Decimal, valor_icms: Decimal, valor_issqn: Decimal) -> Decimal:
        facts = {
            "dummy": 1,
            "valor_produto": self.tributavel.valor_produto,
            "quantidade_produto": self.tributavel.quantidade_produto,
            "frete": self.tributavel.frete,
            "seguro": self.tributavel.seguro,
            "outras_despesas": self.tributavel.outras_despesas,
            "desconto": self.tributavel.desconto,
            "desconto": self.tributavel.desconto,
            "ajuste_pis": valor_pis if self.tributavel.somar_pis_na_base_ibs_cbs else -valor_pis,
            "ajuste_cofins": valor_cofins if self.tributavel.somar_cofins_na_base_ibs_cbs else -valor_cofins,
            "ajuste_icms": valor_icms if self.tributavel.somar_icms_na_base_ibs_cbs else -valor_icms,
            "ajuste_issqn": valor_issqn if self.tributavel.somar_issqn_na_base_ibs_cbs else -valor_issqn
        }
        
        results = decide_single_table(IBS_CBS_BASE_RULE, facts, strict_mode=True)
        if not results:
             raise ValueError("No matching IBS/CBS Base rule found.")
             
        return Decimal(str(results[0]["base_calculo_ibs_cbs"]))

class CalculadoraIbs:
    def __init__(self, tributavel: Tributavel):
        self.tributavel = tributavel

    def calcula(self, base_calculo: Decimal) -> ResultadoCalculoIbs:
        facts = {
            "dummy": 1,
            "base_calculo_ibs_cbs": base_calculo,
            "percentual_ibs_uf": self.tributavel.percentual_ibs_uf,
            "percentual_reducao_ibs_uf": self.tributavel.percentual_reducao_ibs_uf
        }
        
        results = decide_single_table(IBS_CALC_RULE, facts, strict_mode=True)
        if not results:
             raise ValueError("No matching IBS rule found.")
             
        val = Decimal(str(results[0]["valor_ibs"]))
        return ResultadoCalculoIbs(
            base_calculo=base_calculo,
            valor=val.quantize(Decimal('0.01'))
        )

class CalculadoraIbsMunicipal:
    def __init__(self, tributavel: Tributavel):
        self.tributavel = tributavel

    def calcula(self, base_calculo: Decimal) -> ResultadoCalculoIbs:
        facts = {
            "dummy": 1,
            "base_calculo_ibs_cbs": base_calculo,
            "percentual_ibs_municipal": self.tributavel.percentual_ibs_municipal,
            "percentual_reducao_ibs_municipal": self.tributavel.percentual_reducao_ibs_municipal
        }
        
        results = decide_single_table(IBS_MUNICIPAL_CALC_RULE, facts, strict_mode=True)
        if not results:
            raise ValueError("No matching IBS Municipal rule found.")
            
        val = Decimal(str(results[0]["valor_ibs_municipal"]))
        return ResultadoCalculoIbs(
            base_calculo=base_calculo,
            valor=val.quantize(Decimal('0.01'))
        )

class CalculadoraCbs:
    def __init__(self, tributavel: Tributavel):
        self.tributavel = tributavel

    def calcula(self, base_calculo: Decimal) -> ResultadoCalculoCbs:
        facts = {
            "dummy": 1,
            "base_calculo_ibs_cbs": base_calculo,
            "percentual_cbs": self.tributavel.percentual_cbs,
            "percentual_reducao_cbs": self.tributavel.percentual_reducao_cbs
        }
        
        results = decide_single_table(CBS_CALC_RULE, facts, strict_mode=True)
        if not results:
             raise ValueError("No matching CBS rule found.")
             
        val = Decimal(str(results[0]["valor_cbs"]))
        return ResultadoCalculoCbs(
            base_calculo=base_calculo,
            valor=val.quantize(Decimal('0.01'))
        )
