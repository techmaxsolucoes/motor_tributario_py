from decimal import Decimal

# FCP Rule
# Inputs: Base ICMS (calculated externally or passed), Rate
# Logic: Value = Base * Rate/100
FCP_CALC_RULE = {
    "title": "FCP Calculation",
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
            {"id": "valor_fcp"}
        ],
        "rows": [
            [
                '( ( base_calculo_icms * percentual_fcp ) / decimal(100) )'
            ]
        ]
    }
}
