from decimal import Decimal

# Full ICMS Logic Rule
# Inputs: 
# - valor_produto, quantidade_produto, frete, seguro, outras_despesas
# - valor_ipi, is_ativo_imobilizado_ou_uso_consumo (bool string "true"/"false")
# - tipo_desconto, desconto
# - percentual_reducao, percentual_icms
ICMS_CALC_RULE = {
    "title": "Full ICMS Calculation Rules",
    "hit_policy": "Unique",
    "inputs": {
        "cols": [
            {"id": "is_ativo"},      # "true" / "false"
            {"id": "tipo_desconto"}  # "Condicional" / "Incondicional"
        ],
        "rows": [
            ['true', '"Condicional"'],
            ['true', '"Incondicional"'],
            ['false', '"Condicional"'],
            ['false', '"Incondicional"']
        ]
    },
    "outputs": {
        "cols": [
            {"id": "base_calculo"},
            {"id": "valor_final"}
        ],
        "rows": [
            # 1. Ativo=True (Add IPI), Condicional (Add Discount)
            [
                '( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) + desconto ) * (decimal(1) - (percentual_reducao / decimal(100)))',
                '( ( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) + desconto ) * (decimal(1) - (percentual_reducao / decimal(100))) ) * percentual_icms) / decimal(100)'
            ],
            
            # 2. Ativo=True (Add IPI), Incondicional (Sub Discount)
            [
                '( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) - desconto ) * (decimal(1) - (percentual_reducao / decimal(100)))',
                '( ( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) - desconto ) * (decimal(1) - (percentual_reducao / decimal(100))) ) * percentual_icms) / decimal(100)'
            ],
            
            # 3. Ativo=False (No IPI), Condicional (Add Discount)
            [
                '( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + desconto ) * (decimal(1) - (percentual_reducao / decimal(100)))',
                '( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + desconto ) * (decimal(1) - (percentual_reducao / decimal(100))) ) * percentual_icms) / decimal(100)'
            ],
            
            # 4. Ativo=False (No IPI), Incondicional (Sub Discount)
            [
                '( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) - desconto ) * (decimal(1) - (percentual_reducao / decimal(100)))',
                '( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) - desconto ) * (decimal(1) - (percentual_reducao / decimal(100))) ) * percentual_icms) / decimal(100)'
            ]
        ]
    }
}
