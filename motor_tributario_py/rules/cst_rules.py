# CST Dispatch Rules
# Determines which calculations are needed based on CST code

CST_DISPATCH_RULE = {
    "title": "CST Dispatch Rules",
    "hit_policy": "Unique",
    "inputs": {
        "cols": [
            {"id": "cst", "type": "string"}
        ],
        "rows": [
            ['"00"'],  # Tributada integralmente
            ['"10"'],  # Tributada com cobrança do ICMS por ST
            ['"20"'],  # Com redução de BC
            ['"30"'],  # Isenta ou não tributada com cobrança do ICMS por ST
            ['"40"'],  # Isenta
            ['"41"'],  # Não tributada
            ['"50"'],  # Suspensão
            ['"51"'],  # Diferimento
            ['"60"'],  # ICMS cobrado anteriormente por ST
            ['"70"'],  # Com redução de BC e cobrança do ICMS por ST
            ['"90"'],  # Outras
        ]
    },
    "outputs": {
        "cols": [
            {"id": "calcular_icms", "type": "boolean"},
            {"id": "calcular_icms_st", "type": "boolean"},
            {"id": "modo_calculo", "type": "string"}
        ],
        "rows": [
            # 00: ICMS only
            ['true', 'false', '"ICMS Only"'],
            # 10: ICMS + ST
            ['true', 'true', '"ICMS + ST"'],
            # 20: ICMS with reduction
            ['true', 'false', '"ICMS with Reduction"'],
            # 30: ST only (no ICMS proprio)
            ['false', 'true', '"ST Only"'],
            # 40: Exempt
            ['false', 'false', '"Exempt"'],
            # 41: Not taxed
            ['false', 'false', '"Not Taxed"'],
            # 50: Suspension
            ['false', 'false', '"Suspension"'],
            # 51: Deferral
            ['true', 'false', '"Deferral"'],
            # 60: ST already collected
            ['false', 'false', '"ST Already Collected"'],
            # 70: ICMS with reduction + ST
            ['true', 'true', '"ICMS with Reduction + ST"'],
            # 90: Other
            ['true', 'true', '"Other"'],
        ]
    }
}
