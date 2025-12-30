from decimal import Decimal

# ICMS Monofásico Rule
# Inputs: CST, QtyBase, AdRem, ReducaoAdRem, Biodiesel%, OriginarioUF%, QtyBaseRetAnt, AdRemRetAnt
# Output: Valor, ValorRet, ValorOp, ValorDif, ValorRetAnt
ICMS_MONOFASICO_RULE = {
    "title": "ICMS Monofásico Calculation",
    "hit_policy": "Unique",
    "inputs": {
        "cols": [
            {"id": "cst"}
        ],
        "rows": [
            ['"02"'], # CST 02
            ['"15"'], # CST 15
            ['"53"'], # CST 53
            ['"61"']  # CST 61
        ]
    },
    "outputs": {
        "cols": [
            {"id": "valor_icms_monofasico"},
            {"id": "valor_icms_monofasico_retencao"},
            {"id": "valor_icms_monofasico_operacao"},
            {"id": "valor_icms_monofasico_diferido"},
            {"id": "valor_icms_monofasico_retido_anteriormente"}
        ],
        "rows": [
            # CST 02: Val = QtyBase * AdRem
            [
                '( quantidade_base_calculo_icms_monofasico * aliquota_ad_rem_icms )',
                'decimal(0)', 'decimal(0)', 'decimal(0)', 'decimal(0)'
            ],
            
            # CST 15: 
            # AliqRed = AdRem * (1 - Red/100)
            # QtyBaseProp = QtyBase * (1 - Bio/100)
            # Val = QtyBaseProp * AliqRed
            # QtyRet = QtyBase * (Bio/100)
            # ValRet = (QtyRet * AdRem) * (Orig/100)
            [
                '( ( quantidade_base_calculo_icms_monofasico * ( decimal(1) - ( percentual_biodiesel / decimal(100) ) ) ) * ( aliquota_ad_rem_icms * ( decimal(1) - ( percentual_reducao_aliquota_ad_rem_icms / decimal(100) ) ) ) )',
                '( ( ( quantidade_base_calculo_icms_monofasico * ( percentual_biodiesel / decimal(100) ) ) * aliquota_ad_rem_icms ) * ( percentual_originario_uf / decimal(100) ) )',
                'decimal(0)', 'decimal(0)', 'decimal(0)'
            ],
            
            # CST 53:
            # Val = (QtyBase * AdRem) - (QtyBase * AdRem * Orig/100) -> QtyBase * AdRem * (1 - Orig/100)
            # ValOp = QtyBase * AdRem
            # ValDif = QtyBase * AdRem * Orig/100
            [
                '( ( quantidade_base_calculo_icms_monofasico * aliquota_ad_rem_icms ) - ( ( quantidade_base_calculo_icms_monofasico * aliquota_ad_rem_icms ) * ( percentual_originario_uf / decimal(100) ) ) )',
                'decimal(0)',
                '( quantidade_base_calculo_icms_monofasico * aliquota_ad_rem_icms )',
                '( ( quantidade_base_calculo_icms_monofasico * aliquota_ad_rem_icms ) * ( percentual_originario_uf / decimal(100) ) )',
                'decimal(0)'
            ],
            
            # CST 61:
            # ValRetAnt = QtyBaseRetAnt * AdRemRetAnt
            [
                 'decimal(0)', 'decimal(0)', 'decimal(0)', 'decimal(0)',
                 '( quantidade_base_calculo_icms_monofasico_retido_anteriormente * aliquota_ad_rem_icms_retido_anteriormente )'
            ]
        ]
    }
}
