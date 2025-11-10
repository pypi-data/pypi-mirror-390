"""
Tests para el Optimizador de Diseño Circular

"""

import unittest
import sys
import os

# Agregar el directorio src al path para importar los módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from bauhaus_circular.design_optimizer import DesignOptimizer
from bauhaus_circular.material_analyzer import MaterialAnalyzer
from bauhaus_circular.carbon_calculator import CarbonCalculator


class TestDesignOptimizer(unittest.TestCase):
    """Test cases para DesignOptimizer"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.optimizer = DesignOptimizer()
        self.test_materials = ['wood', 'glass', 'recycled_steel']
        self.test_quantities = [45.0, 12.0, 28.0]
    
    def test_initialization_default(self):
        """Test de inicialización con dependencias por defecto"""
        optimizer = DesignOptimizer()
        self.assertIsNotNone(optimizer.material_analyzer)
        self.assertIsNotNone(optimizer.carbon_calculator)
        self.assertIn('hot', optimizer.climate_strategies)
        self.assertIn('temperate', optimizer.climate_strategies)
        self.assertIn('cold', optimizer.climate_strategies)
    
    def test_initialization_custom_dependencies(self):
        """Test de inicialización con dependencias personalizadas"""
        material_analyzer = MaterialAnalyzer()
        carbon_calculator = CarbonCalculator()
        optimizer = DesignOptimizer(material_analyzer, carbon_calculator)
        
        self.assertEqual(optimizer.material_analyzer, material_analyzer)
        self.assertEqual(optimizer.carbon_calculator, carbon_calculator)
    
    def test_optimize_design_basic(self):
        """Test básico de optimización de diseño"""
        result = self.optimizer.optimize_design(
            self.test_materials, 
            self.test_quantities,
            'temperate'
        )
        
        # Verificar estructura básica del resultado
        self.assertIn('current_design', result)
        self.assertIn('material_analysis', result)
        self.assertIn('carbon_analysis', result)
        self.assertIn('recommendations', result)
        self.assertIn('optimized_alternative', result)
        self.assertIn('summary', result)
        
        # Verificar tipos de datos
        self.assertIsInstance(result['current_design']['circularity_score'], float)
        self.assertIsInstance(result['current_design']['carbon_footprint_kg_co2'], float)
        self.assertIsInstance(result['current_design']['total_cost_usd'], float)
        self.assertIsInstance(result['current_design']['bauhaus_compliant'], bool)
    
    def test_optimize_design_different_climates(self):
        """Test de optimización para diferentes zonas climáticas"""
        climates = ['hot', 'temperate', 'cold']
        
        for climate in climates:
            with self.subTest(climate=climate):
                result = self.optimizer.optimize_design(
                    ['wood', 'glass'],
                    [30.0, 15.0],
                    climate
                )
                
                self.assertEqual(result['climate_analysis']['climate'], climate)
                self.assertIsInstance(result['climate_analysis']['overall_score'], (int, float))
                self.assertGreaterEqual(result['climate_analysis']['overall_score'], 0)
                self.assertLessEqual(result['climate_analysis']['overall_score'], 100)
    
    def test_optimize_design_with_budget(self):
        """Test de optimización con límite de presupuesto"""
        result_with_budget = self.optimizer.optimize_design(
            self.test_materials,
            self.test_quantities,
            'temperate',
            budget_limit=50000.0
        )
        
        # Verificar que se incluye análisis de presupuesto
        self.assertIn('budget_analysis', result_with_budget)
        self.assertIn('within_budget', result_with_budget['budget_analysis'])
        self.assertIn('budget_utilization', result_with_budget['budget_analysis'])
    
    def test_optimize_design_error_cases(self):
        """Test de casos de error"""
        # Listas de longitud diferente
        with self.assertRaises(ValueError):
            self.optimizer.optimize_design(
                ['wood', 'glass'],
                [30.0],  # Solo una cantidad para dos materiales
                'temperate'
            )
    
    def test_quick_assessment(self):
        """Test de evaluación rápida"""
        assessment = self.optimizer.quick_assessment(
            self.test_materials,
            self.test_quantities
        )
        
        # Verificar estructura del resultado
        self.assertIn('overall_score', assessment)
        self.assertIn('circularity_score', assessment)
        self.assertIn('carbon_savings_percent', assessment)
        self.assertIn('bauhaus_compliant', assessment)
        self.assertIn('performance_level', assessment)
        
        # Verificar rangos de valores
        self.assertGreaterEqual(assessment['overall_score'], 0)
        self.assertLessEqual(assessment['overall_score'], 100)
        self.assertIn(assessment['performance_level'], ['Alto', 'Medio', 'Bajo'])
    
    def test_calculate_costs(self):
        """Test de cálculo de costos"""
        costs = self.optimizer._calculate_costs(
            self.test_materials,
            self.test_quantities
        )
        
        self.assertIn('total_cost', costs)
        self.assertIn('cost_breakdown', costs)
        self.assertIn('cost_per_m3_avg', costs)
        
        # Verificar que el costo total es positivo
        self.assertGreaterEqual(costs['total_cost'], 0)
        
        # Verificar que hay un breakdown para cada material
        for material in self.test_materials:
            self.assertIn(material, costs['cost_breakdown'])
    
    def test_evaluate_climate_fit(self):
        """Test de evaluación de adecuación climática"""
        climate_fit = self.optimizer._evaluate_climate_fit(
            self.test_materials,
            self.test_quantities,
            'temperate'
        )
        
        self.assertIn('climate', climate_fit)
        self.assertIn('thermal_mass_index', climate_fit)
        self.assertIn('overall_score', climate_fit)
        self.assertIn('recommended_strategy', climate_fit)
        self.assertIn('issues', climate_fit)
        self.assertIn('strengths', climate_fit)
        
        # Verificar rangos
        self.assertGreaterEqual(climate_fit['overall_score'], 0)
        self.assertLessEqual(climate_fit['overall_score'], 100)
        self.assertGreaterEqual(climate_fit['thermal_mass_index'], 0)
    
    def test_generate_recommendations(self):
        """Test de generación de recomendaciones"""
        # Primero necesitamos los análisis completos
        result = self.optimizer.optimize_design(
            self.test_materials,
            self.test_quantities,
            'temperate'
        )
        
        recommendations = self.optimizer._generate_recommendations(
            result['material_analysis'],
            result['carbon_analysis'],
            result['climate_analysis'],
            result['cost_analysis'],
            'temperate',
            None
        )
        
        # Verificar que es una lista de diccionarios con estructura esperada
        self.assertIsInstance(recommendations, list)
        if recommendations:
            first_rec = recommendations[0]
            self.assertIn('priority', first_rec)
            self.assertIn('type', first_rec)
            self.assertIn('title', first_rec)
            self.assertIn('description', first_rec)
            self.assertIn('impact', first_rec)
            self.assertIn('action', first_rec)
    
    def test_calculate_improvement_potential(self):
        """Test de cálculo de potencial de mejora"""
        result = self.optimizer.optimize_design(
            self.test_materials,
            self.test_quantities,
            'temperate'
        )
        
        improvement = self.optimizer._calculate_improvement_potential(
            result['material_analysis'],
            result['carbon_analysis']
        )
        
        # Verificar que es un número entre 0 y 100
        self.assertIsInstance(improvement, float)
        self.assertGreaterEqual(improvement, 0)
        self.assertLessEqual(improvement, 100)
    
    def test_generate_optimized_alternative(self):
        """Test de generación de alternativa optimizada"""
        alternative = self.optimizer._generate_optimized_alternative(
            self.test_materials,
            self.test_quantities,
            'temperate',
            None
        )
        
        # Verificar estructura básica
        self.assertIn('materials', alternative)
        self.assertIn('quantities_m3', alternative)
        self.assertIn('circularity_score', alternative)
        self.assertIn('carbon_footprint_kg_co2', alternative)
        self.assertIn('improvements', alternative)
        self.assertIn('rationale', alternative)
        
        # Verificar que tiene máximo 3 materiales (principio Bauhaus)
        self.assertLessEqual(len(alternative['materials']), 3)
        
        # Verificar que las mejoras son números
        improvements = alternative['improvements']
        self.assertIsInstance(improvements['circularity_improvement'], (int, float))
        self.assertIsInstance(improvements['carbon_reduction_kg_co2'], (int, float))
    
    def test_generate_summary(self):
        """Test de generación de resumen ejecutivo"""
        result = self.optimizer.optimize_design(
            self.test_materials,
            self.test_quantities,
            'temperate'
        )
        
        summary = self.optimizer._generate_summary(
            result['material_analysis'],
            result['carbon_analysis'],
            result['improvement_potential_percent'],
            result['budget_analysis']
        )
        
        # Verificar que es un string no vacío
        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary), 0)
        
        # Verificar que contiene palabras clave esperadas
        self.assertTrue(
            any(word in summary for word in ['DISEÑO', 'Bauhaus', 'materiales', 'potencial']),
            f"El resumen debería contener palabras clave relevantes: {summary}"
        )
    
    def test_check_budget_with_limit(self):
        """Test de verificación de presupuesto con límite"""
        # Caso dentro del presupuesto
        budget_status = self.optimizer._check_budget(30000, 50000)
        self.assertTrue(budget_status['within_budget'])
        self.assertLessEqual(budget_status['budget_utilization'], 100)
        
        # Caso excede presupuesto
        budget_status = self.optimizer._check_budget(60000, 50000)
        self.assertFalse(budget_status['within_budget'])
        self.assertGreater(budget_status['budget_utilization'], 100)
    
    def test_check_budget_no_limit(self):
        """Test de verificación de presupuesto sin límite"""
        budget_status = self.optimizer._check_budget(30000, None)
        self.assertTrue(budget_status['within_budget'])
        self.assertEqual(budget_status['budget_utilization'], 0)
    
    def test_optimize_design_with_unknown_materials(self):
        """Test con materiales desconocidos en la base de datos"""
        materials_with_unknown = ['wood', 'unknown_material', 'glass']
        quantities = [30.0, 10.0, 15.0]
        
        result = self.optimizer.optimize_design(
            materials_with_unknown,
            quantities,
            'temperate'
        )
        
        # Verificar que el análisis se completa incluso con materiales desconocidos
        self.assertIn('unknown_material', result['material_analysis']['materials_not_found'])
        self.assertIn('wood', result['material_analysis']['materials_found'])
        
        # Verificar que hay recomendaciones sobre materiales desconocidos
        unknown_recommendations = [
            rec for rec in result['recommendations'] 
            if 'unknown_material' in rec.get('description', '')
        ]
        self.assertGreater(len(unknown_recommendations), 0)
    
    def test_optimize_design_single_material(self):
        """Test con un solo material (caso mínimo)"""
        result = self.optimizer.optimize_design(
            ['wood'],
            [50.0],
            'temperate'
        )
        
        # Verificar que funciona con un solo material
        self.assertEqual(len(result['current_design']['materials']), 1)
        self.assertTrue(result['current_design']['bauhaus_compliant'])
        self.assertGreater(result['current_design']['circularity_score'], 0)
    
    def test_optimize_design_empty_materials(self):
        """Test con lista vacía de materiales"""
        with self.assertRaises(ValueError):
            self.optimizer.optimize_design([], [], 'temperate')
    
    def test_climate_strategies_content(self):
        """Test del contenido de las estrategias climáticas"""
        strategies = self.optimizer.climate_strategies
        
        for climate, strategy in strategies.items():
            self.assertIn('thermal_mass', strategy)
            self.assertIn('insulation', strategy)
            self.assertIn('ventilation', strategy)
            self.assertIn('glazing', strategy)
            self.assertIn('materials_recommended', strategy)
            self.assertIn('description', strategy)
            
            # Verificar que hay materiales recomendados
            self.assertGreater(len(strategy['materials_recommended']), 0)
            self.assertLessEqual(len(strategy['materials_recommended']), 3)


class TestDesignOptimizerIntegration(unittest.TestCase):
    """Tests de integración para DesignOptimizer"""
    
    def setUp(self):
        """Configuración para tests de integración"""
        self.material_analyzer = MaterialAnalyzer()
        self.carbon_calculator = CarbonCalculator()
        self.optimizer = DesignOptimizer(self.material_analyzer, self.carbon_calculator)
    
    def test_integration_workflow(self):
        """Test de flujo de trabajo completo integrado"""
        # Paso 1: Análisis de materiales
        material_analysis = self.material_analyzer.analyze_materials(['wood', 'glass'])
        self.assertIn('circular_score', material_analysis)
        
        # Paso 2: Cálculo de carbono
        carbon_analysis = self.carbon_calculator.calculate_carbon_footprint(
            ['wood', 'glass'], [30.0, 15.0]
        )
        self.assertIn('total_carbon', carbon_analysis)
        
        # Paso 3: Optimización completa
        optimization_result = self.optimizer.optimize_design(
            ['wood', 'glass'], [30.0, 15.0], 'temperate'
        )
        
        # Verificar que todos los componentes están integrados
        self.assertIn('material_analysis', optimization_result)
        self.assertIn('carbon_analysis', optimization_result)
        self.assertIn('climate_analysis', optimization_result)
        self.assertIn('cost_analysis', optimization_result)
        
        # Verificar consistencia entre análisis individual e integrado
        self.assertEqual(
            material_analysis['circular_score'],
            optimization_result['material_analysis']['circular_score']
        )
    
    def test_alternative_optimization_comparison(self):
        """Test de comparación entre diseño actual y alternativa optimizada"""
        result = self.optimizer.optimize_design(
            ['low_carbon_concrete', 'glass'],
            [40.0, 20.0],
            'temperate'
        )
        
        alternative = result['optimized_alternative']
        
        # Verificar que la alternativa tiene mejor score de circularidad
        self.assertGreater(
            alternative['circularity_score'],
            result['current_design']['circularity_score']
        )
        
        # Verificar que sigue el principio Bauhaus (máx 3 materiales)
        self.assertLessEqual(len(alternative['materials']), 3)
        self.assertTrue(alternative['bauhaus_compliant'])


def run_tests():
    """Función para ejecutar los tests manualmente"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestDesignOptimizer)
    suite.addTests(loader.loadTestsFromTestCase(TestDesignOptimizerIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # Ejecutar tests cuando se corre el archivo directamente
    success = run_tests()
    sys.exit(0 if success else 1)