from decimal import Decimal

# IBPT Calculation Rule
# Inputs: 
# - valor_produto, quantidade_produto, desconto
# - Rates: percentual_federal, percentual_estadual, percentual_municipal, percentual_federal_importados
IBPT_CALC_RULE = {
    "title": "IBPT Calculation Rules",
    "hit_policy": "Unique",
    "inputs": {
        "cols": [
            {"id": "dummy"} # Single always-true row
        ],
        "rows": [
            ['1'] 
        ]
    },
    "outputs": {
        "cols": [
            {"id": "base_calculo"},
            {"id": "valor_federal"},
            {"id": "valor_estadual"},
            {"id": "valor_municipal"},
            {"id": "valor_federal_importados"}
        ],
        "rows": [
            [
                # Base = (Val * Qty) - Desc
                # Note: C# code uses "- _tributavel.Desconto".
                '( (valor_produto * quantidade_produto) - desconto )',
                
                # Federal
                '( ( ( (valor_produto * quantidade_produto) - desconto ) * percentual_federal ) / decimal(100) )',
                
                # Estadual
                '( ( ( (valor_produto * quantidade_produto) - desconto ) * percentual_estadual ) / decimal(100) )',
                
                # Municipal
                '( ( ( (valor_produto * quantidade_produto) - desconto ) * percentual_municipal ) / decimal(100) )',
                
                # Importados
                '( ( ( (valor_produto * quantidade_produto) - desconto ) * percentual_federal_importados ) / decimal(100) )'
            ]
        ]
    }
}
