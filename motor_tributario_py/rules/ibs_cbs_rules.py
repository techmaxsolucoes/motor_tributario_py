from decimal import Decimal

# IBS/CBS Base Calculation Rule
# Formula: vProd + vServ + vFrete + vSeg + vOutro - vDesc - vPis - vCofins - vIcms - vIssqn
# Note: vServ is implicit in product value if it's a service, or separate? 
# In C# code: baseCalculo = CalculaBaseDeCalculo() -> (vProd * Qty) + Frete + Seg + Outras.
# So "vServ" is just part of the product/service value.
IBS_CBS_BASE_RULE = {
    "title": "IBS/CBS Base Calculation",
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
            {"id": "base_calculo_ibs_cbs"}
        ],
        "rows": [
            [
                '( ( ( ( ( ( ( ( ( (valor_produto * quantidade_produto) + frete) + seguro) + outras_despesas) - desconto) + ajuste_pis) + ajuste_cofins) + ajuste_icms) + ajuste_issqn) )'
            ]
        ]
    }
}

# IBS Calculation Rule
# Value = Base * (Rate * (1 - Reduction/100)) / 100
IBS_CALC_RULE = {
    "title": "IBS Calculation",
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
            {"id": "valor_ibs"}
        ],
        "rows": [
            [
                '( ( base_calculo_ibs_cbs * ( percentual_ibs_uf * ( decimal(1) - ( percentual_reducao_ibs_uf / decimal(100) ) ) ) ) / decimal(100) )'
            ]
        ]
    }
}

# IBS Municipal Calculation Rule
# Value = Base * Rate / 100 (assuming simple rate for now, C# test implies it exists)
IBS_MUNICIPAL_CALC_RULE = {
    "title": "IBS Municipal Calculation",
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
            {"id": "valor_ibs_municipal"}
        ],
        "rows": [
            [
                '( ( base_calculo_ibs_cbs * ( percentual_ibs_municipal * ( decimal(1) - ( percentual_reducao_ibs_municipal / decimal(100) ) ) ) ) / decimal(100) )'
            ]
        ]
    }
}


# CBS Calculation Rule
# Value = Base * (Rate * (1 - Reduction/100)) / 100
CBS_CALC_RULE = {
    "title": "CBS Calculation",
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
            {"id": "valor_cbs"}
        ],
        "rows": [
            [
                '( ( base_calculo_ibs_cbs * ( percentual_cbs * ( decimal(1) - ( percentual_reducao_cbs / decimal(100) ) ) ) ) / decimal(100) )'
            ]
        ]
    }
}
