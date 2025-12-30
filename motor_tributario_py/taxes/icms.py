from decimal import Decimal
from dataclasses import dataclass
from typing import Dict, Any, Optional
from motor_tributario_py.models import Tributavel
from motor_tributario_py.rules.icms_rules import ICMS_CALC_RULE
from bkflow_dmn.api import decide_single_table

@dataclass
class ResultadoCalculoIcms:
    base_calculo: Decimal
    valor: Decimal
    # CST-specific fields (pass-through from input)
    percentual_icms: Optional[Decimal] = None
    percentual_reducao: Optional[Decimal] = None
    percentual_icms_st: Optional[Decimal] = None
    percentual_mva: Optional[Decimal] = None
    base_calculo_st: Optional[Decimal] = None
    valor_icms_st: Optional[Decimal] = None
    percentual_reducao_st: Optional[Decimal] = None
    # CST 51 - Diferimento
    percentual_diferimento: Optional[Decimal] = None
    valor_icms_diferido: Optional[Decimal] = None
    valor_icms_operacao: Optional[Decimal] = None
    # CST 60 - ST Retido
    valor_bc_st_retido: Optional[Decimal] = None
    # CST 60 - Efetivo
    base_calculo_icms_efetivo: Optional[Decimal] = None
    valor_icms_efetivo: Optional[Decimal] = None
    # CST 70/90 - Modalidade
    modalidade_determinacao_bc_icms: Optional[str] = None
    modalidade_determinacao_bc_icms_st: Optional[str] = None

class CalculadoraIcms:
    def __init__(self, tributavel: Tributavel):
        self.tributavel = tributavel

    def calcula(self, ignore_ipi: bool = False) -> ResultadoCalculoIcms:
        # Prepare Fact Context from Tributavel
        # ignore_ipi: Forced exclusion of IPI (used for ST Proprio deduction)
        
        is_ativo = self.tributavel.is_ativo_imobilizado_ou_uso_consumo
        if ignore_ipi:
             is_ativo = False
             
        facts = {
            "valor_produto": self.tributavel.valor_produto,
            "quantidade_produto": self.tributavel.quantidade_produto,
            "frete": self.tributavel.frete,
            "seguro": self.tributavel.seguro,
            "outras_despesas": self.tributavel.outras_despesas,
            "valor_ipi": self.tributavel.valor_ipi,
            "is_ativo": is_ativo, # Python bool
            "tipo_desconto": self.tributavel.tipo_desconto,
            "desconto": self.tributavel.desconto,
            "percentual_reducao": self.tributavel.percentual_reducao,
            "percentual_icms": self.tributavel.percentual_icms
        }
        
        results = decide_single_table(ICMS_CALC_RULE, facts, strict_mode=True)
        
        if not results:
             # Fallback or error?
             raise ValueError("No matching ICMS rule found for inputs.")

        base_calculo = Decimal(str(results[0]["base_calculo"]))
        valor = Decimal(str(results[0]["valor_final"]))
        
        
        # CST-specific post-processing using DMN rules
        valor_icms_operacao = None
        valor_icms_diferido = None
        base_calculo_icms_efetivo = None
        valor_icms_efetivo = None
        
        if self.tributavel.cst:
            from motor_tributario_py.rules.cst_post_processing_rules import CST_POST_PROCESSING_RULE
            
            facts = {"cst": str(self.tributavel.cst)}
            post_decision = decide_single_table(CST_POST_PROCESSING_RULE, facts, strict_mode=False)
            
            if post_decision:
                calcular_diferimento = post_decision[0].get("calcular_diferimento")
                calcular_efetivo = post_decision[0].get("calcular_efetivo")
                
                # CST 51 - Diferimento (Deferral)
                if (calcular_diferimento == 'true' or calcular_diferimento is True) and self.tributavel.percentual_diferimento > 0:
                    from decimal import ROUND_UP
                    # Calculate full operation value
                    valor_icms_operacao = (base_calculo * self.tributavel.percentual_icms / Decimal('100')).quantize(Decimal('0.01'))
                    # Calculate deferred amount - use ROUND_UP to match C# MidpointRounding.AwayFromZero
                    valor_icms_diferido = (valor_icms_operacao * self.tributavel.percentual_diferimento / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_UP)
                    # Final ICMS = Operation - Deferred
                    valor = valor_icms_operacao - valor_icms_diferido
                
                # CST 60 - Efetivo
                if (calcular_efetivo == 'true' or calcular_efetivo is True) and self.tributavel.percentual_icms_efetivo > 0:
                    from motor_tributario_py.taxes.icms_efetivo import CalculadoraIcmsEfetivo
                    calc_efetivo = CalculadoraIcmsEfetivo(self.tributavel)
                    res_efetivo = calc_efetivo.calcula()
                    base_calculo_icms_efetivo = res_efetivo.base_calculo
                    valor_icms_efetivo = res_efetivo.valor_icms_efetivo
        
        return ResultadoCalculoIcms(
            base_calculo=base_calculo,
            valor=valor,
            percentual_icms=self.tributavel.percentual_icms,
            percentual_reducao=self.tributavel.percentual_reducao,
            percentual_icms_st=self.tributavel.percentual_icms_st,
            percentual_mva=self.tributavel.percentual_mva,
            base_calculo_st=None,  # Will be populated by facade if needed
            valor_icms_st=None,  # Will be populated by facade if needed
            percentual_reducao_st=self.tributavel.percentual_reducao_st,
            percentual_diferimento=self.tributavel.percentual_diferimento,
            valor_bc_st_retido=self.tributavel.valor_produto,  # CST 60: base = valor_produto
            valor_icms_operacao=valor_icms_operacao,
            valor_icms_diferido=valor_icms_diferido,
            base_calculo_icms_efetivo=base_calculo_icms_efetivo,
            valor_icms_efetivo=valor_icms_efetivo,
            # Modalidade - default to "ValorOperacao" for ICMS, "MargemValorAgregado" for ST
            modalidade_determinacao_bc_icms="ValorOperacao",
            modalidade_determinacao_bc_icms_st="MargemValorAgregado" if self.tributavel.percentual_mva > 0 else None
        )
