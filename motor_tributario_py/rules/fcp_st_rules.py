from decimal import Decimal

# FCP ST Rule
# Logic: Calculate Base ST (same as ICMS ST), then apply FCP ST Rate.
# Inputs: valor_produto, quantidade_produto, frete, seguro, outras_despesas, valor_ipi, desconto, percentual_mva, percentual_fcp_st
FCP_ST_CALC_RULE = {
    "title": "FCP ST Calculation Rules",
    "hit_policy": "Unique",
    "inputs": {
        "cols": [
            {"id": "tipo_desconto"}
        ],
        "rows": [
            ['"Condicional"'],
            ['"Incondicional"']
        ]
    },
    "outputs": {
        "cols": [
            {"id": "base_calculo_fcp_st"},
            {"id": "valor_fcp_st"}
        ],
        "rows": [
            # 1. Condicional (+ Desc to Base)
            # Base = ((Val * Qty + Frete + Seg + Outras + IPI) + Desc) * (1 + MVA/100)
            [
                '( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) + desconto ) * ( decimal(1) + ( percentual_mva / decimal(100) ) ) )',
                '( ( ( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) + desconto ) * ( decimal(1) + ( percentual_mva / decimal(100) ) ) ) ) * percentual_fcp_st ) / decimal(100)'
            ],
            
            # 2. Incondicional (- Desc from Base)
            # Base = ((Val * Qty + Frete + Seg + Outras + IPI) - Desc) * (1 + MVA/100)
            [
                 '( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) - desconto ) * ( decimal(1) + ( percentual_mva / decimal(100) ) ) )',
                 '( ( ( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) - desconto ) * ( decimal(1) + ( percentual_mva / decimal(100) ) ) ) ) * percentual_fcp_st ) / decimal(100)'
            ]
        ]
    }
}

# FCP ST Retido Rule
# Logic: Base = ValorUltimaBaseCalculoIcmsStRetido * Qty. Valor = Base * Rate.
FCP_ST_RETIDO_CALC_RULE = {
    "title": "FCP ST Retido Calculation Rules",
    "hit_policy": "Unique",
    "inputs": {
        "cols": [{"id": "dummy"}],
        "rows": [['1']]
    },
    "outputs": {
        "cols": [
            {"id": "base_calculo"},
            {"id": "valor_fcp_st_retido"}
        ],
        "rows": [
            [
                '( valor_ultima_base_calculo_icms_st_retido * quantidade_produto )',
                '( ( valor_ultima_base_calculo_icms_st_retido * quantidade_produto ) * percentual_fcp_st_retido ) / decimal(100)'
            ]
        ]
    }
}
