"""
Tests de Integración Completa

"""

import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from bauhaus_circular import quick_analysis
from bauhaus_circular.design_optimizer import DesignOptimizer
from bauhaus_circular.material_analyzer import MaterialAnalyzer
from bauhaus_circular.carbon_calculator import CarbonCalculator


class TestIntegration(unittest.TestCase):
    """Tests de integración completa del sistema"""
    
    def test_quick_analysis_integration(self):
        """Test de la función de análisis rápido"""
        materials = ['wood', 'glass', 'recycled_steel']
        quantities = [45.0, 12.0, 28.0]
        
        result = quick_analysis(materials, quantities, 'temperate')
        
        # Verificar estructura completa
        self.assertIn('current_design', result)
        self.assertIn('material_analysis', result)
        self.assertIn('carbon_analysis', result)
        self.assertIn('recommendations', result)
        self.assertIn('optimized_alternative', result)
        
        # Verificar datos básicos
        current = result['current_design']
        self.assertGreater(current['circularity_score'], 0)
        self.assertGreater(current['carbon_footprint_kg_co2'], 0)
        self.assertIsInstance(current['bauhaus_compliant'], bool)
    
    def test_full_workflow_integration(self):
        """Test del flujo de trabajo completo"""
        # 1. Inicializar componentes
        analyzer = MaterialAnalyzer()
        calculator = CarbonCalculator()
        optimizer = DesignOptimizer(analyzer, calculator)
        
        # 2. Datos de prueba
        materials = ['wood', 'bamboo', 'recycled_insulation']
        quantities = [35.0, 20.0, 15.0]
        
        # 3. Ejecutar análisis completo
        result = optimizer.optimize_design(
            materials, quantities, 'hot', budget_limit=40000
        )
        
        # 4. Verificar integración
        self.assertIn('budget_analysis', result)
        self.assertIn('climate_analysis', result)
        self.assertIn('improvement_potential_percent', result)
        
        # 5. Verificar que todos los análisis están conectados
        self.assertEqual(
            result['material_analysis']['circular_score'],
            result['current_design']['circularity_score']
        )
        self.assertEqual(
            result['carbon_analysis']['total_carbon'],
            result['current_design']['carbon_footprint_kg_co2']
        )
    
    def test_error_handling_integration(self):
        """Test de manejo de errores en integración"""
        # Materiales desconocidos deberían manejarse gracefulmente
        materials = ['wood', 'material_desconocido', 'glass']
        quantities = [30.0, 10.0, 15.0]
        
        result = quick_analysis(materials, quantities, 'temperate')
        
        # El sistema debería continuar funcionando incluso con materiales desconocidos
        self.assertIn('material_desconocido', result['material_analysis']['materials_not_found'])
        self.assertIn('recommendations', result)
        
        # Debería haber recomendaciones sobre el material desconocido
        unknown_recommendations = [
            rec for rec in result['recommendations'] 
            if 'desconocido' in rec.get('description', '') or 'unknown' in rec.get('description', '').lower()
        ]
        self.assertGreater(len(unknown_recommendations), 0)
    
    def test_climate_integration(self):
        """Test de integración con análisis climático"""
        climates = ['hot', 'temperate', 'cold']
        
        for climate in climates:
            with self.subTest(climate=climate):
                result = quick_analysis(
                    ['wood', 'glass'], 
                    [30.0, 15.0], 
                    climate
                )
                
                # Verificar que el análisis climático se integró correctamente
                self.assertEqual(result['climate_analysis']['climate'], climate)
                self.assertIn('overall_score', result['climate_analysis'])
                self.assertIn('thermal_mass_index', result['climate_analysis'])
                
                # Verificar que las recomendaciones consideran el clima
                climate_recommendations = [
                    rec for rec in result['recommendations'] 
                    if rec.get('type') == 'climate'
                ]
                if result['climate_analysis']['overall_score'] < 70:
                    self.assertGreater(len(climate_recommendations), 0)
    
    def test_optimized_alternative_integration(self):
        """Test de que la alternativa optimizada es coherente"""
        result = quick_analysis(
            ['low_carbon_concrete', 'glass', 'clay_brick'],
            [40.0, 15.0, 25.0],
            'temperate'
        )
        
        alternative = result['optimized_alternative']
        
        # La alternativa debería ser Bauhaus compliant
        self.assertTrue(alternative['bauhaus_compliant'])
        self.assertLessEqual(len(alternative['materials']), 3)
        
        # Debería tener mejor circularidad que el diseño actual
        self.assertGreater(
            alternative['circularity_score'],
            result['current_design']['circularity_score']
        )
        
        # Debería incluir análisis de mejoras
        self.assertIn('circularity_improvement', alternative['improvements'])
        self.assertIn('carbon_reduction_kg_co2', alternative['improvements'])


class TestPerformanceIntegration(unittest.TestCase):
    """Tests de rendimiento y estabilidad"""
    
    def test_large_project_integration(self):
        """Test con proyecto grande (múltiples materiales)"""
        materials = ['wood', 'glass', 'recycled_steel', 'bamboo', 'clay_brick']
        quantities = [100.0, 50.0, 75.0, 30.0, 60.0]
        
        result = quick_analysis(materials, quantities, 'temperate')
        
        # Verificar que maneja correctamente más de 3 materiales
        self.assertFalse(result['current_design']['bauhaus_compliant'])
        
        # Debería generar recomendaciones para reducir materiales
        bauhaus_recommendations = [
            rec for rec in result['recommendations'] 
            if rec.get('type') == 'bauhaus'
        ]
        self.assertGreater(len(bauhaus_recommendations), 0)
    
    def test_rapid_sequential_analysis(self):
        """Test de múltiples análisis secuenciales rápidos"""
        test_cases = [
            (['wood', 'glass'], [30.0, 15.0], 'hot'),
            (['recycled_steel', 'bamboo'], [25.0, 20.0], 'temperate'),
            (['rammed_earth', 'recycled_insulation'], [40.0, 10.0], 'cold')
        ]
        
        for i, (materials, quantities, climate) in enumerate(test_cases):
            with self.subTest(case=i):
                result = quick_analysis(materials, quantities, climate)
                
                # Cada análisis debería completarse exitosamente
                self.assertIn('current_design', result)
                self.assertIn('summary', result)
                self.assertIsInstance(result['summary'], str)


def run_integration_tests():
    """Función para ejecutar tests de integración manualmente"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestIntegration)
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1)