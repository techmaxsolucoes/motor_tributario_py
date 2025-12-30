from decimal import Decimal

# ICMS Desonerado Rule
# Inputs:
# - base_calculo (Calculated externally via ICMS Base Rule)
# - subtotal_produto (Val * Qty)
# - cst (String: "20", "30", "40", "70")
# - tipo_calculo (String: "BaseSimples", "BasePorDentro")
# - percentual_icms, percentual_reducao
ICMS_DESONERADO_CALC_RULE = {
    "title": "ICMS Desonerado Calculation Rules",
    "hit_policy": "First", # First match wins (BasePorDentro specific cases first)
    "inputs": {
        "cols": [
            {"id": "tipo_calculo"},      # "BaseSimples" / "BasePorDentro"
            {"id": "cst_group"}          # "GroupA" (20,70), "GroupB" (30,40), or "-"
        ],
        "rows": [
            # 1. Base Simples (Any CST)
            ['"BaseSimples"', '"-"'],
            
            # 2. Base Por Dentro - CST 20 or 70
            ['"BasePorDentro"', '"GroupA"'],
            
            # 3. Base Por Dentro - CST 30 or 40
            ['"BasePorDentro"', '"GroupB"']
        ]
    },
    "outputs": {
        "cols": [
            {"id": "valor_icms_desonerado"}
        ],
        "rows": [
            # 1. Base Simples: Base * Rate
            ['( base_calculo * (percentual_icms / decimal(100)) )'],
            
            # 2. Base Por Dentro (Group A: 20, 70)
            # Formula: ((Base * (1 - (Rate * (1 - Reducao)))) / (1 - Rate)) - Base
            # Rate = percentual_icms / 100
            # Reducao = percentual_reducao / 100
            [
                '( ( ( subtotal_produto * ( decimal(1) - ( (percentual_icms / decimal(100)) * ( decimal(1) - (percentual_reducao / decimal(100)) ) ) ) ) / ( decimal(1) - (percentual_icms / decimal(100)) ) ) - subtotal_produto )'
            ],
            
            # 3. Base Por Dentro (Group B: 30, 40)
            # Formula: (Base / (1 - Rate)) * Rate
            # Note: "Base" here refers to "subtotal_produto" (Price in invoice) based on C# code logic for 30/40? 
            # C# Logic: return (valorBase / (1 - aliquota)) * aliquota;
            # Where valorBase is passed as subtotalProduto for BasePorDentro.
            [
                '( ( subtotal_produto / ( decimal(1) - (percentual_icms / decimal(100)) ) ) * (percentual_icms / decimal(100)) )'
            ]
        ]
    }
}
