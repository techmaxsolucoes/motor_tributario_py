from decimal import Decimal
from dataclasses import dataclass
from typing import Optional
from motor_tributario_py.models import Tributavel
from motor_tributario_py.audit import AuditManager, ExecutionReport
from motor_tributario_py.taxes.icms import CalculadoraIcms, ResultadoCalculoIcms
from motor_tributario_py.taxes.icms_st import CalculadoraIcmsSt, ResultadoCalculoIcmsSt
from motor_tributario_py.taxes.icms import CalculadoraIcms, ResultadoCalculoIcms
from motor_tributario_py.taxes.icms_st import CalculadoraIcmsSt, ResultadoCalculoIcmsSt
from motor_tributario_py.taxes.difal import CalculadoraDifal, ResultadoCalculoDifal
from motor_tributario_py.taxes.issqn import CalculadoraIssqn, ResultadoCalculoIssqn
from motor_tributario_py.taxes.ipi import CalculadoraIpi, ResultadoCalculoIpi
from motor_tributario_py.taxes.pis import CalculadoraPis, ResultadoCalculoPis
from motor_tributario_py.taxes.cofins import CalculadoraCofins, ResultadoCalculoCofins
from motor_tributario_py.taxes.ibpt import CalculadoraIbpt, ResultadoCalculoIbpt
from motor_tributario_py.taxes.fcp_st import CalculadoraFcpSt, ResultadoCalculoFcpSt, CalculadoraFcpStRetido, ResultadoCalculoFcpStRetido
from motor_tributario_py.taxes.icms_desonerado import CalculadoraIcmsDesonerado, ResultadoCalculoIcmsDesonerado
from motor_tributario_py.taxes.ibs_cbs import CalculadoraBaseIbsCbs, CalculadoraIbs, CalculadoraIbsMunicipal, CalculadoraCbs, ResultadoCalculoIbs, ResultadoCalculoCbs
from motor_tributario_py.taxes.icms_efetivo import CalculadoraIcmsEfetivo, ResultadoCalculoIcmsEfetivo
from motor_tributario_py.taxes.icms_monofasico import CalculadoraIcmsMonofasico, ResultadoCalculoIcmsMonofasico
from motor_tributario_py.taxes.fcp import CalculadoraFcp, ResultadoCalculoFcp
from motor_tributario_py.taxes.credito_icms import CalculadoraCreditoIcms, ResultadoCalculoCreditoIcms
from motor_tributario_py.taxes.csosn import CalculadoraCsosn, ResultadoCalculoCsosn
from motor_tributario_py.utils.functions import register_feel_functions

class FacadeCalculadoraTributacao:
    # ... existing init ...
    def __init__(self, tributavel: Tributavel, **kwargs):
        register_feel_functions()
        self.tributavel = tributavel
        # Handle overrides from kwargs (used in tests)
        for key, value in kwargs.items():
            if hasattr(self.tributavel, key):
                setattr(self.tributavel, key, value)
    
    # ... existing methods ...

    # Helper to avoid code duplication for base
    def _calcula_base_ibs_cbs(self) -> Decimal:
        pis_val = self.calcula_pis().valor.quantize(Decimal('0.01'))
        cofins_val = self.calcula_cofins().valor.quantize(Decimal('0.01'))
        icms_val = self.calcula_icms().valor.quantize(Decimal('0.01'))
        issqn_val = self.calcula_issqn().valor.quantize(Decimal('0.01'))
        
        return CalculadoraBaseIbsCbs(self.tributavel).calcula_base(
            valor_pis=pis_val,
            valor_cofins=cofins_val,
            valor_icms=icms_val,
            valor_issqn=issqn_val
        )

    def calcula_credito_icms(self) -> ResultadoCalculoCreditoIcms:
        # Assuming _get_calculator is a placeholder for direct instantiation based on existing methods
        # and the user's instruction is to replace the previous complex logic with a simpler call.
        return CalculadoraCreditoIcms(self.tributavel).calcula()

    def calcula_csosn(self) -> ResultadoCalculoCsosn:
        # Assuming _get_calculator is a placeholder for direct instantiation based on existing methods
        # and the user's instruction had a typo.
        return CalculadoraCsosn(self.tributavel).calcula()

    def calcula_ibs(self) -> ResultadoCalculoIbs:
        base = self._calcula_base_ibs_cbs()
        return CalculadoraIbs(self.tributavel).calcula(base)

    def calcula_ibs_municipal(self) -> ResultadoCalculoIbs:
        base = self._calcula_base_ibs_cbs()
        return CalculadoraIbsMunicipal(self.tributavel).calcula(base)

    def calcula_cbs(self) -> ResultadoCalculoCbs:
        base = self._calcula_base_ibs_cbs()
        return CalculadoraCbs(self.tributavel).calcula(base)

    def calcula_ibpt(self) -> ResultadoCalculoIbpt:
        return CalculadoraIbpt(self.tributavel).calcula()

    def calcula_fcp_st(self) -> ResultadoCalculoFcpSt:
        # FCP ST depends on IPI for Base Calculation (same as ICMS ST)
        ipi_result = self.calcula_ipi()
        return CalculadoraFcpSt(self.tributavel).calcula(valor_ipi=ipi_result.valor)

    def calcula_fcp_st_retido(self) -> ResultadoCalculoFcpStRetido:
        return CalculadoraFcpStRetido(self.tributavel).calcula()

    def calcula_icms_desonerado(self) -> ResultadoCalculoIcmsDesonerado:
        # Depends on base calculation from ICMS logic for BaseSimples scenarios
        icms_result = self.calcula_icms()
        return CalculadoraIcmsDesonerado(self.tributavel).calcula(base_calculo_icms=icms_result.base_calculo)

    def calcula_icms_efetivo(self) -> ResultadoCalculoIcmsEfetivo:
        return CalculadoraIcmsEfetivo(self.tributavel).calcula()

    def calcula_icms_monofasico(self) -> ResultadoCalculoIcmsMonofasico:
        return CalculadoraIcmsMonofasico(self.tributavel).calcula()

    def calcula_fcp(self) -> ResultadoCalculoFcp:
        # FCP uses ICMS Base
        icms_res = self.calcula_icms()
        return CalculadoraFcp(self.tributavel).calcula(base_calculo_icms=icms_res.base_calculo)

    def calcula_credito_icms(self, icms_base_calculo: Optional[Decimal] = None) -> ResultadoCalculoCreditoIcms:
        # Logic from C#: Switch on Documento
        # CTe -> ValorIcmsSt is the base
        # Others -> BaseCalculoIcms is the base (passed as parameter to avoid recursion)
        base_to_use = Decimal('0')
        
        if self.tributavel.documento == "CTe":
             # Depends on ICMS ST
             # Note: ICMS ST might depend on IPI/ICMS Proprio
             st_res = self.calcula_icms_st()
             base_to_use = st_res.valor_icms_st
        else:
             # Use the base provided (from calcula_icms orchestration) to avoid recursion
             if icms_base_calculo is not None:
                 base_to_use = icms_base_calculo
             else:
                 # Fallback: calculate ICMS if not provided (legacy behavior)
                 icms_res = CalculadoraIcms(self.tributavel).calcula()
                 base_to_use = icms_res.base_calculo
             
        return CalculadoraCreditoIcms(self.tributavel).calcula(base_calculo=base_to_use)

    def calcula_icms(self) -> ResultadoCalculoIcms:
        from motor_tributario_py.rules.cst_rules import CST_DISPATCH_RULE
        from bkflow_dmn.api import decide_single_table
        
        result = CalculadoraIcms(self.tributavel).calcula()
        
        # Use DMN rules to determine additional calculations needed
        if self.tributavel.cst:
            facts = {"cst": str(self.tributavel.cst)}
            decision = decide_single_table(CST_DISPATCH_RULE, facts, strict_mode=False)
            
            if decision:
                d = decision[0]
                
                # Check if ST calculation is needed
                calcular_st = d.get("calcular_icms_st")
                needs_st = calcular_st == 'true' or calcular_st is True
                
                if needs_st and self.tributavel.percentual_icms_st and self.tributavel.percentual_mva:
                    # Calculate ICMS ST and merge into result
                    st_result = self.calcula_icms_st()
                    result.base_calculo_st = st_result.base_calculo_icms_st
                    result.valor_icms_st = st_result.valor_icms_st
                
                # Check if Credito calculation is needed (CST 90)
                calcular_credito = d.get("calcular_credito")
                needs_credito = calcular_credito == 'true' or calcular_credito is True
                
                if needs_credito and self.tributavel.percentual_credito:
                    # Calculate credito passing the ICMS base to avoid recursion
                    credito_result = self.calcula_credito_icms(icms_base_calculo=result.base_calculo)
                    result.percentual_credito = self.tributavel.percentual_credito
                    result.valor_credito = credito_result.valor
        
        return result

    def calcula_ipi(self) -> ResultadoCalculoIpi:
        return CalculadoraIpi(self.tributavel).calcula()
    
    def calcula_pis(self) -> ResultadoCalculoPis:
        # PIS depends on ICMS value for deduction if configured
        # Internal calculator handles dependency if needed
        return CalculadoraPis(self.tributavel).calcula()

    def calcula_cofins(self) -> ResultadoCalculoCofins:
        # COFINS depends on ICMS value for deduction if configured
        # Internal calculator handles dependency if needed
        return CalculadoraCofins(self.tributavel).calcula()

    def calcula_icms_st(self) -> ResultadoCalculoIcmsSt:
        # Internal calculator handles dependencies
        return CalculadoraIcmsSt(self.tributavel).calcula()

    def calcula_difal(self) -> ResultadoCalculoDifal:
        # DIFAL depends on IPI and ICMS Proprio logic for base components
        # (Though current implementations re-calculate base internally or assume independent base flows)
        # For DIFAL, we use the specific calculator.
        return CalculadoraDifal(self.tributavel).calcula()

    def calcula_issqn(self, calcular_retencoes: bool = False) -> ResultadoCalculoIssqn:
        return CalculadoraIssqn(self.tributavel).calcula(calcular_retencoes)
    
    def debug_execution(self, method_name: str, *args, **kwargs) -> ExecutionReport:
        """
        Execute any facade method with comprehensive audit tracing.
        
        Args:
            method_name: Name of the method to debug (e.g., 'calcula_icms')
            *args, **kwargs: Arguments to pass to the method
            
        Returns:
            ExecutionReport containing result and full audit trail
            
        Example:
            >>> facade = FacadeCalculadoraTributacao(produto)
            >>> report = facade.debug_execution('calcula_icms')
            >>> print(report.format_pretty())
        """
        return AuditManager.debug_method(self, method_name, *args, **kwargs)

    # Aliases to match C# Facade structure for DDT
    def calcula_difal_fcp(self) -> ResultadoCalculoDifal:
        # C# "CalculaDifalFcp" -> seems to map to generic Difal calc in our Python implementation
        return self.calcula_difal()

    def calcula_icms_credito(self) -> ResultadoCalculoCreditoIcms:
        # C# "CalculaIcmsCredito" 
        return self.calcula_credito_icms()

    def calcula_ibpt(self, *args, **kwargs) -> ResultadoCalculoIbpt:
        return CalculadoraIbpt(self.tributavel).calcula()

    def calcula_tributacao(self) -> 'ResultadoTributacao':
        # Composite calculation to match C# ResultadoTributacao
        res_icms = self.calcula_icms()
        res_ipi = self.calcula_ipi()
        res_pis = self.calcula_pis()
        res_cofins = self.calcula_cofins()
        res_issqn = self.calcula_issqn(calcular_retencoes=True)
        res_fcp = self.calcula_fcp()
        res_difal = self.calcula_difal()
        res_icms_st = self.calcula_icms_st()
        res_ibpt = self.calcula_ibpt()
        res_icms_deson = self.calcula_icms_desonerado()
        res_icms_mono = self.calcula_icms_monofasico()
        
        # Determine strict returns for C# assertions (which expect Flat properties)
        # We map them dynamically in ResultadoTributacao class
        return ResultadoTributacao(
            res_icms=res_icms,
            res_ipi=res_ipi,
            res_pis=res_pis,
            res_cofins=res_cofins,
            res_issqn=res_issqn,
            res_fcp=res_fcp,
            res_difal=res_difal,
            res_icms_st=res_icms_st,
            res_ibpt=res_ibpt,
            res_icms_desonerado=res_icms_deson,
            res_icms_monofasico=res_icms_mono
        )

@dataclass
class ResultadoTributacao:
    
    # Use res_ prefix to avoid name collision with properties (especially fcp)
    res_icms: ResultadoCalculoIcms
    res_ipi: ResultadoCalculoIpi
    res_pis: ResultadoCalculoPis
    res_cofins: ResultadoCalculoCofins
    res_issqn: ResultadoCalculoIssqn
    res_fcp: ResultadoCalculoFcp
    res_difal: ResultadoCalculoDifal
    res_icms_st: ResultadoCalculoIcmsSt
    res_ibpt: ResultadoCalculoIbpt
    res_icms_desonerado: ResultadoCalculoIcmsDesonerado
    res_icms_monofasico: ResultadoCalculoIcmsMonofasico
    
    @property
    def valor_bc_icms(self): return self.res_icms.base_calculo
    @property
    def valor_icms(self): return self.res_icms.valor
    
    # Crédito ICMS (from ICMS orchestration for CST 90)
    @property
    def valor_credito(self): return self.res_icms.valor_credito or Decimal('0')
    @property
    def percentual_credito(self): return self.res_icms.percentual_credito or Decimal('0')
    
    @property
    def valor_ipi(self): return self.res_ipi.valor
    
    @property
    def valor_cofins(self): return self.res_cofins.valor
    @property
    def valor_pis(self): return self.res_pis.valor
    
    @property
    def valor_iss(self): return self.res_issqn.valor
    @property
    def valor_ret_irrf(self): return self.res_issqn.valor_ret_irrf
    @property
    def valor_ret_cofins(self): return self.res_issqn.valor_ret_cofins
    @property
    def valor_ret_pis(self): return self.res_issqn.valor_ret_pis
    @property
    def valor_ret_inss(self): return self.res_issqn.valor_ret_inss
    @property
    def valor_ret_clss(self): return self.res_issqn.valor_ret_csll 
    
    # DIFAL
    @property
    def fcp(self): return self.res_difal.fcp
    @property
    def valor_difal(self): return self.res_difal.difal
    @property
    def valor_icms_origem(self): return self.res_difal.valor_icms_origem
    @property
    def valor_icms_destino(self): return self.res_difal.valor_icms_destino
    
    # IBPT
    @property
    def valor_tributacao_federal(self): return self.res_ibpt.tributacao_federal
    @property
    def valor_tributacao_federal_importados(self): return self.res_ibpt.tributacao_federal_importados
    @property
    def valor_tributacao_estadual(self): return self.res_ibpt.tributacao_estadual
    @property
    def valor_tributacao_municipal(self): return self.res_ibpt.tributacao_municipal
    
    # ST
    @property
    def valor_icms_st(self): return self.res_icms_st.valor_icms_st
    @property
    def base_calculo_icms_st(self): return self.res_icms_st.base_calculo_icms_st
    @property
    def valor_icms_proprio(self): return self.res_icms_st.valor_icms_proprio
    @property
    def base_calculo_operacao_propria(self): return self.res_icms_st.base_calculo_operacao_propria
    
    # Desonerado
    @property
    def valor_icms_desonerado(self): return self.res_icms_desonerado.valor_icms_desonerado

    # Monofasico
    @property
    def valor_icms_monofasico_proprio(self): return self.res_icms_monofasico.valor_icms_monofasico
    @property
    def valor_icms_monofasico_retencao(self): return self.res_icms_monofasico.valor_icms_monofasico_retencao
    @property
    def valor_icms_monofasico_operacao(self): return self.res_icms_monofasico.valor_icms_monofasico_operacao
    @property
    def valor_icms_monofasico_diferido(self): return self.res_icms_monofasico.valor_icms_monofasico_diferido
    @property
    def valor_icms_monofasico_retido_anteriormente(self): return self.res_icms_monofasico.valor_icms_monofasico_retido_anteriormente
