from decimal import Decimal

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
