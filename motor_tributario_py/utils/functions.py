from decimal import Decimal
from bkflow_feel.utils import FEELFunctionsManager

def to_decimal(val):
    return Decimal(str(val))

def apply_threshold(val, limit):
    v = Decimal(str(val))
    l = Decimal(str(limit))
    return v if v > l else Decimal('0')

def check_threshold(test_val, limit, return_val):
    t = Decimal(str(test_val))
    l = Decimal(str(limit))
    r = Decimal(str(return_val))
    return r if t > l else Decimal('0')

def register_feel_functions():
    # FEELFunctionsManager expects dotted path string.
    REGISTER_FUNCS = {
        "decimal": "motor_tributario_py.utils.functions.to_decimal",
        "apply_threshold": "motor_tributario_py.utils.functions.apply_threshold",
        "check_threshold": "motor_tributario_py.utils.functions.check_threshold"
    }
    try:
        FEELFunctionsManager.register_funcs(REGISTER_FUNCS)
    except ValueError:
        # Already registered or partial registration error
        pass
