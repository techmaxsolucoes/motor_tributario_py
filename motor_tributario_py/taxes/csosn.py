from decimal import Decimal
from dataclasses import dataclass, field
from typing import Optional
from motor_tributario_py.models import Tributavel
from motor_tributario_py.taxes.icms import CalculadoraIcms
from motor_tributario_py.taxes.icms_st import CalculadoraIcmsSt
from motor_tributario_py.taxes.credito_icms import CalculadoraCreditoIcms
from motor_tributario_py.taxes.icms_efetivo import CalculadoraIcmsEfetivo
from motor_tributario_py.taxes.ipi import CalculadoraIpi

from motor_tributario_py.rules.csosn_rules import CSOSN_DISPATCH_RULE
from bkflow_dmn.api import decide_single_table

@dataclass
class ResultadoCalculoCsosn:
    csosn: int
    # Standard ICMS (Proprio) - Used by 900
    base_calculo_icms: Optional[Decimal] = None
    valor_icms: Optional[Decimal] = None
    percentual_icms: Optional[Decimal] = None
    percentual_reducao_icms: Optional[Decimal] = None
    
    # ST
    base_calculo_icms_st: Optional[Decimal] = None
    valor_icms_st: Optional[Decimal] = None
    percentual_icms_st: Optional[Decimal] = None
    percentual_mva: Optional[Decimal] = None
    percentual_reducao_st: Optional[Decimal] = None
    
    # Credito
    valor_credito: Optional[Decimal] = None
    percentual_credito: Optional[Decimal] = None
    
    # Efetivo / Retido
    base_calculo_icms_efetivo: Optional[Decimal] = None
    valor_icms_efetivo: Optional[Decimal] = None
    percentual_icms_efetivo: Optional[Decimal] = None
    percentual_reducao_icms_efetivo: Optional[Decimal] = None
    
    # Flags/Status
    modo_calculo: str = ""

class CalculadoraCsosn:
    def __init__(self, tributavel: Tributavel):
        self.tributavel = tributavel
        
    def calcula(self) -> ResultadoCalculoCsosn:
        code = self.tributavel.csosn
        
        # Decide strategy using DMN
        facts = {"csosn": code}
        decision = decide_single_table(CSOSN_DISPATCH_RULE, facts, strict_mode=True)
        
        if not decision:
             # Default fallback or error
             result = ResultadoCalculoCsosn(csosn=code, modo_calculo="Unknown")
             return result

        d = decision[0]
        result = ResultadoCalculoCsosn(csosn=code, modo_calculo=str(d["modo_calculo"]))
        
        run_proprio = d["calcular_icms_proprio"] == 'true' or d["calcular_icms_proprio"] is True
        run_st = d["calcular_icms_st"] == 'true' or d["calcular_icms_st"] is True
        run_credito = d["calcular_credito"] == 'true' or d["calcular_credito"] is True
        run_efetivo = d["calcular_efetivo"] == 'true' or d["calcular_efetivo"] is True
        
        # Pre-requisite: IPI for ST (201, 202, 203, 900 etc usually need IPI)
        # If running ST, ensure IPI
        if run_st:
             self._ensure_valor_ipi()

        # Execute modules
        if run_proprio:
             self._calc_proprio(result)
             
        if run_st:
             self._calc_st_logic(result)
             
        if run_credito:
             self._calc_credito(result)
             
        if run_efetivo:
             self._calc_efetivo(result)
            
        return result

    def _ensure_valor_ipi(self):
         calc_ipi = CalculadoraIpi(self.tributavel)
         res_ipi = calc_ipi.calcula()
         # Round IPI to 2 decimal places to match C# behavior before using in ST Base
         self.tributavel.valor_ipi = res_ipi.valor.quantize(Decimal('0.01'))

    def _calc_proprio(self, res: ResultadoCalculoCsosn):
        res.percentual_reducao_icms = self.tributavel.percentual_reducao
        res.percentual_icms = self.tributavel.percentual_icms
        
        calc_icms = CalculadoraIcms(self.tributavel)
        icms_res = calc_icms.calcula()
        res.base_calculo_icms = icms_res.base_calculo
        res.valor_icms = icms_res.valor

    def _calc_credito(self, res: ResultadoCalculoCsosn):
        # Credito uses a base similar to ICMS
        # Logic matches C#: Remove reduction, calc base?, apply credit rate.
        # But wait, does Credito have its own base rule? Yes.
        # However, `CalculadoraCreditoIcms.calcula` requires `base_calculo` input.
        # So we must calculate the base first.
        # C# behavior: `CalculaIcmsCredito` uses `CalculaBaseCalculoIcms`?
        # Yes looking at `Csosn101.cs`, it calls `CalculaIcmsCredito`.
        # Which likely orchestrates base calculation.
        
        # We will assume Credito Base = ICMS Base (Proprio) but with Reduction=0 (handled below)
        
        original_reduction = self.tributavel.percentual_reducao
        self.tributavel.percentual_reducao = Decimal(0)
        
        # Calculate Base using standard ICMS calculator
        calc_icms_base = CalculadoraIcms(self.tributavel)
        res_icms_base = calc_icms_base.calcula()
        
        base_for_credito = res_icms_base.base_calculo
        
        # Now Calc Credit Value
        calc_cred = CalculadoraCreditoIcms(self.tributavel)
        res_cred = calc_cred.calcula(base_calculo=base_for_credito)
        
        res.valor_credito = res_cred.valor
        res.percentual_credito = self.tributavel.percentual_credito
        
        # Restore
        self.tributavel.percentual_reducao = original_reduction

    def _calc_st_logic(self, res: ResultadoCalculoCsosn):
        res.percentual_mva = self.tributavel.percentual_mva
        res.percentual_reducao_st = self.tributavel.percentual_reducao_st
        res.percentual_icms_st = self.tributavel.percentual_icms_st
        
        calc_st = CalculadoraIcmsSt(self.tributavel)
        st_res = calc_st.calcula()
        
        res.base_calculo_icms_st = st_res.base_calculo_icms_st
        res.valor_icms_st = st_res.valor_icms_st

    def _calc_efetivo(self, res: ResultadoCalculoCsosn):
        calc_efetivo = CalculadoraIcmsEfetivo(self.tributavel)
        ef_res = calc_efetivo.calcula()
        
        res.base_calculo_icms_efetivo = ef_res.base_calculo
        res.valor_icms_efetivo = ef_res.valor_icms_efetivo
        res.percentual_icms_efetivo = self.tributavel.percentual_icms_efetivo
        res.percentual_reducao_icms_efetivo = self.tributavel.percentual_reducao_icms_efetivo

