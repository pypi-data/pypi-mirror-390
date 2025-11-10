"""
Optimizador de Diseño Circular

Principios Bauhaus aplicados:
- Gesamtkunstwerk (obra de arte total integrada)
- Unidad de todos los elementos
- Pedagogía (enseña al arquitecto)

Autora: Mary Magali Villca Cruz
Email: arqmaryvillca@gmail.com
"""

from typing import List, Dict, Optional
from .material_analyzer import MaterialAnalyzer
from .carbon_calculator import CarbonCalculator


class DesignOptimizer:
    """
    Optimizador que integra análisis de materiales + carbono + clima.
    
    Aplica principios Bauhaus de simplicidad, verdad material y unidad
    para crear diseños arquitectónicos circulares y sostenibles.
    """
    
    def __init__(self, material_analyzer: Optional[MaterialAnalyzer] = None, 
                 carbon_calculator: Optional[CarbonCalculator] = None):
        """
        Inicializa el optimizador de diseño.
        
        Args:
            material_analyzer: Instancia de MaterialAnalyzer (opcional)
            carbon_calculator: Instancia de CarbonCalculator (opcional)
        """
        self.material_analyzer = material_analyzer or MaterialAnalyzer()
        self.carbon_calculator = carbon_calculator or CarbonCalculator()
        
        # Configuración climática basada en principios de diseño pasivo
        self.climate_strategies = {
            'hot': {
                'thermal_mass': 'high',
                'insulation': 'moderate',
                'ventilation': 'high',
                'glazing': 'low',
                'materials_recommended': ['rammed_earth', 'clay_brick', 'wood'],
                'description': 'Enfoque en masa térmica y ventilación natural'
            },
            'temperate': {
                'thermal_mass': 'moderate',
                'insulation': 'high',
                'ventilation': 'moderate',
                'glazing': 'moderate',
                'materials_recommended': ['wood', 'recycled_steel', 'glass'],
                'description': 'Balance entre aislamiento y ganancia solar'
            },
            'cold': {
                'thermal_mass': 'moderate',
                'insulation': 'very_high',
                'ventilation': 'low',
                'glazing': 'high',
                'materials_recommended': ['recycled_insulation', 'wood', 'clay_brick'],
                'description': 'Máximo aislamiento y ganancia solar'
            }
        }

    def optimize_design(self, 
                       user_materials: List[str], 
                       quantities: List[float],
                       climate: str = 'temperate',
                       budget_limit: Optional[float] = None) -> Dict:
        """
        Optimización completa del diseño basada en principios Bauhaus.
        
        Args:
            user_materials: Materiales seleccionados
            quantities: Cantidades en m³
            climate: Zona climática ('hot', 'temperate', 'cold')
            budget_limit: Presupuesto máximo en USD (opcional)
        
        Returns:
            dict: Análisis completo con recomendaciones y alternativa optimizada
        
        Example:
            >>> optimizer = DesignOptimizer()
            >>> result = optimizer.optimize_design(['wood', 'glass'], [45, 12], 'temperate')
            >>> print(f"Score circular: {result['current_design']['circularity_score']}%")
        """
        # Validar entradas
        if len(user_materials) != len(quantities):
            raise ValueError("La lista de materiales y cantidades deben tener la misma longitud")
        
        # ARREGLADO: Validar lista vacía
        if not user_materials or not quantities:
            raise ValueError("La lista de materiales y cantidades no puede estar vacía")
        
        # Análisis de materiales
        material_analysis = self.material_analyzer.analyze_materials(user_materials)
        
        # Cálculo de carbono
        carbon_analysis = self.carbon_calculator.calculate_carbon_footprint(
            user_materials, quantities
        )
        
        # Evaluación climática
        climate_fit = self._evaluate_climate_fit(user_materials, quantities, climate)
        
        # Cálculo de costos
        cost_analysis = self._calculate_costs(user_materials, quantities)
        
        # Verificación de presupuesto
        budget_status = self._check_budget(cost_analysis['total_cost'], budget_limit)
        
        # Recomendaciones integradas
        recommendations = self._generate_recommendations(
            material_analysis, carbon_analysis, climate_fit, 
            cost_analysis, climate, budget_limit
        )
        
        # Potencial de mejora
        improvement_potential = self._calculate_improvement_potential(
            material_analysis, carbon_analysis
        )
        
        # Alternativa optimizada
        optimized_alternative = self._generate_optimized_alternative(
            user_materials, quantities, climate, budget_limit
        )
        
        return {
            'current_design': {
                'materials': user_materials,
                'quantities_m3': quantities,
                'circularity_score': material_analysis['circular_score'],
                'carbon_footprint_kg_co2': carbon_analysis['total_carbon'],
                'carbon_savings_percent': carbon_analysis['carbon_savings_percent'],
                'total_cost_usd': cost_analysis['total_cost'],
                'bauhaus_compliant': material_analysis['bauhaus_compliant'],
                'climate_fit_score': climate_fit['overall_score']
            },
            'material_analysis': material_analysis,
            'carbon_analysis': carbon_analysis,
            'climate_analysis': climate_fit,
            'cost_analysis': cost_analysis,
            'budget_analysis': budget_status,
            'recommendations': recommendations,
            'improvement_potential_percent': improvement_potential,
            'optimized_alternative': optimized_alternative,
            'summary': self._generate_summary(
                material_analysis, carbon_analysis, improvement_potential, budget_status
            )
        }
    
    def _evaluate_climate_fit(self, materials: List[str], 
                             quantities: List[float], climate: str) -> Dict:
        """Evalúa adecuación climática del diseño."""
        strategy = self.climate_strategies.get(climate, self.climate_strategies['temperate'])
        
        # Calcular masa térmica aproximada basada en materiales
        total_thermal_mass = 0.0
        total_volume = sum(quantities)
        
        thermal_mass_materials = ['rammed_earth', 'clay_brick', 'low_carbon_concrete']
        for i, material in enumerate(materials):
            if material in thermal_mass_materials:
                # Materiales con alta masa térmica
                thermal_mass = 800 * quantities[i]
                total_thermal_mass += thermal_mass
            elif material in ['wood', 'recycled_steel']:
                # Materiales con masa térmica media
                thermal_mass = 300 * quantities[i]
                total_thermal_mass += thermal_mass
        
        thermal_mass_index = total_thermal_mass / (total_volume * 500) if total_volume > 0 else 0.0
        
        # Evaluar adecuación climática
        fit_score = 70.0  # Puntuación base
        issues = []
        strengths = []
        
        # Evaluar según estrategia climática
        if climate == 'hot':
            if thermal_mass_index >= 0.7:
                strengths.append("Alta masa térmica ideal para clima cálido")
                fit_score += 15.0
            else:
                issues.append("Masa térmica insuficiente para clima cálido")
                fit_score -= 10.0
                
        elif climate == 'cold':
            if thermal_mass_index <= 0.5:
                strengths.append("Masa térmica adecuada para clima frío")
                fit_score += 10.0
            else:
                issues.append("Masa térmica excesiva para clima frío")
                fit_score -= 5.0
        
        # Verificar materiales recomendados para el clima
        recommended_materials = strategy['materials_recommended']
        used_recommended = [mat for mat in materials if mat in recommended_materials]
        if used_recommended:
            strengths.append(f"Materiales apropiados para clima {climate}: {', '.join(used_recommended)}")
            fit_score += len(used_recommended) * 5.0
        
        fit_score = max(0.0, min(100.0, fit_score))
        
        return {
            'climate': climate,
            'thermal_mass_index': thermal_mass_index,
            'overall_score': fit_score,
            'recommended_strategy': strategy,
            'issues': issues,
            'strengths': strengths
        }
    
    def _calculate_costs(self, materials: List[str], quantities: List[float]) -> Dict:
        """Calcula costos totales basados en la base de datos de materiales."""
        total_cost = 0.0
        cost_breakdown = {}
        
        for i, material in enumerate(materials):
            material_info = self.material_analyzer.get_material_info(material)
            if material_info:
                material_cost = material_info['cost_usd_m3'] * quantities[i]
                total_cost += material_cost
                cost_breakdown[material] = {
                    'cost_usd': material_cost,
                    'quantity_m3': quantities[i],
                    'unit_cost': material_info['cost_usd_m3']
                }
            else:
                # Costo estimado para materiales no encontrados
                estimated_cost = 500.0 * quantities[i]
                total_cost += estimated_cost
                cost_breakdown[material] = {
                    'cost_usd': estimated_cost,
                    'quantity_m3': quantities[i],
                    'unit_cost': 500.0,
                    'warning': 'Costo estimado - material no encontrado'
                }
        
        return {
            'total_cost': total_cost,
            'cost_breakdown': cost_breakdown,
            'cost_per_m3_avg': total_cost / sum(quantities) if sum(quantities) > 0 else 0.0
        }
    
    def _check_budget(self, total_cost: float, budget_limit: Optional[float]) -> Dict:
        """Verifica el cumplimiento del presupuesto."""
        if budget_limit is None:
            return {
                'within_budget': True,
                'budget_utilization': 0.0,
                'message': 'Sin límite de presupuesto especificado'
            }
        
        within_budget = total_cost <= budget_limit
        utilization = (total_cost / budget_limit * 100) if budget_limit > 0 else 0.0
        
        if within_budget:
            message = f"Dentro del presupuesto ({utilization:.1f}% utilizado)"
        else:
            message = f"Excede el presupuesto por ${total_cost - budget_limit:.0f}"
        
        return {
            'within_budget': within_budget,
            'budget_utilization': utilization,
            'message': message
        }
    
    def _generate_recommendations(self, mat_analysis, carbon_analysis, 
                                 climate_fit, cost_analysis, climate, budget) -> List[Dict]:
        """Genera recomendaciones priorizadas basadas en principios Bauhaus."""
        recommendations = []
        priority = 1
        
        # ALTA PRIORIDAD: Cumplimiento Bauhaus
        if not mat_analysis['bauhaus_compliant']:
            recommendations.append({
                'priority': priority,
                'type': 'bauhaus',
                'title': 'Simplificar Paleta de Materiales',
                'description': f"Reducir de {mat_analysis['unique_materials_count']} a 3 materiales principales",
                'impact': 'Mejora la claridad y reduce la complejidad',
                'action': 'Combinar materiales similares o eliminar secundarios',
                'estimated_improvement': '15-25% en score circular'
            })
            priority += 1
        
        # ALTA PRIORIDAD: Circularidad baja
        if mat_analysis['circular_score'] < 70:
            recommendations.append({
                'priority': priority,
                'type': 'circularity',
                'title': 'Mejorar Circularidad de Materiales',
                'description': f"Actual: {mat_analysis['circular_score']:.1f}%. Objetivo: >70%",
                'impact': f"Podría mejorar recuperación en {(70 - mat_analysis['circular_score']):.0f}%",
                'action': 'Reemplazar con madera, acero reciclado o bambú',
                'estimated_improvement': f"{(70 - mat_analysis['circular_score']):.0f}% en circularidad"
            })
            priority += 1
        
        # MEDIA PRIORIDAD: Carbono
        if carbon_analysis['carbon_savings_percent'] < 30:
            recommendations.append({
                'priority': priority,
                'type': 'carbon',
                'title': 'Reducir Huella de Carbono',
                'description': f"Ahorros actuales: {carbon_analysis['carbon_savings_percent']:.1f}%",
                'impact': f"Objetivo: >30% de ahorro",
                'action': 'Considerar bambú, tierra apisonada o materiales reciclados',
                'estimated_improvement': f"{(30 - carbon_analysis['carbon_savings_percent']):.0f}% en ahorro de carbono"
            })
            priority += 1
        
        # MEDIA PRIORIDAD: Clima
        if climate_fit['overall_score'] < 70:
            recommendations.append({
                'priority': priority,
                'type': 'climate',
                'title': 'Mejorar Desempeño Climático',
                'description': f"Puntuación: {climate_fit['overall_score']}/100 para clima {climate}",
                'impact': 'Mejor confort térmico y eficiencia energética',
                'action': '; '.join(climate_fit['issues']) if climate_fit['issues'] else 'Ajustar masa térmica',
                'estimated_improvement': f"{(70 - climate_fit['overall_score']):.0f}% en adecuación climática"
            })
            priority += 1
        
        # BAJA PRIORIDAD: Costo
        if budget and not cost_analysis.get('within_budget', True):
            recommendations.append({
                'priority': priority,
                'type': 'cost',
                'title': 'Optimizar Costos',
                'description': f"Presupuesto excedido por ${cost_analysis.get('over_budget', 0):.0f}",
                'impact': 'Cumplir restricciones presupuestarias',
                'action': 'Considerar alternativas más económicas como tierra apisonada',
                'estimated_improvement': 'Reducción de 10-30% en costos'
            })
        
        # ARREGLADO: Recomendación para materiales desconocidos
        if mat_analysis['materials_not_found']:
            recommendations.append({
                'priority': priority,
                'type': 'material_selection',
                'title': 'Materiales Desconocidos',
                'description': f"Materiales no encontrados en la base de datos: {', '.join(mat_analysis['materials_not_found'])}",
                'impact': 'Puede afectar la precisión del análisis',
                'action': 'Verificar nombres o considerar alternativas conocidas',
                'estimated_improvement': 'Mejor precisión en el análisis'
            })
        
        return recommendations
    
    def _calculate_improvement_potential(self, mat_analysis, carbon_analysis) -> float:
        """Calcula potencial de mejora general (0-100%)."""
        circular_potential = 100 - mat_analysis['circular_score']
        carbon_potential = 100 - carbon_analysis['carbon_savings_percent']
        # Ponderar: circularidad 60%, carbono 40%
        weighted_potential = (circular_potential * 0.6) + (carbon_potential * 0.4)
        return min(100.0, max(0.0, weighted_potential))
    
    def _generate_optimized_alternative(self, current_materials, quantities, 
                                       climate, budget) -> Dict:
        """Genera una alternativa optimizada basada en principios Bauhaus."""
        # Obtener estrategia climática
        strategy = self.climate_strategies.get(climate, self.climate_strategies['temperate'])
        recommended_materials = strategy['materials_recommended']
        
        # Seleccionar hasta 3 materiales de los recomendados
        optimized_materials = recommended_materials[:3]
        
        # Distribuir cantidades equitativamente
        total_quantity = sum(quantities)
        optimized_quantities = [total_quantity / len(optimized_materials)] * len(optimized_materials)
        
        # Calcular métricas de la alternativa optimizada
        opt_mat_analysis = self.material_analyzer.analyze_materials(optimized_materials)
        opt_carbon = self.carbon_calculator.calculate_carbon_footprint(
            optimized_materials, optimized_quantities
        )
        opt_cost = self._calculate_costs(optimized_materials, optimized_quantities)
        
        # Comparar con diseño actual
        current_mat_analysis = self.material_analyzer.analyze_materials(current_materials)
        current_carbon = self.carbon_calculator.calculate_carbon_footprint(
            current_materials, quantities
        )
        
        circular_improvement = opt_mat_analysis['circular_score'] - current_mat_analysis['circular_score']
        carbon_improvement = current_carbon['total_carbon'] - opt_carbon['total_carbon']
        carbon_improvement_percent = (carbon_improvement / current_carbon['total_carbon'] * 100) if current_carbon['total_carbon'] > 0 else 0.0
        
        return {
            'materials': optimized_materials,
            'quantities_m3': optimized_quantities,
            'circularity_score': opt_mat_analysis['circular_score'],
            'carbon_footprint_kg_co2': opt_carbon['total_carbon'],
            'carbon_savings_percent': opt_carbon['carbon_savings_percent'],
            'total_cost_usd': opt_cost['total_cost'],
            'bauhaus_compliant': opt_mat_analysis['bauhaus_compliant'],
            'improvements': {
                'circularity_improvement': circular_improvement,
                'carbon_reduction_kg_co2': carbon_improvement,
                'carbon_reduction_percent': carbon_improvement_percent,
                'cost_difference_usd': opt_cost['total_cost'] - self._calculate_costs(current_materials, quantities)['total_cost']
            },
            'rationale': f"Seleccionados los 3 materiales más circulares optimizados para clima {climate}",
            'climate_strategy': strategy['description']
        }
    
    def _generate_summary(self, mat_analysis, carbon_analysis, 
                         improvement_potential, budget_status) -> str:
        """Genera resumen ejecutivo del análisis."""
        summary_parts = []
        
        # Evaluación general
        if mat_analysis['circular_score'] >= 80 and carbon_analysis['carbon_savings_percent'] >= 40:
            summary_parts.append("🏆 DISEÑO EXCELENTE: Alta circularidad y fuerte desempeño de carbono.")
        elif mat_analysis['circular_score'] >= 60 or carbon_analysis['carbon_savings_percent'] >= 25:
            summary_parts.append("✅ DISEÑO BUENO: Enfoque circular sólido con espacio para optimización.")
        else:
            summary_parts.append("⚠️ NECESITA MEJORA: Potencial significativo para mejor circularidad.")
        
        # Cumplimiento Bauhaus
        if mat_analysis['bauhaus_compliant']:
            summary_parts.append(f"Sigue el principio Bauhaus con {mat_analysis['unique_materials_count']} materiales.")
        else:
            summary_parts.append(f"Excede el límite Bauhaus: {mat_analysis['unique_materials_count']} materiales (recomendado ≤3).")
        
        # Potencial de mejora
        if improvement_potential > 30:
            summary_parts.append(f"Alto potencial de mejora: {improvement_potential:.0f}%.")
        elif improvement_potential > 15:
            summary_parts.append(f"Potencial de mejora moderado: {improvement_potential:.0f}%.")
        else:
            summary_parts.append(f"Cerca del óptimo: {improvement_potential:.0f}% de potencial de mejora.")
        
        # Presupuesto
        if not budget_status['within_budget']:
            summary_parts.append(f"⚠️ Presupuesto excedido.")
        
        return " ".join(summary_parts)

    def quick_assessment(self, materials: List[str], quantities: List[float]) -> Dict:
        """
        Evaluación rápida sin optimización completa.
        
        Args:
            materials: Lista de materiales
            quantities: Lista de cantidades
        
        Returns:
            dict: Evaluación básica con score general
        """
        mat_analysis = self.material_analyzer.analyze_materials(materials)
        carbon_analysis = self.carbon_calculator.calculate_carbon_footprint(materials, quantities)
        
        # Calcular score general (0-100)
        circular_weight = 0.4
        carbon_weight = 0.4
        bauhaus_weight = 0.2
        
        bauhaus_score = 100 if mat_analysis['bauhaus_compliant'] else 60
        overall_score = (
            mat_analysis['circular_score'] * circular_weight +
            carbon_analysis['carbon_savings_percent'] * carbon_weight +
            bauhaus_score * bauhaus_weight
        )
        
        return {
            'overall_score': overall_score,
            'circularity_score': mat_analysis['circular_score'],
            'carbon_savings_percent': carbon_analysis['carbon_savings_percent'],
            'bauhaus_compliant': mat_analysis['bauhaus_compliant'],
            'performance_level': 'Alto' if overall_score >= 70 else 'Medio' if overall_score >= 50 else 'Bajo'
        }