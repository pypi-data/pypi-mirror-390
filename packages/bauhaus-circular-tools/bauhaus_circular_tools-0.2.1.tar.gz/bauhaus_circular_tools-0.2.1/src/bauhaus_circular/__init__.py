"""
Bauhaus Circular: Herramientas de diseño circular para arquitectura

Transforma principios Bauhaus para el siglo XXI:
- "Forma sigue función" → "Forma sigue flujos"
- Verdad material → Transparencia de ciclo de vida
- Unidad arte-técnica → Unidad diseño-impacto ambiental

Autora: Mary Magali Villca Cruz
Email: arqmaryvillca@gmail.com
"""

__version__ = "0.2.0"
__author__ = "Mary Magali Villca Cruz"
__email__ = "arqmaryvillca@gmail.com"

from .material_analyzer import MaterialAnalyzer, MaterialCategory
from .carbon_calculator import CarbonCalculator
from .design_optimizer import DesignOptimizer
from .climate_analyzer import ClimateAnalyzer

def quick_analysis(materials, quantities, climate='temperate'):
    """
    Análisis rápido completo en una función.
    
    Args:
        materials (list): Lista de materiales ['wood', 'glass', 'steel']
        quantities (list): Lista de cantidades en m³ [45, 12, 28]
        climate (str): Zona climática ('hot', 'temperate', 'cold')
    
    Returns:
        dict: Resultados completos del análisis
    
    Example:
        >>> from bauhaus_circular import quick_analysis
        >>> result = quick_analysis(['wood', 'glass'], [45, 12], 'temperate')
        >>> print(f"Circular Score: {result['current_design']['circularity_score']}%")
    """
    analyzer = MaterialAnalyzer()
    calculator = CarbonCalculator()  # CORREGIDO: Sin parámetro
    optimizer = DesignOptimizer(analyzer, calculator)
    
    return optimizer.optimize_design(materials, quantities, climate)

__all__ = [
    'MaterialAnalyzer',
    'MaterialCategory',
    'CarbonCalculator',
    'DesignOptimizer',
    'ClimateAnalyzer',
    'quick_analysis',
    '__version__',
    '__author__',
    '__email__'
]