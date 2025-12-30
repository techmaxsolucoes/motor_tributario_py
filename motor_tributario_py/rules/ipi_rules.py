from decimal import Decimal

# Full IPI Logic Rule
# Inputs:
# - valor_produto, quantidade_produto, frete, seguro, outras_despesas
# - tipo_desconto, desconto
# - percentual_ipi
IPI_CALC_RULE = {
    "title": "Full IPI Calculation Rules",
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
            {"id": "base_calculo"},
            {"id": "valor_final"}
        ],
        "rows": [
            # Condicional: Add Discount
            # Base = ((Val*Qty + Frete + Seg + Outras) + Desc)
            [
                '( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + desconto )',
                '( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + desconto ) * percentual_ipi) / decimal(100)'
            ],
            
            # Incondicional: Subtract Discount
            # Base = ((Val*Qty + Frete + Seg + Outras) - Desc)
            [
                '( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) - desconto )',
                '( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) - desconto ) * percentual_ipi) / decimal(100)'
            ]
        ]
    }
}
