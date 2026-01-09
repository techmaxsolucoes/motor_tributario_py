from decimal import Decimal

# ICMS Efetivo Preprocessing Rule
# Determines if calculation should proceed and calculates component adjustments
ICMS_EFETIVO_PREPROCESSING_RULE = {
    "title": "ICMS Efetivo Preprocessing",
    "hit_policy": "Unique",
    "inputs": {
        "cols": [
            {"id": "percentual_icms_efetivo"},
            {"id": "is_ativo"}  # "true"/"false"
        ],
        "rows": [
            ['percentual_icms_efetivo = decimal(0)', ''],    # Zero percentage
            ['percentual_icms_efetivo > decimal(0)', 'true'],  # Positive percentage, is active asset
            ['percentual_icms_efetivo > decimal(0)', 'false']  # Positive percentage, not active asset
        ]
    },
    "outputs": {
        "cols": [
            {"id": "should_calculate", "type": "boolean"},
            {"id": "ipi_adjustment", "type": "string"}  # "add_to_outras_despesas" or "none"
        ],
        "rows": [
            ['false', '"none"'],                    # Skip if zero
            ['true', '"add_to_outras_despesas"'],   # Include IPI for active assets
            ['true', '"none"']                       # No IPI adjustment
        ]
    }
}

# ICMS Efetivo Base Rule
# Inputs: valor_produto, quantidade_produto, frete, seguro, outras_despesas, desconto, tipo_desconto, percentual_reducao_icms_efetivo
# Logic: Base = ((Val * Qty + Exp) [+/- Desc]) * (1 - Red/100)
# Note: IPI should be added to outras_despesas before calling this rule if is_ativo
ICMS_EFETIVO_BASE_RULE = {
    "title": "ICMS Efetivo Base Calculation",
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
        "cols": [{"id": "base_calculo_efetivo"}],
        "rows": [
            # Condicional: (Gross + Desc) * (1 - Red/100)
            [
                '( ( ( ( ( ( valor_produto * quantidade_produto ) + frete ) + seguro ) + outras_despesas ) + desconto ) * ( decimal(1) - ( percentual_reducao_icms_efetivo / decimal(100) ) ) )'
            ],
            # Incondicional: (Gross - Desc) * (1 - Red/100)
            [
                '( ( ( ( ( ( valor_produto * quantidade_produto ) + frete ) + seguro ) + outras_despesas ) - desconto ) * ( decimal(1) - ( percentual_reducao_icms_efetivo / decimal(100) ) ) )'
            ]
        ]
    }
}

ICMS_EFETIVO_CALC_RULE = {
    "title": "ICMS Efetivo Calculation",
    "hit_policy": "Unique",
    "inputs": {
        "cols": [{"id": "dummy"}],
        "rows": [['1']]
    },
    "outputs": {
        "cols": [{"id": "valor_icms_efetivo"}],
        "rows": [
            ['( ( base_calculo_efetivo * percentual_icms_efetivo ) / decimal(100) )']
        ]
    }
}
