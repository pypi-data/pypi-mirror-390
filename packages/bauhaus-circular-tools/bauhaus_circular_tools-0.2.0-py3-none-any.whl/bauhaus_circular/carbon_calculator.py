"""
Calculador de Carbono Embebido

Principios Bauhaus aplicados:
- Racionalidad científica (decisiones basadas en datos)
- Eficiencia como valor estético
- Honestidad (mostrar verdadero costo ambiental)

Autora: Mary Magali Villca Cruz
Email: arqmaryvillca@gmail.com
"""

from typing import Dict, List, Optional
import warnings


class CarbonCalculator:
    """
    Calculador de huella de carbono para diseños arquitectónicos.
    
    Basado en principios de racionalidad científica y honestidad material
    de la escuela Bauhaus aplicados a la sostenibilidad moderna.
    """
    
    def __init__(self):
        # Baseline convencional (materiales no sostenibles)
        self.conventional_baseline = {
            'wood': 250.0,
            'recycled_steel': 2500.0,
            'bamboo': 250.0,
            'glass': 1200.0,
            'recycled_insulation': 150.0,
            'low_carbon_concrete': 350.0,
            'rammed_earth': 30.0,
            'clay_brick': 300.0
        }
        
        # Intensidad de carbono de materiales circulares
        self.circular_materials_carbon = {
            'wood': 150.0,
            'recycled_steel': 850.0,
            'bamboo': 120.0,
            'glass': 850.0,
            'recycled_insulation': 50.0,
            'low_carbon_concrete': 180.0,
            'rammed_earth': 30.0,
            'clay_brick': 220.0
        }

    def calculate_embodied_carbon(self, material_quantities: Dict[str, float]) -> Dict:
        """
        Calcula carbono embebido basado en cantidades de materiales.
        
        Args:
            material_quantities: Diccionario {material: cantidad_m3}
        
        Returns:
            dict: Resultados del cálculo de carbono
        
        Example:
            >>> calculator = CarbonCalculator()
            >>> result = calculator.calculate_embodied_carbon({'wood': 45, 'glass': 12})
            >>> print(f"Carbono total: {result['total_carbon']} kgCO2e")
        """
        total_carbon = 0.0
        conventional_total = 0.0
        carbon_breakdown = {}
        
        for material, quantity in material_quantities.items():
            # Carbono del material circular
            circular_carbon_intensity = self.circular_materials_carbon.get(material, 300.0)
            material_carbon = circular_carbon_intensity * quantity
            
            # Carbono del material convencional
            conventional_intensity = self.conventional_baseline.get(material, 300.0)
            conventional_material_carbon = conventional_intensity * quantity
            
            total_carbon += material_carbon
            conventional_total += conventional_material_carbon
            
            carbon_breakdown[material] = {
                'carbon_kg_co2': material_carbon,
                'quantity_m3': quantity,
                'carbon_intensity': circular_carbon_intensity,
                'conventional_intensity': conventional_intensity,
                'carbon_savings': conventional_material_carbon - material_carbon
            }
        
        # Calcular ahorros
        total_savings = conventional_total - total_carbon
        savings_percent = (total_savings / conventional_total * 100) if conventional_total > 0 else 0
        
        # Validación: carbono total negativo
        if total_carbon < 0:
            warnings.warn("El carbono total calculado es negativo. Verifique las cantidades.")
        
        # ARREGLADO: Evitar división por cero
        total_quantity = sum(material_quantities.values())
        carbon_per_m3 = total_carbon / total_quantity if total_quantity > 0 else 0.0
        
        return {
            'total_carbon': total_carbon,
            'conventional_baseline': conventional_total,
            'carbon_savings_absolute': max(0, total_savings),
            'carbon_savings_percent': max(0, savings_percent),
            'carbon_breakdown': carbon_breakdown,
            'performance_rating': self._get_performance_rating(savings_percent),
            'carbon_per_m3': carbon_per_m3
        }

    def calculate_carbon_footprint(self, 
                                   user_materials: List[str], 
                                   quantities: List[float]) -> Dict:
        """
        Calcula huella de carbono total (método alternativo).
        
        Args:
            user_materials: Lista de materiales
            quantities: Lista de cantidades en m³
        
        Returns:
            dict: Carbono total, desglose, ahorros
        """
        # ARREGLADO: Manejar listas de diferente longitud rellenando con 1.0
        if len(user_materials) > len(quantities):
            # Extender quantities con 1.0 para los materiales faltantes
            quantities_extended = quantities + [1.0] * (len(user_materials) - len(quantities))
        else:
            quantities_extended = quantities[:len(user_materials)]  # Truncar si hay más quantities
        
        # Convertir a formato de diccionario
        material_dict = dict(zip(user_materials, quantities_extended))
        return self.calculate_embodied_carbon(material_dict)
    
    def _get_performance_rating(self, savings_percent: float) -> str:
        """Califica el desempeño de carbono basado en ahorros."""
        if savings_percent >= 50:
            return "🏆 EXCELENTE - Diseño circular de clase mundial"
        elif savings_percent >= 30:
            return "✅ BUENO - Alto desempeño ambiental"
        elif savings_percent >= 15:
            return "⚠️ MODERADO - Espacio para mejora"
        else:
            return "❌ DEFICIENTE - Considere materiales más circulares"
    
    def compare_materials(self, material_a: str, material_b: str, 
                         quantity: float = 1.0) -> Dict:
        """
        Compara impacto de carbono entre dos materiales.
        
        Args:
            material_a: Primer material a comparar
            material_b: Segundo material a comparar
            quantity: Cantidad en m³ (por defecto 1.0)
        
        Returns:
            dict: Comparación detallada entre materiales
        """
        carbon_a = self.circular_materials_carbon.get(material_a, 300.0) * quantity
        carbon_b = self.circular_materials_carbon.get(material_b, 300.0) * quantity
        
        difference = abs(carbon_a - carbon_b)
        percent_diff = (difference / max(carbon_a, carbon_b)) * 100
        better_material = material_a if carbon_a < carbon_b else material_b
        
        return {
            'material_a': {
                'name': material_a,
                'carbon_kg_co2': carbon_a,
                'intensity': self.circular_materials_carbon.get(material_a, 300.0)
            },
            'material_b': {
                'name': material_b,
                'carbon_kg_co2': carbon_b,
                'intensity': self.circular_materials_carbon.get(material_b, 300.0)
            },
            'difference_kg_co2': difference,
            'percent_difference': percent_diff,
            'better_choice': better_material,
            'recommendation': f"Use {better_material} para ahorrar {difference:.0f} kgCO2e"
        }

    def get_carbon_intensity(self, material: str) -> Optional[float]:
        """
        Obtiene la intensidad de carbono de un material específico.
        
        Args:
            material: Nombre del material
        
        Returns:
            float: Intensidad de carbono en kgCO2/m³, o None si no existe
        """
        # ARREGLADO: Asegurar que siempre devuelve float
        intensity = self.circular_materials_carbon.get(material)
        return float(intensity) if intensity is not None else None

    def list_materials_by_carbon(self) -> List[Dict]:
        """
        Lista materiales ordenados por intensidad de carbono (menor a mayor).
        
        Returns:
            list: Materiales con su información de carbono
        """
        materials = []
        for name, carbon in self.circular_materials_carbon.items():
            conventional = self.conventional_baseline.get(name, carbon)
            savings = conventional - carbon
            savings_percent = (savings / conventional * 100) if conventional > 0 else 0
            
            materials.append({
                'name': name,
                'carbon_intensity': carbon,
                'conventional_intensity': conventional,
                'carbon_savings': savings,
                'savings_percent': savings_percent
            })
        
        return sorted(materials, key=lambda x: x['carbon_intensity'])

    def calculate_project_savings(self, material_quantities: Dict[str, float]) -> Dict:
        """
        Calcula ahorros específicos del proyecto vs baseline convencional.
        
        Args:
            material_quantities: Diccionario de materiales y cantidades
        
        Returns:
            dict: Ahorros detallados del proyecto
        """
        result = self.calculate_embodied_carbon(material_quantities)
        
        savings_breakdown = {}
        for material, data in result['carbon_breakdown'].items():
            savings_breakdown[material] = {
                'circular_carbon': data['carbon_kg_co2'],
                'conventional_carbon': data['conventional_intensity'] * data['quantity_m3'],
                'savings': data['carbon_savings'],
                'savings_percent': (data['carbon_savings'] / 
                                  (data['conventional_intensity'] * data['quantity_m3']) * 100)
            }
        
        return {
            'total_savings_kg_co2': result['carbon_savings_absolute'],
            'total_savings_percent': result['carbon_savings_percent'],
            'savings_breakdown': savings_breakdown,
            'equivalent_trees': result['carbon_savings_absolute'] / 22.0,  # 1 árbol absorbe ~22 kgCO2/año
            'equivalent_cars': result['carbon_savings_absolute'] / 4200.0   # 1 auto emite ~4200 kgCO2/año
        }