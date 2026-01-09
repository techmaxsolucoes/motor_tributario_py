from decimal import Decimal

# Credito ICMS Preprocessing Rule
# Determines the base calculation strategy for credito
# Key insight: Credito should use ICMS base with percentual_reducao = 0
CREDITO_ICMS_PREPROCESSING_RULE = {
    "title": "Credito ICMS Preprocessing",
    "hit_policy": "Unique",
    "inputs": {
        "cols": [
            {"id": "dummy"}
        ],
        "rows": [
            ['1']
        ]
    },
    "outputs": {
        "cols": [
            {"id": "percentual_reducao_override", "type": "number"},
            {"id": "calculation_strategy", "type": "string"}
        ],
        "rows": [
            # Credito always uses reduction = 0 for base calculation
            ['0', '"use_icms_base_without_reduction"']
        ]
    }
}

# Credito ICMS Rule
# Inputs: Base (selected by Calculator based on Doc Type), Rate
# Logic: Value = Base * Rate/100
CREDITO_ICMS_CALC_RULE = {
    "title": "Credito ICMS Calculation",
    "hit_policy": "Unique",
    "inputs": {
        "cols": [
            {"id": "dummy"}
        ],
        "rows": [
            ['1'] 
        ]
    },
    "outputs": {
        "cols": [
            {"id": "valor_credito_icms"}
        ],
        "rows": [
            [
                '( ( base_calculo_credito * percentual_credito ) / decimal(100) )'
            ]
        ]
    }
}
