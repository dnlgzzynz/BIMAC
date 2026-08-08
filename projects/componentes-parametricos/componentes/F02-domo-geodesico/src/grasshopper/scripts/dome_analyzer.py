#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analizador de Domos - F02 Domo Geodesico Parametrico

Analiza propiedades geometricas, estructurales y de costos
de domos geodesicos.

Autor: BIMAC
Version: 1.0.0
"""

import math
from collections import namedtuple

# Estructuras de datos
DomeStatistics = namedtuple('DomeStatistics', [
    'radius', 'frequency', 'truncation',
    'vertex_count', 'edge_count', 'face_count',
    'surface_area', 'volume', 'floor_area',
    'height', 'base_perimeter'
])

StructuralAnalysis = namedtuple('StructuralAnalysis', [
    'total_strut_weight', 'total_node_weight', 'total_panel_weight',
    'total_weight', 'weight_per_m2', 'max_strut_force',
    'critical_slenderness', 'capacity_ratio'
])

CostEstimate = namedtuple('CostEstimate', [
    'structure_cost', 'panel_cost', 'node_cost',
    'fabrication_cost', 'erection_cost', 'total_cost', 'cost_per_m2'
])


class GeometricAnalyzer:
    """Analiza propiedades geometricas del domo."""

    def __init__(self, geodesic_mesh):
        """
        Args:
            geodesic_mesh: GeodesicMesh del generador
        """
        self.mesh = geodesic_mesh

    def calculate_surface_area(self):
        """Calcula area superficial total."""
        return sum(face.area for face in self.mesh.faces)

    def calculate_volume(self):
        """
        Calcula volumen aproximado del domo.

        Usa formula de casquete esferico.
        """
        # Encontrar altura del domo
        z_coords = [v.point.Z for v in self.mesh.vertices]
        h = max(z_coords) - min(z_coords)

        r = self.mesh.radius

        # Volumen de casquete esferico
        # V = (pi * h^2 / 3) * (3r - h)
        volume = (math.pi * h * h / 3.0) * (3 * r - h)

        return volume

    def calculate_floor_area(self):
        """Calcula area de piso (proyeccion en planta)."""
        # Encontrar vertices de base
        base_vertices = [v for v in self.mesh.vertices if v.type == 'base']

        if not base_vertices:
            return math.pi * self.mesh.radius ** 2

        # Calcular area del poligono de base
        n = len(base_vertices)
        if n < 3:
            return 0.0

        # Ordenar por angulo
        center_x = sum(v.point.X for v in base_vertices) / n
        center_y = sum(v.point.Y for v in base_vertices) / n

        base_vertices.sort(key=lambda v: math.atan2(
            v.point.Y - center_y, v.point.X - center_x
        ))

        # Formula de shoelace
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += base_vertices[i].point.X * base_vertices[j].point.Y
            area -= base_vertices[j].point.X * base_vertices[i].point.Y

        return abs(area) / 2.0

    def calculate_height(self):
        """Calcula altura del domo."""
        z_coords = [v.point.Z for v in self.mesh.vertices]
        return max(z_coords) - min(z_coords)

    def calculate_base_perimeter(self):
        """Calcula perimetro de la base."""
        base_vertices = [v for v in self.mesh.vertices if v.type == 'base']

        if len(base_vertices) < 2:
            return 2 * math.pi * self.mesh.radius

        # Ordenar por angulo
        n = len(base_vertices)
        center_x = sum(v.point.X for v in base_vertices) / n
        center_y = sum(v.point.Y for v in base_vertices) / n

        base_vertices.sort(key=lambda v: math.atan2(
            v.point.Y - center_y, v.point.X - center_x
        ))

        # Sumar distancias
        perimeter = 0.0
        for i in range(n):
            j = (i + 1) % n
            perimeter += base_vertices[i].point.DistanceTo(
                base_vertices[j].point
            )

        return perimeter

    def get_statistics(self):
        """Obtiene estadisticas completas."""
        return DomeStatistics(
            radius=self.mesh.radius,
            frequency=self.mesh.frequency,
            truncation=0.5,  # TODO: obtener de mesh
            vertex_count=len(self.mesh.vertices),
            edge_count=len(self.mesh.edges),
            face_count=len(self.mesh.faces),
            surface_area=self.calculate_surface_area(),
            volume=self.calculate_volume(),
            floor_area=self.calculate_floor_area(),
            height=self.calculate_height(),
            base_perimeter=self.calculate_base_perimeter()
        )


class StructuralAnalyzer:
    """Analiza propiedades estructurales del domo."""

    # Constantes
    STEEL_DENSITY = 7850  # kg/m3

    def __init__(self, geodesic_mesh, strut_profile, node_type='spherical'):
        """
        Args:
            geodesic_mesh: GeodesicMesh
            strut_profile: dict con datos del perfil
            node_type: Tipo de nodo
        """
        self.mesh = geodesic_mesh
        self.profile = strut_profile
        self.node_type = node_type

    def calculate_strut_weight(self):
        """Calcula peso total de barras."""
        total_length = sum(edge.length for edge in self.mesh.edges)
        weight_per_m = self.profile.get('weight', 4.24)  # kg/m
        return total_length * weight_per_m

    def calculate_node_weight(self):
        """Calcula peso total de nodos."""
        node_count = len(self.mesh.vertices)

        # Peso promedio por nodo segun tipo
        weights = {
            'spherical': 2.5,
            'plate': 1.8,
            'flattened': 0.5,
            'bolt_through': 0.3
        }

        weight_per_node = weights.get(self.node_type, 2.0)
        return node_count * weight_per_node

    def calculate_panel_weight(self, material='glass_single'):
        """Calcula peso de paneles."""
        surface_area = sum(face.area for face in self.mesh.faces)

        # Peso por m2 segun material
        weights = {
            'glass_single': 20.0,  # kg/m2
            'glass_double': 35.0,
            'polycarbonate': 8.0,
            'etfe': 1.5,
            'aluminum': 10.0
        }

        weight_per_m2 = weights.get(material, 20.0)
        return surface_area * weight_per_m2

    def calculate_loads(self, wind_speed=100, snow_load=0.5):
        """
        Calcula cargas de diseno.

        Args:
            wind_speed: Velocidad de viento en km/h
            snow_load: Carga de nieve en kN/m2

        Returns:
            dict: Cargas de diseno
        """
        surface_area = sum(face.area for face in self.mesh.faces)

        # Presion de viento (simplificada)
        # q = 0.5 * rho * v^2, con factor de forma 0.5 para domo
        v_ms = wind_speed / 3.6
        q_wind = 0.5 * 1.225 * v_ms * v_ms * 0.5 / 1000  # kN/m2

        # Carga de nieve (factor de forma 0.7 para domo)
        q_snow = snow_load * 0.7

        # Peso propio
        total_weight = (self.calculate_strut_weight() +
                        self.calculate_node_weight() +
                        self.calculate_panel_weight())
        q_dead = total_weight * 9.81 / 1000 / surface_area  # kN/m2

        return {
            'dead_load': q_dead,
            'wind_load': q_wind,
            'snow_load': q_snow,
            'total_factored': 1.2 * q_dead + 1.6 * q_snow + 0.5 * q_wind
        }

    def estimate_strut_forces(self, total_load_kN_m2):
        """
        Estima fuerzas en barras.

        Simplificacion: fuerza uniforme en todas las barras.

        Args:
            total_load_kN_m2: Carga total por m2

        Returns:
            dict: Fuerzas estimadas
        """
        surface_area = sum(face.area for face in self.mesh.faces)
        total_load = total_load_kN_m2 * surface_area

        # Distribuir entre barras
        edge_count = len(self.mesh.edges)
        avg_force = total_load / edge_count

        # Factor para barras mas cargadas
        max_factor = 1.5

        return {
            'average_force_kN': avg_force,
            'max_force_kN': avg_force * max_factor,
            'total_load_kN': total_load
        }

    def check_slenderness(self):
        """Verifica esbeltez de las barras."""
        # Radio de giro
        I = self.profile.get('I', 189000)  # mm4
        A = self.profile.get('area', 540)  # mm2
        r = math.sqrt(I / A) / 1000  # m

        # Longitud maxima
        max_length = max(edge.length for edge in self.mesh.edges)

        slenderness = max_length / r

        return {
            'max_length': max_length,
            'radius_of_gyration': r * 1000,  # mm
            'slenderness': slenderness,
            'limit': 200,
            'status': 'OK' if slenderness < 200 else 'NG'
        }

    def get_analysis(self, panel_material='glass_single'):
        """Obtiene analisis estructural completo."""
        strut_weight = self.calculate_strut_weight()
        node_weight = self.calculate_node_weight()
        panel_weight = self.calculate_panel_weight(panel_material)
        total_weight = strut_weight + node_weight + panel_weight

        surface_area = sum(face.area for face in self.mesh.faces)

        loads = self.calculate_loads()
        forces = self.estimate_strut_forces(loads['total_factored'])
        slenderness = self.check_slenderness()

        return StructuralAnalysis(
            total_strut_weight=strut_weight,
            total_node_weight=node_weight,
            total_panel_weight=panel_weight,
            total_weight=total_weight,
            weight_per_m2=total_weight / surface_area,
            max_strut_force=forces['max_force_kN'],
            critical_slenderness=slenderness['slenderness'],
            capacity_ratio=0.0  # TODO: calcular
        )


class CostEstimator:
    """Estima costos del domo."""

    # Costos unitarios (USD)
    COSTS = {
        'steel_per_kg': 2.50,
        'node_spherical': 85.00,
        'node_plate': 45.00,
        'node_simple': 25.00,
        'panel_glass': 180.00,  # por m2
        'panel_polycarbonate': 85.00,
        'panel_etfe': 250.00,
        'fabrication_per_kg': 1.50,
        'galvanizing_per_kg': 0.85,
        'erection_per_m2': 45.00,
        'crane_daily': 1200.00,
        'engineering_factor': 0.08
    }

    def __init__(self, geodesic_mesh, strut_profile):
        """
        Args:
            geodesic_mesh: GeodesicMesh
            strut_profile: dict con datos del perfil
        """
        self.mesh = geodesic_mesh
        self.profile = strut_profile

    def estimate_structure_cost(self):
        """Estima costo de estructura."""
        # Peso de barras
        total_length = sum(edge.length for edge in self.mesh.edges)
        weight_per_m = self.profile.get('weight', 4.24)
        strut_weight = total_length * weight_per_m

        # Costo de material
        material_cost = strut_weight * self.COSTS['steel_per_kg']

        # Costo de fabricacion
        fab_cost = strut_weight * self.COSTS['fabrication_per_kg']

        # Costo de galvanizado
        galv_cost = strut_weight * self.COSTS['galvanizing_per_kg']

        return material_cost + fab_cost + galv_cost

    def estimate_node_cost(self, node_type='spherical'):
        """Estima costo de nodos."""
        node_count = len(self.mesh.vertices)

        costs = {
            'spherical': self.COSTS['node_spherical'],
            'plate': self.COSTS['node_plate'],
            'simple': self.COSTS['node_simple']
        }

        unit_cost = costs.get(node_type, self.COSTS['node_spherical'])
        return node_count * unit_cost

    def estimate_panel_cost(self, material='glass'):
        """Estima costo de paneles."""
        surface_area = sum(face.area for face in self.mesh.faces)

        costs = {
            'glass': self.COSTS['panel_glass'],
            'polycarbonate': self.COSTS['panel_polycarbonate'],
            'etfe': self.COSTS['panel_etfe']
        }

        cost_per_m2 = costs.get(material, self.COSTS['panel_glass'])
        return surface_area * cost_per_m2

    def estimate_erection_cost(self):
        """Estima costo de montaje."""
        surface_area = sum(face.area for face in self.mesh.faces)

        # Costo base por m2
        base_cost = surface_area * self.COSTS['erection_per_m2']

        # Dias de grua (estimacion: 20m2/dia)
        crane_days = math.ceil(surface_area / 20)
        crane_cost = crane_days * self.COSTS['crane_daily']

        return base_cost + crane_cost

    def get_estimate(self, node_type='spherical', panel_material='glass'):
        """Obtiene estimacion completa."""
        structure = self.estimate_structure_cost()
        nodes = self.estimate_node_cost(node_type)
        panels = self.estimate_panel_cost(panel_material)
        erection = self.estimate_erection_cost()

        subtotal = structure + nodes + panels + erection
        engineering = subtotal * self.COSTS['engineering_factor']
        total = subtotal + engineering

        surface_area = sum(face.area for face in self.mesh.faces)

        return CostEstimate(
            structure_cost=structure,
            panel_cost=panels,
            node_cost=nodes,
            fabrication_cost=0,  # Incluido en structure
            erection_cost=erection,
            total_cost=total,
            cost_per_m2=total / surface_area
        )


class WindLoadCalculator:
    """Calcula cargas de viento segun ASCE 7."""

    def __init__(self, geodesic_mesh):
        """
        Args:
            geodesic_mesh: GeodesicMesh
        """
        self.mesh = geodesic_mesh

    def calculate_velocity_pressure(self, basic_wind_speed, exposure='C',
                                     height=None):
        """
        Calcula presion de velocidad.

        Args:
            basic_wind_speed: Velocidad basica en m/s
            exposure: Categoria de exposicion (B, C, D)
            height: Altura sobre el terreno

        Returns:
            float: Presion de velocidad en kN/m2
        """
        if height is None:
            height = max(v.point.Z for v in self.mesh.vertices)

        # Coeficientes de exposicion
        exposure_coeffs = {
            'B': {'alpha': 7.0, 'zg': 365.76},
            'C': {'alpha': 9.5, 'zg': 274.32},
            'D': {'alpha': 11.5, 'zg': 213.36}
        }

        exp = exposure_coeffs.get(exposure, exposure_coeffs['C'])
        alpha = exp['alpha']
        zg = exp['zg']

        # Kz
        z = max(height, 4.6)  # Minimo 4.6m
        Kz = 2.01 * (z / zg) ** (2.0 / alpha)

        # qz = 0.613 * Kz * V^2 (Pa)
        qz = 0.613 * Kz * basic_wind_speed ** 2 / 1000  # kN/m2

        return qz

    def calculate_pressure_coefficients(self):
        """
        Calcula coeficientes de presion para domo.

        Returns:
            dict: Coeficientes por zona
        """
        # Simplificacion para domos
        # ASCE 7 Figura 27.3-2

        return {
            'windward': 0.8,
            'side': -0.7,
            'leeward': -0.5,
            'roof_negative': -1.0,
            'internal': 0.18  # Para edificios cerrados
        }

    def calculate_design_pressures(self, basic_wind_speed, exposure='C'):
        """
        Calcula presiones de diseno.

        Args:
            basic_wind_speed: Velocidad basica m/s
            exposure: Categoria de exposicion

        Returns:
            dict: Presiones de diseno
        """
        qz = self.calculate_velocity_pressure(basic_wind_speed, exposure)
        Cp = self.calculate_pressure_coefficients()

        # Factor de direccionalidad Kd = 0.85 para estructuras
        Kd = 0.85

        pressures = {}
        for zone, cp in Cp.items():
            if zone != 'internal':
                p = qz * Kd * cp
                pressures[zone] = p

        return pressures


class ReportGenerator:
    """Genera reportes del analisis del domo."""

    def __init__(self, geodesic_mesh, strut_profile):
        """
        Args:
            geodesic_mesh: GeodesicMesh
            strut_profile: dict con datos del perfil
        """
        self.mesh = geodesic_mesh
        self.profile = strut_profile

        self.geo_analyzer = GeometricAnalyzer(geodesic_mesh)
        self.struct_analyzer = StructuralAnalyzer(geodesic_mesh, strut_profile)
        self.cost_estimator = CostEstimator(geodesic_mesh, strut_profile)

    def generate_summary_report(self, node_type='spherical',
                                 panel_material='glass'):
        """
        Genera reporte resumido.

        Returns:
            str: Reporte formateado
        """
        geo = self.geo_analyzer.get_statistics()
        struct = self.struct_analyzer.get_analysis(panel_material)
        cost = self.cost_estimator.get_estimate(node_type, panel_material)

        lines = []
        lines.append("=" * 60)
        lines.append("REPORTE DE DOMO GEODESICO")
        lines.append("=" * 60)
        lines.append("")

        lines.append("GEOMETRIA")
        lines.append("-" * 40)
        lines.append(f"  Radio:                {geo.radius:.2f} m")
        lines.append(f"  Frecuencia:           {geo.frequency}V")
        lines.append(f"  Altura:               {geo.height:.2f} m")
        lines.append(f"  Vertices:             {geo.vertex_count}")
        lines.append(f"  Barras:               {geo.edge_count}")
        lines.append(f"  Paneles:              {geo.face_count}")
        lines.append(f"  Area superficial:     {geo.surface_area:.2f} m2")
        lines.append(f"  Area de piso:         {geo.floor_area:.2f} m2")
        lines.append(f"  Volumen:              {geo.volume:.2f} m3")
        lines.append(f"  Perimetro base:       {geo.base_perimeter:.2f} m")
        lines.append("")

        lines.append("ESTRUCTURA")
        lines.append("-" * 40)
        lines.append(f"  Peso barras:          {struct.total_strut_weight:.0f} kg")
        lines.append(f"  Peso nodos:           {struct.total_node_weight:.0f} kg")
        lines.append(f"  Peso paneles:         {struct.total_panel_weight:.0f} kg")
        lines.append(f"  Peso total:           {struct.total_weight:.0f} kg")
        lines.append(f"  Peso por m2:          {struct.weight_per_m2:.1f} kg/m2")
        lines.append(f"  Esbeltez critica:     {struct.critical_slenderness:.0f}")
        lines.append("")

        lines.append("COSTOS (USD)")
        lines.append("-" * 40)
        lines.append(f"  Estructura:           ${cost.structure_cost:,.0f}")
        lines.append(f"  Nodos:                ${cost.node_cost:,.0f}")
        lines.append(f"  Paneles:              ${cost.panel_cost:,.0f}")
        lines.append(f"  Montaje:              ${cost.erection_cost:,.0f}")
        lines.append(f"  Total:                ${cost.total_cost:,.0f}")
        lines.append(f"  Costo por m2:         ${cost.cost_per_m2:.2f}/m2")
        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)


# Ejemplo de uso
if __name__ == "__main__":
    from geodesic_generator import GeodesicDomeGenerator

    # Generar domo
    generator = GeodesicDomeGenerator()
    mesh = generator.generate(radius=15.0, frequency=4, truncation=0.5)

    # Perfil de barras
    profile = {
        'name': 'D60x3',
        'diameter': 60.3,
        'wall': 3.0,
        'area': 540,
        'I': 189000,
        'weight': 4.24
    }

    # Generar reporte
    report_gen = ReportGenerator(mesh, profile)
    report = report_gen.generate_summary_report()
    print(report)
