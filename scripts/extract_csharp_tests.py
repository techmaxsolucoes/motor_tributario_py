import re
import json
import os
from pathlib import Path
from decimal import Decimal

# Configuration
CS_TEST_DIR = "/home/maxwell/Rule/MotorTributarioNet/src/TestesUnitarios"
OUTPUT_FILE = "/home/maxwell/Rule/motor_tributario_py/tests/fixtures.json"

# Regex Patterns
CLASS_PATTERN = re.compile(r'public\s+class\s+(\w+)')
METHOD_PATTERN = re.compile(r'\[Fact\]\s*public\s+void\s+(\w+)', re.DOTALL)
PRODUTO_BLOCK_PATTERN = re.compile(r'var\s+produto\s*=\s*new\s+Produto\s*\{(.*?)\};', re.DOTALL)
FACADE_PATTERN = re.compile(r'var\s+facade\s*=\s*new\s+FacadeCalculadoraTributacao\((.*?)\);')
RESULT_TRIB_PATTERN = re.compile(r'(?:var|ResultadoTributacao)\s+\w+\s*=\s*new\s+ResultadoTributacao\((.*?)\);', re.DOTALL)
CALCULATE_PATTERN = re.compile(r'(?:var\s+(\w+)\s*=\s*facade\.(Calcula\w+)\((.*?)\);|var\s+(\w+)\s*=\s*(\w+)\.(Calcular)\((.*?)\);)', re.DOTALL)
# New pattern for direct calculator instantiation (CSOSN/CST)
DIRECT_CALC_PATTERN = re.compile(r'var\s+(\w+)\s*=\s*new\s+(Csosn\d+|Cst\d+)\(\);', re.DOTALL)
DIRECT_CALC_CALL_PATTERN = re.compile(r'(\w+)\.Calcula\(produto\);', re.DOTALL)
ASSERT_PATTERN = re.compile(r'Assert\.Equal\((.*?),\s*(.*?)\);')

def parse_value(val_str):
    val_str = val_str.strip()
    if val_str.endswith('m'):
        return float(val_str[:-1]) # JSON doesn't support Decimal strictly, float typical for transport
    if val_str.endswith('f'):
        return float(val_str[:-1])
    if val_str.lower() == 'true':
        return True
    if val_str.lower() == 'false':
        return False
    if val_str.startswith('"') and val_str.endswith('"'):
        return val_str.strip('"')
    
    # Handle Enums (dot notation)
    # Heuristic: Variables (references) usually start with lowercase (e.g. 'resultado.Valor').
    # Enums/Classes usually start with Uppercase (e.g. 'Cst.Cst20', 'Tipo.Base').
    if '.' in val_str and val_str[0].isupper():
        parts = val_str.split('.')
        last = parts[-1]
        
        # CST Handling: Cst00 -> 00, Cst20 -> 20
        if last.startswith('Cst') and len(last) > 3 and last[3].isdigit():
            return last[3:]
            
        return last

    try:
        return float(val_str)
    except:
        return val_str

def extract_tests(root_dir):
    extracted_tests = []
    
    files = Path(root_dir).rglob("*.cs")
    for f in files:
        if "UtilsTestes" in str(f):
            continue
            
        content = f.read_text(encoding="utf-8")
        
        # Split by [Fact] to handle methods roughly
        # This is a naive parser; for robust parsing we'd need a real grammar, but predictable style allows this.
        
        # We need to preserve class name
        class_match = CLASS_PATTERN.search(content)
        group_name = class_match.group(1).replace("Test", "") if class_match else "Unknown"
        
        # Split content into method blocks based on [Fact]
        # We find indices of [Fact]
        fact_indices = [m.start() for m in re.finditer(r'\[Fact\]', content)]
        
        for i, start_idx in enumerate(fact_indices):
            end_idx = fact_indices[i+1] if i+1 < len(fact_indices) else len(content)
            block = content[start_idx:end_idx]
            
            # Extract Method Name
            method_match = re.search(r'public\s+void\s+(\w+)', block)
            if not method_match:
                continue
            test_case_name = method_match.group(1)
            
            # Extract Produto
            prod_match = PRODUTO_BLOCK_PATTERN.search(block)
            inputs = {}
            if prod_match:
                block_content = prod_match.group(1)
                # Remove single line comments
                block_content = re.sub(r'//.*', '', block_content)
                # Remove multi line comments if any (though C# test usu uses //)
                block_content = re.sub(r'/\*.*?\*/', '', block_content, flags=re.DOTALL)
                
                lines = block_content.split(',')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    if '=' in line:
                        key, val = line.split('=', 1)
                        inputs[key.strip()] = parse_value(val.strip())
            
            # Extract Facade & Calculator
            facade_match = FACADE_PATTERN.search(block)
            facade_args = {}
            if facade_match:
                args_str = facade_match.group(1)
                if "TipoDesconto" in args_str:
                     if "Condincional" in args_str:
                         facade_args["tipo_desconto"] = "Condicional"
                     elif "Incondicional" in args_str:
                         facade_args["tipo_desconto"] = "Incondicional"
            
            # Extract ResultadoTributacao (Integration Tests)
            res_trib_match = RESULT_TRIB_PATTERN.search(block)
            if res_trib_match:
                # new ResultadoTributacao(produto, Crt.RegimeNormal, TipoOperacao.OperacaoInterna, TipoPessoa.Fisica);
                args_str = res_trib_match.group(1)
                # Parse args by comma, detecting keywords
                # CRT
                if "RegimeNormal" in args_str: facade_args["crt"] = "RegimeNormal"
                if "SimplesNacional" in args_str: facade_args["crt"] = "SimplesNacional"
                # TipoOperacao
                if "OperacaoInterna" in args_str: facade_args["tipo_operacao"] = "OperacaoInterna"
                if "OperacaoInterestadual" in args_str: facade_args["tipo_operacao"] = "OperacaoInterestadual"
                # TipoPessoa
                if "Fisica" in args_str: facade_args["tipo_pessoa"] = "Fisica"
                if "Juridica" in args_str: facade_args["tipo_pessoa"] = "Juridica"
                
                # Desonerado Type
                if "BaseSimples" in args_str: facade_args["tipo_calculo_icms_desonerado"] = "BaseSimples"
                if "BasePorDentro" in args_str: facade_args["tipo_calculo_icms_desonerado"] = "BasePorDentro"

            # Find ALL calculator calls
            executions = []
            result_vars = {} # map var_name -> method_name for reference

            # Check for direct calculator instantiation (CSOSN/CST pattern)
            direct_calc_match = DIRECT_CALC_PATTERN.search(block)
            if direct_calc_match:
                var_name = direct_calc_match.group(1)
                calc_class = direct_calc_match.group(2)  # e.g., "Csosn101", "Cst00"
                
                # Map calculator class to facade method
                # CSOSN -> calcula_csosn, CST -> calcula_icms (CST is handled by ICMS calculator)
                if calc_class.startswith('Csosn'):
                    method_name = 'calcula_csosn'
                    csosn_number = calc_class[5:]  # Extract number from "Csosn101"
                    # Add CSOSN to both facade_args and inputs
                    facade_args['csosn'] = int(csosn_number)
                    inputs['Csosn'] = int(csosn_number)  # Also set on Tributavel
                elif calc_class.startswith('Cst'):
                    method_name = 'calcula_icms'
                    cst_number = calc_class[3:]  # Extract number from "Cst00"
                    # Add CST to inputs so it gets set on Tributavel
                    inputs['Cst'] = cst_number
                
                # Check if .Calcula(produto) is called
                if DIRECT_CALC_CALL_PATTERN.search(block):
                    executions.append({
                        "var_name": var_name,
                        "method": method_name,
                        "args": []
                    })
                    result_vars[var_name] = method_name

            # Also check for facade pattern
            calc_matches = CALCULATE_PATTERN.finditer(block)
            for match in calc_matches:
                # Group 1-3: facade.CalculaX pattern
                # Group 4-7: obj.Calcular pattern (from new regex parts)
                
                if match.group(2): # facade pattern
                    res_var = match.group(1)
                    c_method = match.group(2)
                    args_str = match.group(3)
                else: # Integration pattern
                    res_var = match.group(4)
                    c_method = "CalculaTributacao" if match.group(6) == "Calcular" else "Unknown"
                    args_str = match.group(7)
                
                py_method = re.sub(r'(?<!^)(?=[A-Z])', '_', c_method).lower()
                
                c_args = []
                if args_str:
                    args_list = args_str.split(',')
                    for arg in args_list:
                         c_args.append(parse_value(arg))
                
                executions.append({
                    "var_name": res_var,
                    "method": py_method,
                    "args": c_args
                })
                result_vars[res_var] = py_method

            # Extract Asserts
            asserts = []
            assert_matches = ASSERT_PATTERN.findall(block)
            for expected, actual in assert_matches:
                # Find which result var is being asserted on in 'actual'
                # e.g. actual = "resultadoCalculoIbsUF.BaseCalculo"
                
                target_var = None
                target_prop = None
                
                # Check against known result vars
                for rv in result_vars.keys():
                    if rv in actual:
                        # Found the target variable
                        target_var = rv
                        # Try to extract property
                        # Regex: rv + "." + (Prop)
                        prop_match = re.search(f"{rv}\.(\w+)", actual)
                        if prop_match:
                            target_prop = prop_match.group(1)
                        break
                
                if target_var and target_prop:
                     assert_val = parse_value(expected)
                     
                     # Check if expected is also a variable reference?
                     # e.g. Assert.Equal(res1.Prop, res2.Prop)
                     # For now, store exactly as is in JSON. Runner will handle resolution.
                     
                     asserts.append({
                         "type": "Equal",
                         "target_var": target_var,
                         "prop": target_prop,
                         "expected": assert_val # Could be value or string ref
                     })

            if inputs and executions:
                 extracted_tests.append({
                    "group": group_name,
                    "testcase": test_case_name,
                    "inputs": inputs,
                    "facade_args": facade_args,
                    "executions": executions,
                    "asserts": asserts
                })

    return extracted_tests

def main():
    print(f"Scanning {CS_TEST_DIR}...")
    tests = extract_tests(CS_TEST_DIR)
    print(f"Found {len(tests)} tests.")
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(tests, f, indent=4)
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
