from decimal import Decimal

# Full PIS/COFINS Logic Rule
# Inputs:
# - valor_produto, quantidade_produto, frete, seguro, outras_despesas
# - valor_ipi, is_ativo (bool), valor_icms, deduz_icms (bool)
# - tipo_desconto, desconto
# - percentual_reducao, percentual_tax (generic for PIS/COFINS)
PIS_COFINS_CALC_RULE = {
    "title": "Full PIS/COFINS Calculation Rules",
    "hit_policy": "Unique",
    "inputs": {
        "cols": [
            {"id": "is_ativo"},      # "true" / "false"
            {"id": "deduz_icms"},    # "true" / "false"
            {"id": "tipo_desconto"}  # "Condicional" / "Incondicional"
        ],
        "rows": [
            ['true', 'true', '"Condicional"'],
            ['true', 'true', '"Incondicional"'],
            ['true', 'false', '"Condicional"'],
            ['true', 'false', '"Incondicional"'],
            ['false', 'true', '"Condicional"'],
            ['false', 'true', '"Incondicional"'],
            ['false', 'false', '"Condicional"'],
            ['false', 'false', '"Incondicional"']
        ]
    },
    "outputs": {
        "cols": [
            {"id": "base_calculo"},
            {"id": "valor_final"}
        ],
        "rows": [
            # 1. T T Cond: ( (Base+IPI-ICMS) * (1-Red) ) + Desc
            [
                '( ( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) - valor_icms) * (decimal(1) - (percentual_reducao / decimal(100))) ) + desconto )',
                '( ( ( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) - valor_icms) * (decimal(1) - (percentual_reducao / decimal(100))) ) + desconto ) * percentual_tax) / decimal(100)'
            ],
            # 2. T T Incond: ( (Base+IPI-ICMS) * (1-Red) ) - Desc
            [
                '( ( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) - valor_icms) * (decimal(1) - (percentual_reducao / decimal(100))) ) - desconto )',
                '( ( ( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) - valor_icms) * (decimal(1) - (percentual_reducao / decimal(100))) ) - desconto ) * percentual_tax) / decimal(100)'
            ],
            # 3. T F Cond: ( (Base+IPI) * (1-Red) ) + Desc
            [
                '( ( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) ) * (decimal(1) - (percentual_reducao / decimal(100))) ) + desconto )',
                '( ( ( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) ) * (decimal(1) - (percentual_reducao / decimal(100))) ) + desconto ) * percentual_tax) / decimal(100)'
            ],
            # 4. T F Incond: ( (Base+IPI) * (1-Red) ) - Desc
            [
                '( ( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) ) * (decimal(1) - (percentual_reducao / decimal(100))) ) - desconto )',
                '( ( ( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) ) * (decimal(1) - (percentual_reducao / decimal(100))) ) - desconto ) * percentual_tax) / decimal(100)'
            ],
            # 5. F T Cond: ( (Base-ICMS) * (1-Red) ) + Desc
            [
                '( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) - valor_icms) * (decimal(1) - (percentual_reducao / decimal(100))) ) + desconto )',
                '( ( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) - valor_icms) * (decimal(1) - (percentual_reducao / decimal(100))) ) + desconto ) * percentual_tax) / decimal(100)'
            ],
            # 6. F T Incond: ( (Base-ICMS) * (1-Red) ) - Desc
            [
                '( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) - valor_icms) * (decimal(1) - (percentual_reducao / decimal(100))) ) - desconto )',
                '( ( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) - valor_icms) * (decimal(1) - (percentual_reducao / decimal(100))) ) - desconto ) * percentual_tax) / decimal(100)'
            ],
            # 7. F F Cond: ( (Base) * (1-Red) ) + Desc
            [
                '( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) ) * (decimal(1) - (percentual_reducao / decimal(100))) ) + desconto )',
                '( ( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) ) * (decimal(1) - (percentual_reducao / decimal(100))) ) + desconto ) * percentual_tax) / decimal(100)'
            ],
            # 8. F F Incond: ( (Base) * (1-Red) ) - Desc
            [
                '( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) ) * (decimal(1) - (percentual_reducao / decimal(100))) ) - desconto )',
                '( ( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) ) * (decimal(1) - (percentual_reducao / decimal(100))) ) - desconto ) * percentual_tax) / decimal(100)'
            ]
        ]
    }
}
