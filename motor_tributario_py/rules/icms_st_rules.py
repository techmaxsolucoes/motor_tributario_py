from decimal import Decimal

# Full ICMS ST Logic Rule
# Inputs:
# - valor_produto, quantidade_produto, frete, seguro, outras_despesas
# - valor_ipi
# - tipo_desconto, desconto
# - percentual_reducao_st, percentual_mva
# - percentual_icms_st, valor_icms_proprio
ICMS_ST_CALC_RULE = {
    "title": "Full ICMS ST Calculation Rules",
    "hit_policy": "Unique",
    "inputs": {
        "cols": [
            {"id": "tipo_desconto"}  # "Condicional" / "Incondicional"
        ],
        "rows": [
            ['"Condicional"'],
            ['"Incondicional"']
        ]
    },
    "outputs": {
        "cols": [
            {"id": "base_calculo_st"},
            {"id": "valor_icms_st"}
        ],
        # Formula Base ST: ( ( (BaseInit + IPI) +/- Desconto ) * (1 - RedST/100) ) * (1 + MVA/100)
        # Formula Value ST: (BaseST * RateST/100) - ICMS_Proprio
        "rows": [
            # Condicional: Add Discount
            [
                '( ( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) + desconto ) * (decimal(1) - (percentual_reducao_st / decimal(100))) ) * (decimal(1) + (percentual_mva / decimal(100))) )',
                '( ( ( ( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) + desconto ) * (decimal(1) - (percentual_reducao_st / decimal(100))) ) * (decimal(1) + (percentual_mva / decimal(100))) ) * percentual_icms_st ) / decimal(100) ) - valor_icms_proprio'
            ],
            
            # Incondicional: Subtract Discount
            [
                '( ( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) - desconto ) * (decimal(1) - (percentual_reducao_st / decimal(100))) ) * (decimal(1) + (percentual_mva / decimal(100))) )',
                '( ( ( ( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) - desconto ) * (decimal(1) - (percentual_reducao_st / decimal(100))) ) * (decimal(1) + (percentual_mva / decimal(100))) ) * percentual_icms_st ) / decimal(100) ) - valor_icms_proprio'
            ]
        ]
    }
}
