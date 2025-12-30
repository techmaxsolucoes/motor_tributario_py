"""
Tests for audit/debug functionality.
"""
import unittest
from decimal import Decimal
from motor_tributario_py.models import Tributavel
from motor_tributario_py.facade import FacadeCalculadoraTributacao


class TestAudit(unittest.TestCase):
    
    def test_debug_execution_icms(self):
        """Test that debug_execution captures ICMS calculation trace."""
        produto = Tributavel(
            valor_produto=Decimal('100'),
            quantidade_produto=Decimal('1'),
            percentual_icms=Decimal('18'),
            cst="00"
        )
        
        facade = FacadeCalculadoraTributacao(produto)
        report = facade.debug_execution('calcula_icms')
        
        # Verify report structure
        self.assertEqual(report.method_name, 'calcula_icms')
        self.assertIsNotNone(report.result)
        self.assertIsNotNone(report.audit_trail)
        
        # Verify audit trail captured decision tables
        self.assertGreater(len(report.audit_trail.traces), 0)
        
        # Verify at least one trace is for ICMS
        trace_titles = [t.table_title for t in report.audit_trail.traces]
        self.assertTrue(any('ICMS' in title for title in trace_titles))
        
        # Verify matched rules are captured
        for trace in report.audit_trail.traces:
            self.assertIsInstance(trace.matched_rules, list)
            self.assertGreater(len(trace.rule_results), 0)
    
    def test_debug_execution_tributacao(self):
        """Test debug_execution with composite ResultadoTributacao."""
        produto = Tributavel(
            valor_produto=Decimal('1000'),
            quantidade_produto=Decimal('1'),
            percentual_icms=Decimal('18'),
            percentual_ipi=Decimal('10'),
            percentual_pis=Decimal('1.65'),
            percentual_cofins=Decimal('7.6'),
            cst="00"
        )
        
        facade = FacadeCalculadoraTributacao(produto)
        report = facade.debug_execution('calcula_tributacao')
        
        # Should have multiple traces (ICMS, IPI, PIS, COFINS, etc.)
        self.assertGreater(len(report.audit_trail.traces), 5)
        
        # Verify result is ResultadoTributacao
        self.assertTrue(hasattr(report.result, 'valor_icms'))
        self.assertTrue(hasattr(report.result, 'valor_ipi'))
    
    def test_format_pretty(self):
        """Test that pretty formatting works."""
        produto = Tributavel(
            valor_produto=Decimal('100'),
            percentual_icms=Decimal('18')
        )
        
        facade = FacadeCalculadoraTributacao(produto)
        report = facade.debug_execution('calcula_icms')
        
        formatted = report.format_pretty()
        
        # Verify key sections are present
        self.assertIn('EXECUTION REPORT', formatted)
        self.assertIn('INPUTS', formatted)
        self.assertIn('DECISION TRACE', formatted)
        self.assertIn('FINAL RESULT', formatted)
        self.assertIn('Rule #', formatted)  # Shows matched rule number
        self.assertIn('Input Conditions', formatted)
        self.assertIn('Output Calculations', formatted)
    
    def test_to_dict_serialization(self):
        """Test that to_dict produces JSON-serializable output."""
        produto = Tributavel(
            valor_produto=Decimal('100'),
            percentual_icms=Decimal('18')
        )
        
        facade = FacadeCalculadoraTributacao(produto)
        report = facade.debug_execution('calcula_icms')
        
        # Should not raise
        report_dict = report.to_dict()
        
        # Verify structure
        self.assertIn('method_name', report_dict)
        self.assertIn('inputs', report_dict)
        self.assertIn('result', report_dict)
        self.assertIn('audit_trail', report_dict)
        
        # Verify Decimals are converted to float
        import json
        json_str = json.dumps(report_dict)  # Should not raise
        self.assertIsInstance(json_str, str)


if __name__ == '__main__':
    unittest.main()
