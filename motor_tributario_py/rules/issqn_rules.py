from decimal import Decimal

# Rule 1: Calculate Base Calculation from Raw Inputs
# Inputs: valor_produto, quantidade_produto, frete, seguro, outras_despesas, desconto, tipo_desconto
ISSQN_BASE_RULE = {
    "title": "ISSQN Base Calculation",
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
        "cols": [{"id": "base_calculo"}],
        "rows": [
            # Condicional: Base + Desconto
            # ( ( ( ( (Val * Qty) + Frete) + Seg) + Outras) + Desc )
            ['( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) + desconto )'],
            # Incondicional: Base - Desconto
            ['( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) - desconto )']
        ]
    }
}

# Rule 2: Calculate Tax Values from Base Calculation
# Inputs: 
# - base_calculo
# - Rates: percentual_issqn, percentual_ret_pis, _cofins, _csll, _irrf, _inss
# - Config: calcular_retencoes (boolean string "true"/"false")
ISSQN_TAX_RULE = {
    "title": "ISSQN Tax Calculation",
    "hit_policy": "Unique",
    "inputs": {
        "cols": [
            {"id": "calcular_retencoes"}
        ],
        "rows": [
            ['true'],
            ['false']
        ]
    },
    "outputs": {
        "cols": [
            {"id": "valor_issqn"},
            {"id": "valor_ret_pis"},
            {"id": "valor_ret_cofins"},
            {"id": "valor_ret_csll"},
            {"id": "valor_ret_irrf"},
            {"id": "valor_ret_inss"}
        ],
        "rows": [
            # 1. Retentions = True
            [
                # ISSQN > 10
                'apply_threshold( ( ( base_calculo * percentual_issqn ) / decimal(100) ), 10 )',
                
                # Check Threshold Logic: IF (Base * TotalRate / 100) > 10 THEN Value ELSE 0
                # TotalRate = ( (Pis + Cofins) + Csll )
                
                # Ret PIS
                'check_threshold( ( ( base_calculo * ( (percentual_ret_pis + percentual_ret_cofins) + percentual_ret_csll ) ) / decimal(100) ), 10, ( ( base_calculo * percentual_ret_pis ) / decimal(100) ) )',
                # Ret COFINS
                'check_threshold( ( ( base_calculo * ( (percentual_ret_pis + percentual_ret_cofins) + percentual_ret_csll ) ) / decimal(100) ), 10, ( ( base_calculo * percentual_ret_cofins ) / decimal(100) ) )',
                # Ret CSLL
                'check_threshold( ( ( base_calculo * ( (percentual_ret_pis + percentual_ret_cofins) + percentual_ret_csll ) ) / decimal(100) ), 10, ( ( base_calculo * percentual_ret_csll ) / decimal(100) ) )',
                
                # Ret IRRF > 10
                'apply_threshold( ( ( base_calculo * percentual_ret_irrf ) / decimal(100) ), 10 )',
                
                # Ret INSS > 29
                'apply_threshold( ( ( base_calculo * percentual_ret_inss ) / decimal(100) ), 29 )'
            ],
            
            # 2. Retentions = False
            [
                # ISSQN > 10
                'apply_threshold( ( ( base_calculo * percentual_issqn ) / decimal(100) ), 10 )',
                'decimal(0)', 
                'decimal(0)', 
                'decimal(0)', 
                'decimal(0)', 
                'decimal(0)'
            ]
        ]
    }
}
