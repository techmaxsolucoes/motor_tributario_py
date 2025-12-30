"""
Audit management for motor_tributario_py.
Provides high-level interface for debugging facade executions.
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from decimal import Decimal
import json

from bkflow_dmn.audit import start_audit, stop_audit, AuditTrail, DecisionTrace


@dataclass
class ExecutionReport:
    """Complete execution report including result and audit trail."""
    method_name: str
    inputs: Dict[str, Any]
    result: Any
    audit_trail: Optional[AuditTrail] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        def convert_value(v):
            if isinstance(v, Decimal):
                return float(v)
            elif hasattr(v, '__dict__'):
                return {k: convert_value(val) for k, val in v.__dict__.items()}
            elif isinstance(v, list):
                return [convert_value(item) for item in v]
            elif isinstance(v, dict):
                return {k: convert_value(val) for k, val in v.items()}
            return v
        
        report = {
            'method_name': self.method_name,
            'inputs': convert_value(self.inputs),
            'result': convert_value(self.result),
        }
        
        if self.audit_trail:
            report['audit_trail'] = {
                'traces': [
                    {
                        'table_title': trace.table_title,
                        'facts': convert_value(trace.facts),
                        'matched_rules': trace.matched_rules,
                        'rule_count': len(trace.rule_results),
                        'final_result': convert_value(trace.final_result),
                        # Enhanced: Include rule details
                        'matched_rule_details': [
                            {
                                'rule_number': rule_idx + 1,
                                'input_conditions': {
                                    col_id: (trace.input_expressions[rule_idx][i] if isinstance(trace.input_expressions[rule_idx], list) else trace.input_expressions[rule_idx])
                                    for i, col_id in enumerate(trace.input_col_ids)
                                    if rule_idx < len(trace.input_expressions) and 
                                       (isinstance(trace.input_expressions[rule_idx], str) or 
                                        (i < len(trace.input_expressions[rule_idx]) and trace.input_expressions[rule_idx][i].strip()))
                                } if trace.input_expressions and rule_idx < len(trace.input_expressions) else {},
                                'output_calculations': {
                                    col_id: {
                                        'expression': (trace.output_expressions[rule_idx][i] if isinstance(trace.output_expressions[rule_idx], list) else trace.output_expressions[rule_idx]),
                                        'evaluated': (trace.evaluated_outputs[rule_idx][i] if trace.evaluated_outputs and rule_idx < len(trace.evaluated_outputs) and isinstance(trace.evaluated_outputs[rule_idx], list) and i < len(trace.evaluated_outputs[rule_idx]) else ''),
                                        'result': convert_value(trace.final_result[0].get(col_id)) if trace.final_result else None
                                    }
                                    for i, col_id in enumerate(trace.output_col_ids)
                                    if rule_idx < len(trace.output_expressions)
                                } if trace.output_expressions and rule_idx < len(trace.output_expressions) else {}
                            }
                            for rule_idx in trace.matched_rules
                        ]
                    }
                    for trace in self.audit_trail.traces
                ]
            }
        
        return report
    
    def format_pretty(self) -> str:
        """Format as human-readable text."""
        lines = []
        lines.append(f"{'='*80}")
        lines.append(f"EXECUTION REPORT: {self.method_name}")
        lines.append(f"{'='*80}")
        lines.append("")
        
        lines.append("INPUTS:")
        for key, value in self.inputs.items():
            if key != 'tributavel':
                lines.append(f"  {key}: {value}")
        
        # Show Tributavel details
        if 'tributavel' in self.inputs:
            lines.append("\n  Tributavel:")
            trib = self.inputs['tributavel']
            for key, value in trib.items():
                if value and value != 0:  # Only show non-zero/non-empty values
                    lines.append(f"    {key}: {value}")
        lines.append("")
        
        if self.audit_trail and self.audit_trail.traces:
            lines.append("DECISION TRACE:")
            for i, trace in enumerate(self.audit_trail.traces, 1):
                lines.append(f"\n  [{i}] {trace.table_title}")
                lines.append(f"      Total Rules: {len(trace.rule_results)}")
                lines.append(f"      Matched: {trace.matched_rules}")
                
                # Show matched rule details
                for rule_idx in trace.matched_rules:
                    lines.append(f"\n      ━━━ Rule #{rule_idx + 1} ━━━")
                    
                    # Show input conditions
                    if trace.input_expressions and rule_idx < len(trace.input_expressions):
                        lines.append("      Input Conditions:")
                        input_row = trace.input_expressions[rule_idx]
                        if isinstance(input_row, str):
                            input_row = [input_row]
                        for col_id, expr in zip(trace.input_col_ids, input_row):
                            if expr and expr.strip():
                                lines.append(f"        • {col_id}: {expr}")
                    
                    # Show output calculations
                    if trace.output_expressions and rule_idx < len(trace.output_expressions):
                        lines.append("      Output Calculations:")
                        output_row = trace.output_expressions[rule_idx]
                        evaluated_row = trace.evaluated_outputs[rule_idx] if trace.evaluated_outputs and rule_idx < len(trace.evaluated_outputs) else []
                        if isinstance(output_row, str):
                            output_row = [output_row]
                        if isinstance(evaluated_row, str):
                            evaluated_row = [evaluated_row]
                        
                        for i, col_id in enumerate(trace.output_col_ids):
                            expr = output_row[i] if i < len(output_row) else ''
                            evaluated = evaluated_row[i] if i < len(evaluated_row) else ''
                            
                            # Get the actual calculated value
                            actual_value = None
                            if trace.final_result and len(trace.final_result) > 0:
                                actual_value = trace.final_result[0].get(col_id)
                            
                            lines.append(f"        • {col_id} = {expr}")
                            if evaluated and evaluated != expr:
                                lines.append(f"          Evaluated: {evaluated}")
                            if actual_value is not None:
                                lines.append(f"          → Result: {actual_value}")
        
        lines.append("")
        lines.append("FINAL RESULT:")
        if hasattr(self.result, '__dict__'):
            for key, value in self.result.__dict__.items():
                lines.append(f"  {key}: {value}")
        else:
            lines.append(f"  {self.result}")
        
        lines.append(f"\n{'='*80}")
        return '\n'.join(lines)


class AuditManager:
    """Manages audit sessions for facade method executions."""
    
    @staticmethod
    def debug_method(facade_instance, method_name: str, *args, **kwargs) -> ExecutionReport:
        """
        Execute a facade method with full audit tracing.
        
        Args:
            facade_instance: Instance of FacadeCalculadoraTributacao
            method_name: Name of the method to call (e.g., 'calcula_icms')
            *args, **kwargs: Arguments to pass to the method
            
        Returns:
            ExecutionReport with result and audit trail
        """
        # Capture inputs
        inputs = {
            'tributavel': facade_instance.tributavel.__dict__.copy(),
            'args': args,
            'kwargs': kwargs
        }
        
        # Start audit
        start_audit()
        
        try:
            # Execute method
            method = getattr(facade_instance, method_name)
            result = method(*args, **kwargs)
            
            # Stop audit and collect trail
            trail = stop_audit()
            
            return ExecutionReport(
                method_name=method_name,
                inputs=inputs,
                result=result,
                audit_trail=trail
            )
        except Exception as e:
            # Ensure audit is stopped even on error
            stop_audit()
            raise
