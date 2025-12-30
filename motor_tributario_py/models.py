from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass
class Tributavel:
    # Basic Values
    valor_produto: Decimal = Decimal('0')
    frete: Decimal = Decimal('0')
    seguro: Decimal = Decimal('0')
    outras_despesas: Decimal = Decimal('0')
    desconto: Decimal = Decimal('0')
    valor_ipi: Decimal = Decimal('0')
    quantidade_produto: Decimal = Decimal('1')
    
    # Flags / Booleans
    is_servico: bool = False
    is_ativo_imobilizado_ou_uso_consumo: bool = False
    is_ativo_imobilizado_ou_uso_consumo: bool = False
    tipo_desconto: str = "Incondicional"  # "Condicional" or "Incondicional"
    cst: str = "" # e.g. "20", "70", "30", "40"
    tipo_calculo_icms_desonerado: str = "" # "BaseSimples" or "BasePorDentro"
    
    # Integration / Facade Config
    crt: str = "" # e.g. "RegimeNormal", "SimplesNacional"
    tipo_operacao: str = "" # "OperacaoInterna", "OperacaoInterestadual"
    tipo_pessoa: str = "" # "Fisica", "Juridica"

    # Rates / Percentages
    percentual_icms: Decimal = Decimal('0')
    percentual_reducao: Decimal = Decimal('0')
    percentual_ipi: Decimal = Decimal('0')
    percentual_pis: Decimal = Decimal('0')
    percentual_reducao_pis: Decimal = Decimal('0')
    percentual_cofins: Decimal = Decimal('0')
    percentual_reducao_cofins: Decimal = Decimal('0')

    # ICMS ST
    percentual_icms_st: Decimal = Decimal('0.00')
    percentual_mva: Decimal = Decimal('0.00')
    percentual_reducao_st: Decimal = Decimal('0.00')

    # FCP / Credito
    percentual_fcp: Decimal = Decimal('0.00')
    percentual_fcp_st: Decimal = Decimal('0.00')
    percentual_credito: Decimal = Decimal('0.00')

    # CSOSN
    csosn: int = 0  # 101, 102, 201, 500, 900 etc.
    percentual_fcp_st_retido: Decimal = Decimal('0.00')
    valor_ultima_base_calculo_icms_st_retido: Decimal = Decimal('0.00')
    percentual_difal_interna: Decimal = Decimal('0.00')
    percentual_difal_interestadual: Decimal = Decimal('0.00')

    # ISSQN
    percentual_issqn: Decimal = Decimal('0.00')
    percentual_ret_pis: Decimal = Decimal('0.00')
    percentual_ret_cofins: Decimal = Decimal('0.00')
    percentual_ret_csll: Decimal = Decimal('0.00')
    percentual_ret_irrf: Decimal = Decimal('0')
    percentual_ret_inss: Decimal = Decimal('0')

    # IBPT (Transparency)
    percentual_federal: Decimal = Decimal('0')
    percentual_estadual: Decimal = Decimal('0')
    percentual_municipal: Decimal = Decimal('0')
    percentual_federal_importados: Decimal = Decimal('0.00')

    # IBS / CBS (Reforma Tributária)
    percentual_ibs_uf: Decimal = Decimal('0.00')
    percentual_ibs_municipal: Decimal = Decimal('0.00')
    percentual_cbs: Decimal = Decimal('0.00')
    percentual_reducao_ibs_uf: Decimal = Decimal('0.00')
    percentual_reducao_ibs_municipal: Decimal = Decimal('0.00')
    percentual_reducao_cbs: Decimal = Decimal('0.00')

    # FCP (Proprio)
    percentual_fcp: Decimal = Decimal('0.00')
    
    # Credito ICMS
    percentual_credito: Decimal = Decimal('0.00')
    documento: str = "" # e.g. "NFe", "CTe", "MFe" 
    
    # ICMS Efetivo
    percentual_icms_efetivo: Decimal = Decimal('0.00')
    percentual_reducao_icms_efetivo: Decimal = Decimal('0.00')
    
    # ICMS Monofásico
    quantidade_base_calculo_icms_monofasico: Decimal = Decimal('0.00')
    aliquota_ad_rem_icms: Decimal = Decimal('0.00')
    percentual_reducao_aliquota_ad_rem_icms: Decimal = Decimal('0.00')
    percentual_biodiesel: Decimal = Decimal('0.00')
    percentual_originario_uf: Decimal = Decimal('0.00')
    # CST 61
    quantidade_base_calculo_icms_monofasico_retido_anteriormente: Decimal = Decimal('0.00')
    aliquota_ad_rem_icms_retido_anteriormente: Decimal = Decimal('0.00')
    
    
    # Flags to include taxes in IBS/CBS Base
    somar_pis_na_base_ibs_cbs: bool = False
    somar_cofins_na_base_ibs_cbs: bool = False
    somar_icms_na_base_ibs_cbs: bool = False
    somar_issqn_na_base_ibs_cbs: bool = False
    
    # ICMS Diferido
    percentual_diferimento: Decimal = Decimal('0.00')

    # PIS/COFINS Flags
    deduz_icms_da_base_de_pis_cofins: bool = False

