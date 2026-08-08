"""
Cost Calculator - Escalera Helicoidal Parametrica
Calcula costos detallados de material, fabricacion e instalacion.

Inputs:
    spiral_data (SpiralData): Datos de la espiral
    tread_result (TreadResult): Resultado del constructor de peldanos
    railing_data (RailingData): Datos del barandal
    tread_material (str): Material de peldanos
    structure_type (str): Tipo de estructura
    finishing (str): Tipo de acabado
    location_factor (float): Factor de ubicacion (default 1.0)

Outputs:
    total_cost (float): Costo total (MXN)
    cost_breakdown (dict): Desglose por categoria
    budget (dict): Presupuesto detallado
    unit_costs (dict): Costos unitarios
"""

import math
from collections import namedtuple

# Resultado del calculo de costos
CostResult = namedtuple('CostResult', [
    'total_cost', 'breakdown', 'budget_items',
    'unit_costs', 'summary', 'formatted_budget'
])

# Item de presupuesto
BudgetItem = namedtuple('BudgetItem', [
    'category', 'subcategory', 'description',
    'quantity', 'unit', 'unit_cost', 'total_cost'
])


class MaterialCostDatabase:
    """Base de datos de costos de materiales."""

    # Precios en MXN (actualizados 2024)
    STEEL_PRICES = {
        'structural_plate': 28000,    # MXN/ton - Placa estructural
        'hss_tube': 32000,            # MXN/ton - Tubo HSS
        'pipe': 30000,                # MXN/ton - Tubo cedula 40
        'round_bar': 26000,           # MXN/ton - Solera redonda
        'flat_bar': 24000,            # MXN/ton - Solera plana
        'angle': 25000,               # MXN/ton - Angulo
        'stainless_304': 85000,       # MXN/ton - Inoxidable 304
        'stainless_316': 120000,      # MXN/ton - Inoxidable 316
    }

    WOOD_PRICES = {
        'pine': 8500,      # MXN/m3 - Pino tratado
        'oak': 28000,      # MXN/m3 - Encino
        'maple': 32000,    # MXN/m3 - Maple
        'walnut': 45000,   # MXN/m3 - Nogal
        'mahogany': 55000, # MXN/m3 - Caoba
    }

    GLASS_PRICES = {
        'tempered_10': 1800,     # MXN/m2 - Templado 10mm
        'tempered_12': 2200,     # MXN/m2 - Templado 12mm
        'laminated_6_6': 2800,   # MXN/m2 - Laminado 6+6
        'laminated_8_8': 3500,   # MXN/m2 - Laminado 8+8
    }

    CONCRETE_PRICES = {
        'precast': 8500,         # MXN/m3 - Prefabricado
        'cast_in_place': 6500,   # MXN/m3 - Colado en sitio
    }

    FINISHING_PRICES = {
        'primer': 180,           # MXN/m2
        'paint': 280,            # MXN/m2 - Pintura esmalte
        'powder_coat': 450,      # MXN/m2 - Pintura electrostatica
        'galvanize': 15,         # MXN/kg - Galvanizado en caliente
        'anodize': 850,          # MXN/m2 - Anodizado
        'polish': 380,           # MXN/m2 - Pulido
        'antislip': 250,         # MXN/m2 - Tratamiento antiderrapante
        'wood_stain': 320,       # MXN/m2 - Tinte para madera
        'lacquer': 420,          # MXN/m2 - Laca para madera
    }


class LaborCostDatabase:
    """Base de datos de costos de mano de obra."""

    # Precios en MXN
    FABRICATION_RATES = {
        'cutting': 450,          # MXN/hr - Corte
        'welding': 580,          # MXN/hr - Soldadura
        'machining': 750,        # MXN/hr - Maquinado
        'bending': 520,          # MXN/hr - Doblado
        'assembly': 420,         # MXN/hr - Ensamble
        'finishing': 380,        # MXN/hr - Acabado
        'quality_control': 650,  # MXN/hr - Control de calidad
    }

    INSTALLATION_RATES = {
        'helper': 350,           # MXN/jornada
        'installer': 650,        # MXN/jornada
        'welder_field': 850,     # MXN/jornada
        'supervisor': 1200,      # MXN/jornada
    }

    EQUIPMENT_RATES = {
        'crane_10ton': 8500,     # MXN/dia
        'crane_25ton': 15000,    # MXN/dia
        'forklift': 3500,        # MXN/dia
        'welder_portable': 1200, # MXN/dia
        'scaffolding': 180,      # MXN/m2/semana
    }


class SpiralStairCostCalculator:
    """Calculadora de costos para escalera helicoidal."""

    def __init__(self, location_factor=1.0, currency='MXN'):
        """
        Args:
            location_factor: Factor de ajuste por ubicacion
            currency: Moneda (MXN, USD)
        """
        self.location_factor = location_factor
        self.currency = currency
        self.material_db = MaterialCostDatabase()
        self.labor_db = LaborCostDatabase()

    def calculate(self, spiral_data, tread_result=None, railing_data=None,
                  tread_material='steel', structure_type='central_column',
                  finishing='powder_coat'):
        """
        Calcula costo total de la escalera.

        Args:
            spiral_data: Datos de la espiral
            tread_result: Resultado del constructor de peldanos
            railing_data: Datos del barandal
            tread_material: Material de peldanos
            structure_type: Tipo de estructura
            finishing: Tipo de acabado

        Returns:
            CostResult
        """
        budget_items = []
        stats = spiral_data.geometry_stats

        # === 1. MATERIALES ===

        # 1.1 Estructura
        structure_cost = self._calculate_structure_cost(
            stats, structure_type, budget_items
        )

        # 1.2 Peldanos
        tread_cost = self._calculate_tread_cost(
            stats, tread_material, tread_result, budget_items
        )

        # 1.3 Barandales
        railing_cost = self._calculate_railing_cost(
            stats, railing_data, budget_items
        )

        # 1.4 Conexiones y herrajes
        hardware_cost = self._calculate_hardware_cost(
            stats, budget_items
        )

        # === 2. FABRICACION ===

        fabrication_cost = self._calculate_fabrication_cost(
            stats, structure_type, tread_material, budget_items
        )

        # === 3. ACABADOS ===

        finishing_cost = self._calculate_finishing_cost(
            stats, tread_result, railing_data, finishing, budget_items
        )

        # === 4. TRANSPORTE ===

        transport_cost = self._calculate_transport_cost(
            stats, budget_items
        )

        # === 5. INSTALACION ===

        installation_cost = self._calculate_installation_cost(
            stats, structure_type, budget_items
        )

        # === 6. INDIRECTOS ===

        # Subtotal antes de indirectos
        subtotal_direct = (
            structure_cost + tread_cost + railing_cost +
            hardware_cost + fabrication_cost + finishing_cost +
            transport_cost + installation_cost
        )

        # Ingenieria y supervision (8%)
        engineering = subtotal_direct * 0.08
        budget_items.append(BudgetItem(
            category='Indirectos',
            subcategory='Ingenieria',
            description='Diseno, planos y supervision',
            quantity=1,
            unit='global',
            unit_cost=engineering,
            total_cost=engineering
        ))

        # Imprevistos (5%)
        contingency = subtotal_direct * 0.05
        budget_items.append(BudgetItem(
            category='Indirectos',
            subcategory='Imprevistos',
            description='Contingencia 5%',
            quantity=1,
            unit='global',
            unit_cost=contingency,
            total_cost=contingency
        ))

        # === TOTALES ===

        total_before_factor = (
            subtotal_direct + engineering + contingency
        )

        total_cost = total_before_factor * self.location_factor

        # Desglose por categoria
        breakdown = {
            'materials': {
                'structure': structure_cost,
                'treads': tread_cost,
                'railing': railing_cost,
                'hardware': hardware_cost,
                'subtotal': structure_cost + tread_cost + railing_cost + hardware_cost
            },
            'fabrication': fabrication_cost,
            'finishing': finishing_cost,
            'transport': transport_cost,
            'installation': installation_cost,
            'indirect': {
                'engineering': engineering,
                'contingency': contingency,
                'subtotal': engineering + contingency
            },
            'subtotal_direct': subtotal_direct,
            'location_factor': self.location_factor,
            'total': total_cost
        }

        # Costos unitarios
        unit_costs = {
            'per_tread': total_cost / max(1, stats['tread_count']),
            'per_meter_height': total_cost / (stats['floor_to_floor'] / 1000),
            'per_kg': total_cost / max(1, tread_result.total_weight if tread_result else 500),
        }

        # Resumen
        summary = {
            'tread_count': stats['tread_count'],
            'floor_height': stats['floor_to_floor'],
            'outer_diameter': stats['outer_diameter'],
            'tread_material': tread_material,
            'structure_type': structure_type,
            'finishing': finishing,
            'total_weight': tread_result.total_weight if tread_result else 0,
            'total_cost': total_cost,
            'cost_per_tread': unit_costs['per_tread'],
            'currency': self.currency
        }

        # Formato de presupuesto
        formatted = self._format_budget(budget_items, breakdown, summary)

        return CostResult(
            total_cost=total_cost,
            breakdown=breakdown,
            budget_items=budget_items,
            unit_costs=unit_costs,
            summary=summary,
            formatted_budget=formatted
        )

    def _calculate_structure_cost(self, stats, structure_type, budget_items):
        """Calcula costo de estructura."""
        cost = 0
        height = stats['floor_to_floor'] / 1000  # m

        if structure_type == 'central_column':
            # Columna central (tubo)
            column_diameter = 0.150  # m
            column_thickness = 0.006  # m
            column_area = math.pi * (column_diameter * column_thickness)
            column_volume = column_area * height
            column_weight = column_volume * 7850  # kg

            column_cost = column_weight / 1000 * self.material_db.STEEL_PRICES['pipe']
            cost += column_cost

            budget_items.append(BudgetItem(
                category='Materiales',
                subcategory='Estructura',
                description=f'Columna central D={column_diameter*1000:.0f}mm',
                quantity=column_weight,
                unit='kg',
                unit_cost=self.material_db.STEEL_PRICES['pipe'] / 1000,
                total_cost=column_cost
            ))

            # Placa base
            base_diameter = 0.400  # m
            base_thickness = 0.020  # m
            base_volume = math.pi * (base_diameter/2)**2 * base_thickness
            base_weight = base_volume * 7850  # kg

            base_cost = base_weight / 1000 * self.material_db.STEEL_PRICES['structural_plate']
            cost += base_cost

            budget_items.append(BudgetItem(
                category='Materiales',
                subcategory='Estructura',
                description='Placa base y superior',
                quantity=base_weight * 2,
                unit='kg',
                unit_cost=self.material_db.STEEL_PRICES['structural_plate'] / 1000,
                total_cost=base_cost * 2
            ))

            cost += base_cost  # Placa superior

        elif structure_type == 'perimeter_beam':
            # Viga helicoidal perimetral
            beam_length = stats['helix_length'] / 1000  # m
            beam_section = 0.10 * 0.15  # m2 (100x150mm)
            beam_weight = beam_section * beam_length * 7850  # kg

            beam_cost = beam_weight / 1000 * self.material_db.STEEL_PRICES['hss_tube']
            cost += beam_cost

            budget_items.append(BudgetItem(
                category='Materiales',
                subcategory='Estructura',
                description='Viga helicoidal perimetral HSS 100x150',
                quantity=beam_weight,
                unit='kg',
                unit_cost=self.material_db.STEEL_PRICES['hss_tube'] / 1000,
                total_cost=beam_cost
            ))

        elif structure_type == 'double_stringer':
            # Doble larguero
            stringer_length = stats['helix_length'] / 1000 * 2  # m (interior + exterior)
            stringer_section = 0.08 * 0.12  # m2
            stringer_weight = stringer_section * stringer_length * 7850

            stringer_cost = stringer_weight / 1000 * self.material_db.STEEL_PRICES['hss_tube']
            cost += stringer_cost

            budget_items.append(BudgetItem(
                category='Materiales',
                subcategory='Estructura',
                description='Largueros helicoidales HSS 80x120',
                quantity=stringer_weight,
                unit='kg',
                unit_cost=self.material_db.STEEL_PRICES['hss_tube'] / 1000,
                total_cost=stringer_cost
            ))

        return cost

    def _calculate_tread_cost(self, stats, material, tread_result, budget_items):
        """Calcula costo de peldanos."""
        cost = 0
        tread_count = stats['tread_count']

        # Estimacion de area por peldano
        inner_r = stats['inner_diameter'] / 2 / 1000  # m
        outer_r = stats['outer_diameter'] / 2 / 1000  # m
        angle_rad = math.radians(stats['rotation_per_tread'])

        # Area de sector
        tread_area = 0.5 * (outer_r**2 - inner_r**2) * angle_rad  # m2
        total_area = tread_area * tread_count

        if material == 'steel':
            thickness = 0.008  # 8mm
            weight = total_area * thickness * 7850  # kg
            unit_cost = self.material_db.STEEL_PRICES['structural_plate'] / 1000

            cost = weight * unit_cost

            budget_items.append(BudgetItem(
                category='Materiales',
                subcategory='Peldanos',
                description=f'{tread_count} peldanos acero {thickness*1000:.0f}mm',
                quantity=weight,
                unit='kg',
                unit_cost=unit_cost,
                total_cost=cost
            ))

        elif material == 'wood':
            thickness = 0.045  # 45mm
            volume = total_area * thickness  # m3
            wood_type = 'oak'  # Default
            unit_cost = self.material_db.WOOD_PRICES[wood_type]

            cost = volume * unit_cost

            budget_items.append(BudgetItem(
                category='Materiales',
                subcategory='Peldanos',
                description=f'{tread_count} peldanos madera encino {thickness*1000:.0f}mm',
                quantity=volume,
                unit='m3',
                unit_cost=unit_cost,
                total_cost=cost
            ))

        elif material == 'glass':
            glass_type = 'laminated_8_8'
            unit_cost = self.material_db.GLASS_PRICES[glass_type]

            cost = total_area * unit_cost

            budget_items.append(BudgetItem(
                category='Materiales',
                subcategory='Peldanos',
                description=f'{tread_count} peldanos vidrio laminado 8+8mm',
                quantity=total_area,
                unit='m2',
                unit_cost=unit_cost,
                total_cost=cost
            ))

        elif material == 'concrete':
            thickness = 0.080  # 80mm
            volume = total_area * thickness
            unit_cost = self.material_db.CONCRETE_PRICES['precast']

            cost = volume * unit_cost

            budget_items.append(BudgetItem(
                category='Materiales',
                subcategory='Peldanos',
                description=f'{tread_count} peldanos concreto prefabricado',
                quantity=volume,
                unit='m3',
                unit_cost=unit_cost,
                total_cost=cost
            ))

        return cost

    def _calculate_railing_cost(self, stats, railing_data, budget_items):
        """Calcula costo de barandales."""
        cost = 0

        # Longitud de pasamanos (estimacion)
        helix_length = stats['helix_length'] / 1000  # m
        handrail_length = helix_length * 2  # Interior + exterior

        # Pasamanos (tubo 42mm)
        handrail_diameter = 0.042  # m
        handrail_thickness = 0.003  # m
        handrail_area = math.pi * (handrail_diameter * handrail_thickness)
        handrail_weight = handrail_area * handrail_length * 7850

        handrail_cost = handrail_weight / 1000 * self.material_db.STEEL_PRICES['pipe']
        cost += handrail_cost

        budget_items.append(BudgetItem(
            category='Materiales',
            subcategory='Barandal',
            description='Pasamanos tubo D42mm',
            quantity=handrail_weight,
            unit='kg',
            unit_cost=self.material_db.STEEL_PRICES['pipe'] / 1000,
            total_cost=handrail_cost
        ))

        # Balaustres
        baluster_count = railing_data.get('baluster_count', stats['tread_count'] * 4) if railing_data else stats['tread_count'] * 4
        baluster_height = 0.9  # m
        baluster_diameter = 0.016  # m
        baluster_weight = math.pi * (baluster_diameter/2)**2 * baluster_height * 7850 * baluster_count

        baluster_cost = baluster_weight / 1000 * self.material_db.STEEL_PRICES['round_bar']
        cost += baluster_cost

        budget_items.append(BudgetItem(
            category='Materiales',
            subcategory='Barandal',
            description=f'{baluster_count} balaustres D16mm',
            quantity=baluster_weight,
            unit='kg',
            unit_cost=self.material_db.STEEL_PRICES['round_bar'] / 1000,
            total_cost=baluster_cost
        ))

        # Postes
        post_count = max(4, stats['tread_count'] // 4)
        post_diameter = 0.050
        post_height = 1.0
        post_weight = math.pi * (post_diameter/2)**2 * post_height * 7850 * post_count

        post_cost = post_weight / 1000 * self.material_db.STEEL_PRICES['pipe']
        cost += post_cost

        budget_items.append(BudgetItem(
            category='Materiales',
            subcategory='Barandal',
            description=f'{post_count} postes D50mm',
            quantity=post_weight,
            unit='kg',
            unit_cost=self.material_db.STEEL_PRICES['pipe'] / 1000,
            total_cost=post_cost
        ))

        return cost

    def _calculate_hardware_cost(self, stats, budget_items):
        """Calcula costo de herrajes y conexiones."""
        tread_count = stats['tread_count']

        # Anclas y tornilleria
        anchors = tread_count * 4 * 25  # 4 anclas por peldano, $25 c/u
        bolts = tread_count * 8 * 8  # 8 tornillos por peldano, $8 c/u

        hardware_cost = anchors + bolts

        budget_items.append(BudgetItem(
            category='Materiales',
            subcategory='Herrajes',
            description='Anclas, tornillos y conectores',
            quantity=1,
            unit='lote',
            unit_cost=hardware_cost,
            total_cost=hardware_cost
        ))

        return hardware_cost

    def _calculate_fabrication_cost(self, stats, structure_type, material, budget_items):
        """Calcula costo de fabricacion."""
        tread_count = stats['tread_count']

        # Horas estimadas por operacion
        cutting_hrs = tread_count * 0.5 + 8  # Corte
        welding_hrs = tread_count * 1.0 + 16  # Soldadura
        assembly_hrs = tread_count * 0.75 + 8  # Ensamble

        cutting_cost = cutting_hrs * self.labor_db.FABRICATION_RATES['cutting']
        welding_cost = welding_hrs * self.labor_db.FABRICATION_RATES['welding']
        assembly_cost = assembly_hrs * self.labor_db.FABRICATION_RATES['assembly']

        total_fab = cutting_cost + welding_cost + assembly_cost

        budget_items.append(BudgetItem(
            category='Fabricacion',
            subcategory='Corte',
            description=f'{cutting_hrs:.1f} hrs corte',
            quantity=cutting_hrs,
            unit='hr',
            unit_cost=self.labor_db.FABRICATION_RATES['cutting'],
            total_cost=cutting_cost
        ))

        budget_items.append(BudgetItem(
            category='Fabricacion',
            subcategory='Soldadura',
            description=f'{welding_hrs:.1f} hrs soldadura',
            quantity=welding_hrs,
            unit='hr',
            unit_cost=self.labor_db.FABRICATION_RATES['welding'],
            total_cost=welding_cost
        ))

        budget_items.append(BudgetItem(
            category='Fabricacion',
            subcategory='Ensamble',
            description=f'{assembly_hrs:.1f} hrs ensamble',
            quantity=assembly_hrs,
            unit='hr',
            unit_cost=self.labor_db.FABRICATION_RATES['assembly'],
            total_cost=assembly_cost
        ))

        return total_fab

    def _calculate_finishing_cost(self, stats, tread_result, railing_data,
                                   finishing, budget_items):
        """Calcula costo de acabados."""
        # Estimar area total a pintar
        tread_count = stats['tread_count']
        inner_r = stats['inner_diameter'] / 2 / 1000
        outer_r = stats['outer_diameter'] / 2 / 1000
        angle_rad = math.radians(stats['rotation_per_tread'])

        tread_area = 0.5 * (outer_r**2 - inner_r**2) * angle_rad * 2  # Ambas caras
        total_tread_area = tread_area * tread_count

        # Estructura y barandales (estimacion)
        structure_area = stats['helix_length'] / 1000 * 0.4  # m2
        railing_area = stats['helix_length'] / 1000 * 0.3 * 2  # m2

        total_area = total_tread_area + structure_area + railing_area

        # Preparacion de superficie
        prep_cost = total_area * 150  # Sandblast
        budget_items.append(BudgetItem(
            category='Acabados',
            subcategory='Preparacion',
            description='Sandblast SA 2.5',
            quantity=total_area,
            unit='m2',
            unit_cost=150,
            total_cost=prep_cost
        ))

        # Acabado final
        finish_rate = self.material_db.FINISHING_PRICES.get(finishing, 350)
        finish_cost = total_area * finish_rate

        budget_items.append(BudgetItem(
            category='Acabados',
            subcategory=finishing.replace('_', ' ').title(),
            description=f'Acabado {finishing}',
            quantity=total_area,
            unit='m2',
            unit_cost=finish_rate,
            total_cost=finish_cost
        ))

        return prep_cost + finish_cost

    def _calculate_transport_cost(self, stats, budget_items):
        """Calcula costo de transporte."""
        # Estimar peso total
        estimated_weight = stats['tread_count'] * 50 + 200  # kg

        # Costo base de transporte
        if estimated_weight < 500:
            transport_cost = 3500
        elif estimated_weight < 1000:
            transport_cost = 5500
        else:
            transport_cost = 8500

        budget_items.append(BudgetItem(
            category='Transporte',
            subcategory='Flete',
            description='Transporte a obra',
            quantity=1,
            unit='viaje',
            unit_cost=transport_cost,
            total_cost=transport_cost
        ))

        # Maniobras de descarga
        maniobras = 2500
        budget_items.append(BudgetItem(
            category='Transporte',
            subcategory='Maniobras',
            description='Descarga y ubicacion',
            quantity=1,
            unit='global',
            unit_cost=maniobras,
            total_cost=maniobras
        ))

        return transport_cost + maniobras

    def _calculate_installation_cost(self, stats, structure_type, budget_items):
        """Calcula costo de instalacion."""
        height = stats['floor_to_floor'] / 1000  # m
        tread_count = stats['tread_count']

        # Dias de trabajo estimados
        install_days = max(3, tread_count // 4)

        # Cuadrilla: 1 supervisor + 2 instaladores + 1 soldador + 1 ayudante
        daily_labor = (
            self.labor_db.INSTALLATION_RATES['supervisor'] +
            self.labor_db.INSTALLATION_RATES['installer'] * 2 +
            self.labor_db.INSTALLATION_RATES['welder_field'] +
            self.labor_db.INSTALLATION_RATES['helper']
        )

        labor_cost = daily_labor * install_days

        budget_items.append(BudgetItem(
            category='Instalacion',
            subcategory='Mano de obra',
            description=f'{install_days} dias cuadrilla instalacion',
            quantity=install_days,
            unit='dia',
            unit_cost=daily_labor,
            total_cost=labor_cost
        ))

        # Equipo
        if height > 3:
            # Necesita andamio
            scaffold_area = stats['outer_diameter'] / 1000 * 2 * height
            scaffold_cost = scaffold_area * self.labor_db.EQUIPMENT_RATES['scaffolding']

            budget_items.append(BudgetItem(
                category='Instalacion',
                subcategory='Equipo',
                description='Andamio',
                quantity=scaffold_area,
                unit='m2',
                unit_cost=self.labor_db.EQUIPMENT_RATES['scaffolding'],
                total_cost=scaffold_cost
            ))
        else:
            scaffold_cost = 0

        # Equipo de soldadura
        welder_cost = install_days * self.labor_db.EQUIPMENT_RATES['welder_portable']

        budget_items.append(BudgetItem(
            category='Instalacion',
            subcategory='Equipo',
            description='Equipo de soldadura portatil',
            quantity=install_days,
            unit='dia',
            unit_cost=self.labor_db.EQUIPMENT_RATES['welder_portable'],
            total_cost=welder_cost
        ))

        return labor_cost + scaffold_cost + welder_cost

    def _format_budget(self, items, breakdown, summary):
        """Formatea el presupuesto para presentacion."""
        lines = []
        lines.append("=" * 70)
        lines.append("PRESUPUESTO - ESCALERA HELICOIDAL PARAMETRICA")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Peldanos: {summary['tread_count']}")
        lines.append(f"Altura: {summary['floor_height']/1000:.2f} m")
        lines.append(f"Diametro: {summary['outer_diameter']/1000:.2f} m")
        lines.append(f"Material peldanos: {summary['tread_material']}")
        lines.append(f"Estructura: {summary['structure_type']}")
        lines.append("")
        lines.append("-" * 70)

        # Agrupar por categoria
        categories = {}
        for item in items:
            if item.category not in categories:
                categories[item.category] = []
            categories[item.category].append(item)

        for category, cat_items in categories.items():
            cat_total = sum(item.total_cost for item in cat_items)
            lines.append(f"\n{category.upper()}")
            lines.append("-" * 50)

            for item in cat_items:
                desc = item.description[:35].ljust(35)
                qty = f"{item.quantity:.2f} {item.unit}".ljust(15)
                total = f"${item.total_cost:,.0f}".rjust(12)
                lines.append(f"  {desc} {qty} {total}")

            lines.append(f"  {'Subtotal '.ljust(50)} ${cat_total:,.0f}".rjust(12))

        lines.append("")
        lines.append("=" * 70)
        lines.append(f"TOTAL {summary['currency']}: ${summary['total_cost']:,.0f}".rjust(70))
        lines.append(f"Costo por peldano: ${summary['cost_per_tread']:,.0f}".rjust(70))
        lines.append("=" * 70)

        return "\n".join(lines)


# Punto de entrada para Grasshopper
if __name__ == "__main__":
    calculator = SpiralStairCostCalculator(
        location_factor=location_factor if 'location_factor' in dir() else 1.0
    )

    result = calculator.calculate(
        spiral_data=spiral_data if 'spiral_data' in dir() else None,
        tread_result=tread_result if 'tread_result' in dir() else None,
        railing_data=railing_data if 'railing_data' in dir() else None,
        tread_material=tread_material if 'tread_material' in dir() else 'steel',
        structure_type=structure_type if 'structure_type' in dir() else 'central_column',
        finishing=finishing if 'finishing' in dir() else 'powder_coat'
    )

    # Salidas para Grasshopper
    total_cost = result.total_cost
    cost_breakdown = result.breakdown
    budget = result.budget_items
    unit_costs = result.unit_costs
    summary = result.summary
    formatted_budget = result.formatted_budget
