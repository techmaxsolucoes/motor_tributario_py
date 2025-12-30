from decimal import Decimal

# ICMS Efetivo Base Rule
# Inputs: valor_produto, quantidade_produto, frete, seguro, outras_despesas, desconto, tipo_desconto, percentual_reducao_icms_efetivo
# Logic: Base = ((Val * Qty + Exp) [+/- Desc]) * (1 - Red/100)
# Note: IPI is added if is_ativo (handled in input to rule or inside rule?)
# C#: `(CalculaBaseDeCalculo() + (_tributavel.IsAtivo...? Ipi : 0))`
# We will pass the pre-calculated "Gross Base with IPI if applicable" as input to keep rule simple, or compute it in rule. 
# Let's compute in rule.
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
