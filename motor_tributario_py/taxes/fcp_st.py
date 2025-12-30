from dataclasses import dataclass
from decimal import Decimal
from motor_tributario_py.models import Tributavel
from motor_tributario_py.rules.fcp_st_rules import FCP_ST_CALC_RULE, FCP_ST_RETIDO_CALC_RULE
from bkflow_dmn.api import decide_single_table

@dataclass
class ResultadoCalculoFcpSt:
    base_calculo_fcp_st: Decimal
    valor_fcp_st: Decimal

@dataclass
class ResultadoCalculoFcpStRetido:
    base_calculo: Decimal
    valor_fcp_st_retido: Decimal

class CalculadoraFcpSt:
    def __init__(self, tributavel: Tributavel):
        self.tributavel = tributavel

    def calcula(self, valor_ipi: Decimal = Decimal('0')) -> ResultadoCalculoFcpSt:
        facts = {
            "valor_produto": self.tributavel.valor_produto,
            "quantidade_produto": self.tributavel.quantidade_produto,
            "frete": self.tributavel.frete,
            "seguro": self.tributavel.seguro,
            "outras_despesas": self.tributavel.outras_despesas,
            "desconto": self.tributavel.desconto,
            "tipo_desconto": self.tributavel.tipo_desconto,
            "valor_ipi": valor_ipi,
            "percentual_mva": self.tributavel.percentual_mva,
            "percentual_fcp_st": self.tributavel.percentual_fcp_st
        }
        
        results = decide_single_table(FCP_ST_CALC_RULE, facts, strict_mode=True)
        
        if not results:
             raise ValueError("No matching FCP ST rule found.")
        
        return ResultadoCalculoFcpSt(
            base_calculo_fcp_st=Decimal(str(results[0]["base_calculo_fcp_st"])),
            valor_fcp_st=Decimal(str(results[0]["valor_fcp_st"]))
        )

class CalculadoraFcpStRetido:
    def __init__(self, tributavel: Tributavel):
        self.tributavel = tributavel

    def calcula(self) -> ResultadoCalculoFcpStRetido:
        facts = {
            "dummy": 1,
            "valor_ultima_base_calculo_icms_st_retido": self.tributavel.valor_ultima_base_calculo_icms_st_retido,
            "quantidade_produto": self.tributavel.quantidade_produto,
            "percentual_fcp_st_retido": self.tributavel.percentual_fcp_st_retido
        }
        
        results = decide_single_table(FCP_ST_RETIDO_CALC_RULE, facts, strict_mode=True)
        
        if not results:
             raise ValueError("No matching FCP ST Retido rule found.")
             
        return ResultadoCalculoFcpStRetido(
            base_calculo=Decimal(str(results[0]["base_calculo"])),
            valor_fcp_st_retido=Decimal(str(results[0]["valor_fcp_st_retido"]))
        )
