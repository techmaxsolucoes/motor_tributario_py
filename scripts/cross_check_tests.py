import os
import re
from collections import defaultdict
from pathlib import Path

# Configuration
CS_TEST_DIR = "/home/maxwell/Rule/MotorTributarioNet/src/TestesUnitarios"
PY_TEST_DIR = "/home/maxwell/Rule/motor_tributario_py/tests"

# Keywords to group tests
# Order matters: more specific first
TOPICS = [
    ("IBS", ["Ibs", "test_ibs"]),
    ("CBS", ["Cbs", "test_cbs"]),
    ("ICMS_ST", ["IcmsSt", "icms_st"]),
    ("ICMS_Desonerado", ["Desonerado", "icms_desonerado"]),
    ("ICMS_Monofasico", ["Monofasico", "icms_monofasico"]),
    ("ICMS_Credito", ["CreditoIcms", "credito_icms"]),
    ("ICMS_Efetivo", ["IcmsEfetivo", "icms_efetivo"]),
    ("FCP", ["Fcp", "fcp"]),
    ("PIS", ["Pis", "test_pis"]),
    ("COFINS", ["Cofins", "test_cofins"]),
    ("IPI", ["Ipi", "test_ipi"]),
    ("ISSQN", ["Issqn", "Iss", "issqn"]),
    ("DIFAL", ["Difal", "difal"]),
    ("IBPT", ["Ibpt", "ibpt"]),
    ("Servico", ["Servico"]),
    ("CSOSN", ["Csosn", "csosn"]),
    # Generic last
    ("ICMS_General", ["CalculaIcms", "CalcularIcms", "Testa_Calculo_CST00", "test_icms.py", "test_icms::"]), 
]

def parse_cs_tests(root_dir):
    tests = []
    files = Path(root_dir).rglob("*.cs")
    for f in files:
        if "UtilsTestes" in str(f):
            continue
        content = f.read_text(encoding="utf-8")
        # Find [Fact] or [Theory] followed by public void MethodName
        # simplified regex
        matches = re.findall(r'\[(Fact|Theory)[^\]]*\]\s*public\s+void\s+(\w+)', content, re.DOTALL)
        for _, method_name in matches:
            tests.append(f"{f.name}::{method_name}")
    return tests

def parse_py_tests(root_dir):
    tests = []
    files = Path(root_dir).rglob("test_*.py")
    for f in files:
        content = f.read_text(encoding="utf-8")
        matches = re.findall(r'def\s+(test_\w+)', content)
        for method_name in matches:
            tests.append(f"{f.name}::{method_name}")
    return tests

def classify_test(test_name, topics):
    parts = test_name.split("::")
    method_name = parts[-1] if len(parts) > 1 else test_name
    
    # Priority 1: Check method name only
    name_lower = method_name.lower()
    for topic, keywords in topics:
        for k in keywords:
            if k.lower() in name_lower:
                return topic

    # Priority 2: Check full string (filename included)
    full_lower = test_name.lower()
    for topic, keywords in topics:
        for k in keywords:
            if k.lower() in full_lower:
                return topic
                
    return "Other"

def main():
    print(f"Scanning C#: {CS_TEST_DIR}")
    cs_tests = parse_cs_tests(CS_TEST_DIR)
    
    print(f"Scanning Py: {PY_TEST_DIR}")
    py_tests = parse_py_tests(PY_TEST_DIR)
    
    cs_grouped = defaultdict(list)
    py_grouped = defaultdict(list)
    
    for t in cs_tests:
        topic = classify_test(t, TOPICS)
        cs_grouped[topic].append(t)
        
    for t in py_tests:
        topic = classify_test(t, TOPICS)
        py_grouped[topic].append(t)
        
    all_topics = sorted(set(cs_grouped.keys()) | set(py_grouped.keys()))
    
    print("\n" + "="*80)
    print(f"{'Topic':<20} | {'C# Count':<10} | {'Py Count':<10} | {'Status':<10}")
    print("-" * 80)
    
    total_cs = 0
    total_py = 0
    
    for topic in all_topics:
        c_count = len(cs_grouped[topic])
        p_count = len(py_grouped[topic])
        total_cs += c_count
        total_py += p_count
        
        status = "OK" if p_count >= c_count else "MISSING"
        if c_count == 0 and p_count > 0: status = "EXTRA"
        
        print(f"{topic:<20} | {c_count:<10} | {p_count:<10} | {status:<10}")

    print("-" * 80)
    print(f"{'TOTAL':<20} | {total_cs:<10} | {total_py:<10} |")
    print("="*80)

    print("\nDetailed Missing Check (Topics with MISSING):")
    for topic in all_topics:
        if len(py_grouped[topic]) < len(cs_grouped[topic]):
            print(f"\nTopic: {topic}")
            print("C# Tests:")
            for t in sorted(cs_grouped[topic]):
                print(f"  - {t}")
            print("Py Tests:")
            for t in sorted(py_grouped[topic]):
                print(f"  - {t}")

if __name__ == "__main__":
    main()
