from decimal import Decimal

# Full DIFAL/FCP Logic Rule
# Inputs:
# - Standard Base: valor_produto, quantidade_produto, frete, seguro, outras_despesas
# - IPI: valor_ipi
# - Config: is_ativo_imobilizado_ou_uso_consumo
# - Discount: tipo_desconto, desconto
# - Rates: percentual_fcp, percentual_difal_interna, percentual_difal_interestadual
DIFAL_CALC_RULE = {
    "title": "Full DIFAL and FCP Calculation Rules",
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
            {"id": "valor_fcp"},
            {"id": "valor_difal"},
            {"id": "valor_icms_destino"},
            {"id": "valor_icms_origem"}
        ],
        "rows": [
            # 1. Ativo=T, Cond: Base = (Raw + IPI) + Desc
            [
                '( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) + desconto )',
                '( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) + desconto ) * percentual_fcp ) / decimal(100)',
                '( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) + desconto ) * (percentual_difal_interna - percentual_difal_interestadual) ) / decimal(100)',
                '( ( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) + desconto ) * (percentual_difal_interna - percentual_difal_interestadual) ) / decimal(100) )', # 100% to Destino
                'decimal(0)' # 0% to Origem
            ],
            
            # 2. Ativo=T, Incond: Base = (Raw + IPI) - Desc
            [
                '( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) - desconto )',
                '( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) - desconto ) * percentual_fcp ) / decimal(100)',
                '( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) - desconto ) * (percentual_difal_interna - percentual_difal_interestadual) ) / decimal(100)',
                '( ( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + valor_ipi) - desconto ) * (percentual_difal_interna - percentual_difal_interestadual) ) / decimal(100) )', 
                'decimal(0)'
            ],
            
            # 3. Ativo=F, Cond: Base = (Raw) + Desc (NO IPI)
            [
                '( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + desconto )',
                '( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + desconto ) * percentual_fcp ) / decimal(100)',
                '( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + desconto ) * (percentual_difal_interna - percentual_difal_interestadual) ) / decimal(100)',
                '( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + desconto ) * (percentual_difal_interna - percentual_difal_interestadual) ) / decimal(100) )', 
                'decimal(0)'
            ],
            
            # 4. Ativo=F, Incond: Base = (Raw) - Desc (NO IPI)
            [
                '( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) - desconto )',
                '( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) - desconto ) * percentual_fcp ) / decimal(100)',
                '( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) - desconto ) * (percentual_difal_interna - percentual_difal_interestadual) ) / decimal(100)',
                '( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) - desconto ) * (percentual_difal_interna - percentual_difal_interestadual) ) / decimal(100) )', 
                'decimal(0)'
            ]
        ]
    }
}
