"""
Tests Completos para el Analizador de Materiales

Autora: Mary Magali Villca Cruz
Email: arqmaryvillca@gmail.com
"""

import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from bauhaus_circular.material_analyzer import MaterialAnalyzer, MaterialCategory


class TestMaterialAnalyzer(unittest.TestCase):
    """Test cases completos para MaterialAnalyzer"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.analyzer = MaterialAnalyzer()
        self.valid_materials = ['wood', 'glass', 'recycled_steel']
    
    def test_initialization(self):
        """Test de inicialización correcta"""
        self.assertIsNotNone(self.analyzer)
        self.assertEqual(self.analyzer.MAX_MATERIALS, 3)
        self.assertEqual(len(self.analyzer.circular_materials), 8)
        
        # Verificar que todos los materiales tienen la estructura correcta
        for material_name, material_data in self.analyzer.circular_materials.items():
            self.assertIn('category', material_data)
            self.assertIn('carbon_kg_co2_m3', material_data)
            self.assertIn('reuse_potential', material_data)
            self.assertIn('recyclability', material_data)
            self.assertIn('cost_usd_m3', material_data)
            self.assertIn('bauhaus_compliant', material_data)
    
    def test_analyze_materials_bauhaus_compliant(self):
        """Test de análisis con 3 materiales (cumple Bauhaus)"""
        result = self.analyzer.analyze_materials(self.valid_materials)
        
        self.assertTrue(result['bauhaus_compliant'])
        self.assertEqual(len(result['materials_found']), 3)
        self.assertEqual(len(result['materials_not_found']), 0)
        self.assertGreater(result['circular_score'], 0)
        self.assertGreater(result['avg_reuse_potential'], 0)
        self.assertIsInstance(result['recommendations'], list)
        self.assertIsInstance(result['material_details'], list)
    
    def test_analyze_materials_non_compliant(self):
        """Test de análisis con más de 3 materiales (no cumple Bauhaus)"""
        materials = ['wood', 'glass', 'recycled_steel', 'bamboo']
        result = self.analyzer.analyze_materials(materials)
        
        self.assertFalse(result['bauhaus_compliant'])
        self.assertEqual(len(result['materials_found']), 4)
        self.assertIn('Simplify Material Palette', 
                     ' '.join([rec['title'] for rec in result['recommendations']]))
    
    def test_analyze_materials_with_unknown(self):
        """Test de análisis con materiales desconocidos"""
        materials = ['wood', 'material_desconocido', 'glass']
        result = self.analyzer.analyze_materials(materials)
        
        self.assertIn('material_desconocido', result['materials_not_found'])
        self.assertIn('wood', result['materials_found'])
        self.assertIn('glass', result['materials_found'])
        
        # Verificar que hay recomendaciones sobre materiales desconocidos
        unknown_recommendations = [
            rec for rec in result['recommendations']
            if 'UNKNOWN' in rec.get('title', '') or 'desconocido' in rec.get('description', '').lower()
        ]
        self.assertGreater(len(unknown_recommendations), 0)
    
    def test_analyze_materials_empty(self):
        """Test de análisis con lista vacía"""
        result = self.analyzer.analyze_materials([])
        
        self.assertTrue(result['bauhaus_compliant'])
        self.assertEqual(result['circular_score'], 0)
        self.assertEqual(result['avg_reuse_potential'], 0)
        self.assertEqual(len(result['materials_found']), 0)
        self.assertEqual(len(result['materials_not_found']), 0)
    
    def test_analyze_materials_single(self):
        """Test de análisis con un solo material"""
        result = self.analyzer.analyze_materials(['wood'])
        
        self.assertTrue(result['bauhaus_compliant'])
        self.assertEqual(len(result['materials_found']), 1)
        self.assertGreater(result['circular_score'], 0)
        self.assertEqual(result['material_details'][0]['name'], 'wood')
    
    def test_calculate_circularity_score(self):
        """Test del cálculo específico de score de circularidad"""
        score = self.analyzer.calculate_circularity_score(['wood', 'glass'])
        
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        
        # Score debería ser mayor para materiales más circulares
        high_circular_score = self.analyzer.calculate_circularity_score(['wood', 'bamboo'])
        low_circular_score = self.analyzer.calculate_circularity_score(['low_carbon_concrete'])
        self.assertGreater(high_circular_score, low_circular_score)
    
    def test_calculate_circularity_score_edge_cases(self):
        """Test de edge cases para cálculo de circularidad"""
        # Lista vacía
        self.assertEqual(self.analyzer.calculate_circularity_score([]), 0)
        
        # Materiales desconocidos
        self.assertEqual(self.analyzer.calculate_circularity_score(['unknown1', 'unknown2']), 0)
        
        # Mix de conocidos y desconocidos
        mixed_score = self.analyzer.calculate_circularity_score(['wood', 'unknown'])
        self.assertGreater(mixed_score, 0)
    
    def test_suggest_alternatives_valid(self):
        """Test de sugerencia de alternativas para material válido"""
        alternatives = self.analyzer.suggest_alternatives('wood')
        
        self.assertIsInstance(alternatives, list)
        self.assertLessEqual(len(alternatives), 3)
        
        if alternatives:
            for alt in alternatives:
                self.assertIn('name', alt)
                self.assertIn('circular_score', alt)
                self.assertIn('carbon_reduction', alt)
                self.assertIn('cost_difference', alt)
                self.assertIn('description', alt)
                
                # Verificar que las alternativas son del mismo tipo
                original_category = self.analyzer.circular_materials['wood']['category']
                alt_category = self.analyzer.circular_materials[alt['name']]['category']
                self.assertEqual(original_category, alt_category)
    
    def test_suggest_alternatives_invalid(self):
        """Test de sugerencia de alternativas para material inválido"""
        alternatives = self.analyzer.suggest_alternatives('material_inexistente')
        self.assertEqual(alternatives, [])
    
    def test_get_material_info_valid(self):
        """Test de obtención de información de material válido"""
        info = self.analyzer.get_material_info('wood')
        
        self.assertIsNotNone(info)
        self.assertEqual(info['category'], MaterialCategory.STRUCTURAL)
        self.assertEqual(info['carbon_kg_co2_m3'], 150)
        self.assertEqual(info['reuse_potential'], 0.90)
        self.assertEqual(info['recyclability'], 0.95)
        self.assertTrue(info['bauhaus_compliant'])
        self.assertTrue(info['natural_finish'])
    
    def test_get_material_info_invalid(self):
        """Test de obtención de información de material inválido"""
        info = self.analyzer.get_material_info('material_inexistente')
        self.assertIsNone(info)
    
    def test_list_available_materials(self):
        """Test de listado de materiales disponibles"""
        materials = self.analyzer.list_available_materials()
        
        expected_materials = [
            'wood', 'recycled_steel', 'bamboo', 'glass', 
            'recycled_insulation', 'low_carbon_concrete', 
            'rammed_earth', 'clay_brick'
        ]
        
        self.assertIsInstance(materials, list)
        self.assertEqual(len(materials), 8)
        self.assertEqual(set(materials), set(expected_materials))
    
    def test_material_categories(self):
        """Test de categorías de materiales"""
        # Verificar que cada material tiene una categoría válida
        for material_name in self.analyzer.list_available_materials():
            material_info = self.analyzer.get_material_info(material_name)
            self.assertIsInstance(material_info['category'], MaterialCategory)
            self.assertIn(material_info['category'], [MaterialCategory.STRUCTURAL, 
                                                     MaterialCategory.ENVELOPE, 
                                                     MaterialCategory.FINISHING])
    
    def test_material_properties_ranges(self):
        """Test de rangos válidos para propiedades de materiales"""
        for material_name in self.analyzer.list_available_materials():
            material_info = self.analyzer.get_material_info(material_name)
            
            # Carbon debe ser positivo
            self.assertGreaterEqual(material_info['carbon_kg_co2_m3'], 0)
            
            # Reuse y recyclability entre 0 y 1
            self.assertGreaterEqual(material_info['reuse_potential'], 0)
            self.assertLessEqual(material_info['reuse_potential'], 1)
            self.assertGreaterEqual(material_info['recyclability'], 0)
            self.assertLessEqual(material_info['recyclability'], 1)
            
            # Costo positivo
            self.assertGreaterEqual(material_info['cost_usd_m3'], 0)
            
            # Lifespan positivo
            self.assertGreaterEqual(material_info['lifespan_years'], 0)


class TestMaterialAnalyzerEdgeCases(unittest.TestCase):
    """Tests de casos extremos para MaterialAnalyzer"""
    
    def setUp(self):
        self.analyzer = MaterialAnalyzer()
    
    def test_duplicate_materials(self):
        """Test con materiales duplicados en la lista"""
        materials = ['wood', 'wood', 'glass']
        result = self.analyzer.analyze_materials(materials)
        
        # Debería manejar duplicados correctamente
        self.assertEqual(len(result['materials_found']), 3)  # Incluye duplicados
        self.assertTrue(result['bauhaus_compliant'])  # 3 elementos = límite (debería ser compliant)
    
    def test_mixed_case_materials(self):
        """Test con diferentes casos en nombres de materiales"""
        materials = ['Wood', 'GLASS', 'Recycled_Steel']  # Mayúsculas diferentes
        result = self.analyzer.analyze_materials(materials)
        
        # Debería ser case-sensitive
        self.assertEqual(len(result['materials_found']), 0)
        self.assertEqual(len(result['materials_not_found']), 3)
    
    def test_special_characters_materials(self):
        """Test con caracteres especiales en nombres"""
        materials = ['wood!', 'glass@', 'steel#']
        result = self.analyzer.analyze_materials(materials)
        
        self.assertEqual(len(result['materials_found']), 0)
        self.assertEqual(len(result['materials_not_found']), 3)
    
    def test_none_input(self):
        """Test con entrada None"""
        with self.assertRaises(TypeError):
            self.analyzer.analyze_materials(None)


def run_material_tests():
    """Función para ejecutar tests manualmente"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestMaterialAnalyzer)
    suite.addTests(loader.loadTestsFromTestCase(TestMaterialAnalyzerEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_material_tests()
    sys.exit(0 if success else 1)