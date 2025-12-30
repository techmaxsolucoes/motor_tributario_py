CSOSN_DISPATCH_RULE = {
    "title": "CSOSN Dispatch Rules",
    "hit_policy": "Unique",
    "inputs": {
        "cols": [
            {"id": "csosn", "type": "number"}
        ],
        "rows": [
            ['101'],
            ['102'],
            ['103'],
            ['201'],
            ['202'],
            ['203'],
            ['300'],
            ['400'],
            ['500'],
            ['900']
        ]
    },
    "outputs": {
        "cols": [
            {"id": "calcular_icms_proprio", "type": "boolean"},
            {"id": "calcular_icms_st", "type": "boolean"},
            {"id": "calcular_credito", "type": "boolean"},
            {"id": "calcular_efetivo", "type": "boolean"},
            {"id": "modo_calculo", "type": "string"}
        ],
        "rows": [
            # 101: Credito
            ['false', 'false', 'true', 'false', '"Credito Only"'],
            # 102/103: Exempt
            ['false', 'false', 'false', 'false', '"Exempt"'],
            ['false', 'false', 'false', 'false', '"Exempt"'],
            # 201: Credito + ST
            ['false', 'true', 'true', 'false', '"Credito + ST"'],
            # 202/203: ST Only
            ['false', 'true', 'false', 'false', '"ST Only"'],
            ['false', 'true', 'false', 'false', '"ST Only"'],
            # 300/400: Exempt
            ['false', 'false', 'false', 'false', '"Exempt"'],
            ['false', 'false', 'false', 'false', '"Exempt"'],
            # 500: Efetivo (conditional in code usually, but here we can flag it)
            ['false', 'false', 'false', 'true', '"CSOSN 500 Efetivo"'],
            # 900: All
            ['true', 'true', 'true', 'false', '"All (900)"']
        ]
    }
}
