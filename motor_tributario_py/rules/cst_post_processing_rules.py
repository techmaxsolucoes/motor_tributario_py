from decimal import Decimal

# CST Post-Processing Rules
# Determines additional calculations needed after base ICMS calculation
# based on CST code

CST_POST_PROCESSING_RULE = {
    "title": "CST Post-Processing Rules",
    "hit_policy": "Unique",
    "inputs": {
        "cols": [
            {"id": "cst", "type": "string"}
        ],
        "rows": [
            ['"51"'],  # Diferimento
            ['"60"']   # ST Retido / Efetivo
        ]
    },
    "outputs": {
        "cols": [
            {"id": "calcular_diferimento", "type": "boolean"},
            {"id": "calcular_efetivo", "type": "boolean"},
            {"id": "modo_post_processing", "type": "string"}
        ],
        "rows": [
            # CST 51: Calculate diferimento
            ['true', 'false', '"Diferimento"'],
            # CST 60: Calculate efetivo (if percentual_icms_efetivo > 0)
            ['false', 'true', '"Efetivo"']
        ]
    }
}

# CST 51 Diferimento Calculation Rule
# Inputs: base_calculo, percentual_icms, percentual_diferimento
# Outputs: valor_icms_operacao, valor_icms_diferido, valor_final
CST_51_DIFERIMENTO_RULE = {
    "title": "CST 51 Diferimento Calculation",
    "hit_policy": "Unique",
    "inputs": {
        "cols": [
            {"id": "percentual_diferimento"}  # Should be > 0
        ],
        "rows": [
            ['percentual_diferimento > decimal(0)'],
            ['percentual_diferimento <= decimal(0)']  # Guard case
        ]
    },
    "outputs": {
        "cols": [
            {"id": "should_calculate", "type": "boolean"},
            {"id": "valor_icms_operacao"},
            {"id": "valor_icms_diferido"},
            {"id": "valor_final"}
        ],
        "rows": [
            # Calculate operation value, deferred value, and final ICMS
            # valor_icms_diferido will need ROUND_UP quantization in Python
            [
                'true',
                '(base_calculo * percentual_icms) / decimal(100)',
                '(((base_calculo * percentual_icms) / decimal(100)) * percentual_diferimento) / decimal(100)',
                '((base_calculo * percentual_icms) / decimal(100)) - ((((base_calculo * percentual_icms) / decimal(100)) * percentual_diferimento) / decimal(100))'
            ],
            # No diferimento percentage - return base ICMS value
            [
                'false',
                'decimal(0)',
                'decimal(0)',
                'decimal(0)'
            ]
        ]
    }
}
