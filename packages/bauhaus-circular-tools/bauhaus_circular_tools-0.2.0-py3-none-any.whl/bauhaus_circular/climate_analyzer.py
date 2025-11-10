"""
Analizador Climático con Integración Ladybug

Principios Bauhaus aplicados:
- Función basada en datos reales
- Honestidad (datos climáticos certificados)
- Racionalidad científica

Autora: Mary Magali Villca Cruz
Email: arqmaryvillca@gmail.com
"""

from typing import Dict, Optional, Tuple, List
import os
import math

# Intentar importar Ladybug (opcional)
try:
    from ladybug.epw import EPW
    from ladybug.sunpath import Sunpath
    from ladybug.location import Location
    LADYBUG_AVAILABLE = True
except ImportError:
    LADYBUG_AVAILABLE = False


class ClimateAnalyzer:
    """
    Analizador climático con soporte opcional para Ladybug Tools.
    """
    
    def __init__(self, epw_file_path: Optional[str] = None, climate_zone: str = 'temperate'):
        self.epw_file_path = epw_file_path
        self.epw_data = None
        self.location = None
        self.use_simplified = True
        self.climate_zone = climate_zone
        
        if LADYBUG_AVAILABLE and epw_file_path and os.path.exists(epw_file_path):
            self._load_epw_data()
    
    def _load_epw_data(self):
        """Carga datos EPW usando Ladybug."""
        try:
            self.epw_data = EPW(self.epw_file_path)
            self.location = self.epw_data.location
            self.use_simplified = False
            print(f"✅ Loaded climate data: {self.location.city}")
        except Exception as e:
            print(f"⚠️ Could not load EPW: {e}")
            self.use_simplified = True
    
    def get_climate_zone(self, latitude: Optional[float] = None) -> str:
        """Determina zona climática, opcionalmente usando latitud."""
        if latitude is not None:
            if abs(latitude) < 23.5:
                return 'hot'
            elif abs(latitude) < 35:
                return 'arid' 
            elif abs(latitude) < 60:
                return 'temperate'
            else:
                return 'cold'
        
        if not self.use_simplified and self.epw_data:
            temps = self.epw_data.dry_bulb_temperature.values
            avg_temp = sum(temps) / len(temps)
            
            if avg_temp >= 25:
                return 'hot'
            elif avg_temp >= 15:
                return 'temperate'
            else:
                return 'cold'
        
        return self.climate_zone
    
    def get_solar_radiation_annual(self) -> Dict[str, float]:
        """Calcula radiación solar anual."""
        if not self.use_simplified and self.epw_data:
            direct = sum(self.epw_data.direct_normal_radiation.values) / 1000
            diffuse = sum(self.epw_data.diffuse_horizontal_radiation.values) / 1000
            global_rad = sum(self.epw_data.global_horizontal_radiation.values) / 1000
            
            return {
                'direct_normal_kwh_m2': direct,
                'diffuse_horizontal_kwh_m2': diffuse,
                'global_horizontal_kwh_m2': global_rad,
                'source': 'ladybug_epw',
                'confidence': 'high'
            }
        else:
            climate = self.get_climate_zone()
            estimates = {
                'hot': {'direct': 2200, 'diffuse': 800, 'global': 2400},
                'temperate': {'direct': 1600, 'diffuse': 700, 'global': 1800},
                'cold': {'direct': 1200, 'diffuse': 600, 'global': 1400}
            }
            est = estimates.get(climate, estimates['temperate'])
            
            return {
                'direct_normal_kwh_m2': est['direct'],
                'diffuse_horizontal_kwh_m2': est['diffuse'],
                'global_horizontal_kwh_m2': est['global'],
                'source': 'simplified_estimate',
                'confidence': 'medium'
            }
    
    def get_heating_cooling_degree_days(self) -> Dict[str, float]:
        """Calcula grados-día de calefacción/refrigeración."""
        if not self.use_simplified and self.epw_data:
            temps = self.epw_data.dry_bulb_temperature.values
            base_temp = 18
            
            hdd = sum(max(0, base_temp - t) for t in temps) / 24
            cdd = sum(max(0, t - base_temp) for t in temps) / 24
            
            return {
                'heating_degree_days': hdd,
                'cooling_degree_days': cdd,
                'balance_point_c': base_temp,
                'source': 'ladybug_epw',
                'confidence': 'high'
            }
        else:
            climate = self.get_climate_zone()
            estimates = {
                'hot': {'hdd': 200, 'cdd': 3500},
                'temperate': {'hdd': 1500, 'cdd': 800},
                'cold': {'hdd': 4000, 'cdd': 100}
            }
            est = estimates.get(climate, estimates['temperate'])
            
            return {
                'heating_degree_days': est['hdd'],
                'cooling_degree_days': est['cdd'],
                'balance_point_c': 18,
                'source': 'simplified_estimate',
                'confidence': 'medium'
            }

    def estimate_energy_savings(self, area: float) -> Dict[str, float]:
        """
        Estima ahorros energéticos basados en el área.
        """
        climate = self.get_climate_zone()
        
        base_savings = {
            'hot': 45.0,
            'temperate': 50.0,
            'cold': 55.0
        }
        
        savings_per_m2 = base_savings.get(climate, 50.0)
        annual_savings = savings_per_m2 * area
        co2_savings = annual_savings * 0.5

        return {
            'annual_energy_savings_kwh': annual_savings,
            'savings_per_m2': savings_per_m2,
            'area_m2': area,
            'climate_zone': climate,
            'heating_kwh_year': annual_savings * 0.6,
            'cooling_kwh_year': annual_savings * 0.3,
            'lighting_kwh_year': annual_savings * 0.1,
            'total_co2_savings_kg_year': co2_savings
        }

    @staticmethod
    def get_available_climate_zones() -> List[Dict]:
        """Devuelve zonas climáticas disponibles como diccionarios."""
        zones = [
            {
                'zone': 'hot', 
                'description': 'Clima cálido con alta demanda de refrigeración',
                'typical_locations': ['Miami', 'Dubai', 'Singapur'],
                'key_challenge': 'Sobrecarga de refrigeración y ganancia solar excesiva'
            },
            {
                'zone': 'temperate', 
                'description': 'Clima templado con demanda balanceada',
                'typical_locations': ['Nueva York', 'Londres', 'Tokio'],
                'key_challenge': 'Variaciones estacionales y necesidad de sistemas mixtos'
            },
            {
                'zone': 'cold', 
                'description': 'Clima frío con alta demanda de calefacción',
                'typical_locations': ['Moscú', 'Toronto', 'Estocolmo'],
                'key_challenge': 'Pérdida de calor y bajas temperaturas extremas'
            }
        ]
        return zones

    def get_climate_summary(self) -> Dict:
        """Devuelve resumen climático completo."""
        climate_zone = self.get_climate_zone()
        
        # Calcular demandas basadas en la zona climática
        if climate_zone == 'hot':
            heating_demand = 'Baja'
            cooling_demand = 'Alta'
            solar_potential = 'Muy Alta'
        elif climate_zone == 'temperate':
            heating_demand = 'Media'
            cooling_demand = 'Media'
            solar_potential = 'Alta'
        else:  # cold
            heating_demand = 'Alta'
            cooling_demand = 'Baja'
            solar_potential = 'Moderada'

        return {
            'climate_zone': climate_zone,
            'solar_radiation': self.get_solar_radiation_annual(),
            'degree_days': self.get_heating_cooling_degree_days(),
            'design_recommendations': self.generate_design_recommendations(),
            'summary': f"Climate analysis for {climate_zone} zone",
            'data_source': 'ladybug_epw' if not self.use_simplified else 'simplified_estimate',
            'temperature_profile': self.get_temperature_profile(),
            'performance_indicators': {
                'energy_efficiency': 'Alta',
                'passive_design_potential': 'Moderado a Alto',
                'comfort_index': 75,
                'sustainability_rating': 'Bueno',
                'heating_demand': heating_demand,
                'cooling_demand': cooling_demand,
                'natural_ventilation_potential': 'Alta',
                'solar_potential': solar_potential
            },
            'bauhaus_principles_applied': [
                'Form follows climate function',
                'Material honesty in environmental performance',
                'Unity of technical and aesthetic solutions'
            ]
        }

    def get_temperature_profile(self) -> Dict[str, any]:
        """Devuelve perfil de temperaturas."""
        climate = self.get_climate_zone()
        
        profiles = {
            'hot': {'max_temp_c': 40.0, 'min_temp_c': 15.0, 'avg_temp_c': 28.0},
            'temperate': {'max_temp_c': 35.0, 'min_temp_c': -5.0, 'avg_temp_c': 15.0},
            'cold': {'max_temp_c': 25.0, 'min_temp_c': -20.0, 'avg_temp_c': 5.0}
        }
        
        profile = profiles.get(climate, profiles['temperate'])
        
        monthly_temperatures = []
        base_temp = profile['avg_temp_c']
        for month in range(12):
            variation = 10 * math.sin(2 * math.pi * month / 12)
            monthly_temperatures.append(round(base_temp + variation, 1))
        
        return {
            'max_temp_c': profile['max_temp_c'],
            'min_temp_c': profile['min_temp_c'],
            'avg_temp_c': profile['avg_temp_c'],
            'monthly_temperatures_c': monthly_temperatures,
            'source': 'simplified_estimate',
            'climate_zone': climate,
            'annual_average_c': profile['avg_temp_c']
        }

    def generate_design_recommendations(self, building_type: str = 'residential') -> Dict:
        """Genera recomendaciones de diseño basadas en clima."""
        climate = self.get_climate_zone()
        
        recommendations = {
            'climate_zone': climate,
            'primary_strategy': '',
            'thermal_mass': '',
            'glazing_recommendation': '',
            'materials_priority': [],
            'insulation_level': '',
            'building_type': building_type,
            'passive_strategies': []
        }
        
        if climate == 'hot':
            recommendations['primary_strategy'] = 'Passive cooling and sun protection'
            recommendations['thermal_mass'] = 'HIGH - Use rammed earth, concrete'
            recommendations['glazing_recommendation'] = 'LOW WWR (15-25%)'
            recommendations['materials_priority'] = ['rammed_earth', 'clay_brick', 'bamboo']
            recommendations['insulation_level'] = 'MODERATE - Focus on roof insulation'
            recommendations['passive_strategies'] = ['Natural ventilation', 'Shading devices', 'Thermal mass']
        elif climate == 'temperate':
            recommendations['primary_strategy'] = 'Balanced heating/cooling'
            recommendations['thermal_mass'] = 'MODERATE - Balanced storage'
            recommendations['glazing_recommendation'] = 'MODERATE WWR (25-35%)'
            recommendations['materials_priority'] = ['wood', 'recycled_steel', 'recycled_insulation']
            recommendations['insulation_level'] = 'HIGH - Comprehensive insulation'
            recommendations['passive_strategies'] = ['Solar gain management', 'Cross ventilation', 'Night purging']
        else:  # cold
            recommendations['primary_strategy'] = 'Passive solar heating and insulation'
            recommendations['thermal_mass'] = 'MODERATE - Solar storage'
            recommendations['glazing_recommendation'] = 'MODERATE-HIGH WWR (30-40%)'
            recommendations['materials_priority'] = ['wood', 'recycled_insulation', 'low_carbon_concrete']
            recommendations['insulation_level'] = 'VERY HIGH - Maximum insulation'
            recommendations['passive_strategies'] = ['Solar orientation', 'Air tightness', 'Thermal storage']
        
        return recommendations