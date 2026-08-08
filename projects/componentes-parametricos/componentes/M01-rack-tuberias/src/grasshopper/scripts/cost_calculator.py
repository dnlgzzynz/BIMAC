"""
Cost Calculator - Rack de Tuberias Parametrico
Calcula costos detallados de material, fabricacion e instalacion.

Inputs:
    rack_data (RackData): Datos de la estructura
    support_result (SupportResult): Datos de soportes
    routing_result (RoutingResult): Datos de tuberias
    finishing (str): Tipo de acabado
    location_factor (float): Factor de ubicacion

Outputs:
    total_cost (float): Costo total (MXN)
    cost_breakdown (dict): Desglose por categoria
    budget (dict): Presupuesto detallado
"""

import math
from collections import namedtuple

# Resultado del calculo
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

    # Acero estructural (MXN/kg)
    STEEL_PRICES = {
        'A36': 28,
        'A572_Gr50': 32,
        'A500_Gr_B': 35,
    }

    # Tuberia (MXN/kg)
    PIPE_PRICES = {
        'carbon_steel': 32,
        'stainless_304': 180,
        'stainless_316': 250,
        'alloy': 150,
    }

    # Aislamiento (MXN/m lineal por pulgada de NPS)
    INSULATION_PRICES = {
        'mineral_wool': 85,      # Lana mineral
        'calcium_silicate': 120,  # Silicato de calcio
        'cellular_glass': 180,    # Vidrio celular
        'polyurethane': 95,       # Poliuretano
    }

    # Acabados (MXN/m2)
    FINISHING_PRICES = {
        'primer': 150,
        'paint': 280,
        'galvanize_hot': 15,      # Por kg
        'galvanize_cold': 380,    # Por m2
        'fireproof': 850,
    }

    # Soportes (MXN cada uno)
    SUPPORT_PRICES = {
        'shoe_small': 450,        # ≤4"
        'shoe_medium': 650,       # 6-8"
        'shoe_large': 950,        # ≥10"
        'guide': 850,
        'anchor': 1200,
        'hanger_rod': 750,
        'spring_variable': 2500,
        'spring_constant': 4500,
    }

    # Bandeja de cables (MXN/m)
    CABLE_TRAY_PRICES = {
        'ladder_300': 650,
        'ladder_450': 750,
        'ladder_600': 850,
        'solid_300': 850,
        'solid_450': 1050,
        'solid_600': 1200,
        'mesh_300': 450,
        'mesh_450': 550,
        'mesh_600': 650,
    }


class LaborCostDatabase:
    """Base de datos de costos de mano de obra."""

    # Fabricacion (MXN/hr)
    FABRICATION_RATES = {
        'cutting': 420,
        'welding': 580,
        'drilling': 380,
        'assembly': 450,
        'blasting': 350,
        'painting': 320,
        'quality_control': 650,
    }

    # Instalacion (MXN/jornada)
    INSTALLATION_RATES = {
        'helper': 450,
        'ironworker': 750,
        'pipefitter': 850,
        'welder_certified': 950,
        'insulator': 650,
        'electrician': 750,
        'supervisor': 1400,
    }

    # Equipo (MXN/dia)
    EQUIPMENT_RATES = {
        'crane_15ton': 12000,
        'crane_30ton': 18000,
        'crane_50ton': 25000,
        'manlift': 3500,
        'forklift': 2800,
        'welder_machine': 1200,
        'compressor': 1500,
    }


class PipeRackCostCalculator:
    """Calculadora de costos para pipe rack."""

    def __init__(self, location_factor=1.0, currency='MXN'):
        self.location_factor = location_factor
        self.currency = currency
        self.material_db = MaterialCostDatabase()
        self.labor_db = LaborCostDatabase()

    def calculate(self, rack_data, support_result=None, routing_result=None,
                  material='A36', finishing='paint'):
        """
        Calcula costo total del pipe rack.

        Args:
            rack_data: Datos de la estructura
            support_result: Resultado de soportes
            routing_result: Resultado de ruteo de tuberias
            material: Material estructural
            finishing: Tipo de acabado

        Returns:
            CostResult
        """
        budget_items = []
        summary = rack_data.summary

        # === 1. ESTRUCTURA ===
        structure_cost = self._calculate_structure_cost(
            rack_data, material, budget_items
        )

        # === 2. SOPORTES ===
        support_cost = 0
        if support_result:
            support_cost = self._calculate_support_cost(
                support_result, budget_items
            )

        # === 3. TUBERIAS ===
        piping_cost = 0
        if routing_result:
            piping_cost = self._calculate_piping_cost(
                routing_result, budget_items
            )

        # === 4. AISLAMIENTO ===
        insulation_cost = 0
        if routing_result:
            insulation_cost = self._calculate_insulation_cost(
                routing_result, budget_items
            )

        # === 5. FABRICACION ===
        fabrication_cost = self._calculate_fabrication_cost(
            rack_data, budget_items
        )

        # === 6. ACABADOS ===
        finishing_cost = self._calculate_finishing_cost(
            rack_data, finishing, budget_items
        )

        # === 7. TRANSPORTE ===
        transport_cost = self._calculate_transport_cost(
            rack_data, budget_items
        )

        # === 8. INSTALACION ===
        installation_cost = self._calculate_installation_cost(
            rack_data, support_result, routing_result, budget_items
        )

        # === SUBTOTAL DIRECTO ===
        subtotal_direct = (
            structure_cost + support_cost + piping_cost +
            insulation_cost + fabrication_cost + finishing_cost +
            transport_cost + installation_cost
        )

        # === 9. INDIRECTOS ===

        # Ingenieria (6%)
        engineering = subtotal_direct * 0.06
        budget_items.append(BudgetItem(
            category='Indirectos',
            subcategory='Ingenieria',
            description='Ingenieria y planos de taller',
            quantity=1,
            unit='global',
            unit_cost=engineering,
            total_cost=engineering
        ))

        # Supervision (4%)
        supervision = subtotal_direct * 0.04
        budget_items.append(BudgetItem(
            category='Indirectos',
            subcategory='Supervision',
            description='Supervision de obra',
            quantity=1,
            unit='global',
            unit_cost=supervision,
            total_cost=supervision
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

        # === TOTAL ===
        total_before_factor = subtotal_direct + engineering + supervision + contingency
        total_cost = total_before_factor * self.location_factor

        # Desglose
        breakdown = {
            'structure': structure_cost,
            'supports': support_cost,
            'piping': piping_cost,
            'insulation': insulation_cost,
            'fabrication': fabrication_cost,
            'finishing': finishing_cost,
            'transport': transport_cost,
            'installation': installation_cost,
            'indirect': {
                'engineering': engineering,
                'supervision': supervision,
                'contingency': contingency,
                'subtotal': engineering + supervision + contingency
            },
            'subtotal_direct': subtotal_direct,
            'location_factor': self.location_factor,
            'total': total_cost
        }

        # Costos unitarios
        unit_costs = {
            'per_meter_length': total_cost / (summary['total_length'] / 1000),
            'per_bay': total_cost / max(1, summary['bay_count']),
            'per_kg_steel': total_cost / max(1, summary['total_weight']),
            'per_tier': total_cost / max(1, summary['tier_count']),
        }

        # Resumen
        result_summary = {
            'rack_length': summary['total_length'],
            'bay_count': summary['bay_count'],
            'tier_count': summary['tier_count'],
            'steel_weight': summary['total_weight'],
            'material': material,
            'finishing': finishing,
            'total_cost': total_cost,
            'cost_per_meter': unit_costs['per_meter_length'],
            'currency': self.currency
        }

        # Formato
        formatted = self._format_budget(budget_items, breakdown, result_summary)

        return CostResult(
            total_cost=total_cost,
            breakdown=breakdown,
            budget_items=budget_items,
            unit_costs=unit_costs,
            summary=result_summary,
            formatted_budget=formatted
        )

    def _calculate_structure_cost(self, rack_data, material, budget_items):
        """Calcula costo de estructura de acero."""
        summary = rack_data.summary
        weight = summary['total_weight']
        unit_price = self.material_db.STEEL_PRICES.get(material, 28)

        cost = weight * unit_price

        budget_items.append(BudgetItem(
            category='Materiales',
            subcategory='Estructura',
            description=f'Acero estructural {material}',
            quantity=weight,
            unit='kg',
            unit_cost=unit_price,
            total_cost=cost
        ))

        # Conexiones y tornilleria (15% del acero)
        connections = weight * unit_price * 0.15

        budget_items.append(BudgetItem(
            category='Materiales',
            subcategory='Estructura',
            description='Placas, tornillos y conexiones',
            quantity=1,
            unit='lote',
            unit_cost=connections,
            total_cost=connections
        ))

        return cost + connections

    def _calculate_support_cost(self, support_result, budget_items):
        """Calcula costo de soportes de tuberia."""
        summary = support_result.summary
        cost = 0

        # Zapatas
        shoe_count = summary['shoe_count']
        shoe_price = self.material_db.SUPPORT_PRICES['shoe_medium']
        shoe_cost = shoe_count * shoe_price
        cost += shoe_cost

        if shoe_count > 0:
            budget_items.append(BudgetItem(
                category='Materiales',
                subcategory='Soportes',
                description='Zapatas de tuberia',
                quantity=shoe_count,
                unit='pza',
                unit_cost=shoe_price,
                total_cost=shoe_cost
            ))

        # Guias
        guide_count = summary['guide_count']
        guide_price = self.material_db.SUPPORT_PRICES['guide']
        guide_cost = guide_count * guide_price
        cost += guide_cost

        if guide_count > 0:
            budget_items.append(BudgetItem(
                category='Materiales',
                subcategory='Soportes',
                description='Guias de tuberia',
                quantity=guide_count,
                unit='pza',
                unit_cost=guide_price,
                total_cost=guide_cost
            ))

        # Anclajes
        anchor_count = summary['anchor_count']
        anchor_price = self.material_db.SUPPORT_PRICES['anchor']
        anchor_cost = anchor_count * anchor_price
        cost += anchor_cost

        if anchor_count > 0:
            budget_items.append(BudgetItem(
                category='Materiales',
                subcategory='Soportes',
                description='Anclajes de tuberia',
                quantity=anchor_count,
                unit='pza',
                unit_cost=anchor_price,
                total_cost=anchor_cost
            ))

        # Bandeja de cables
        tray_segments = summary['tray_segments']
        if tray_segments > 0:
            tray_length = tray_segments * 6  # 6m por segmento
            tray_price = self.material_db.CABLE_TRAY_PRICES['ladder_600']
            tray_cost = tray_length * tray_price

            budget_items.append(BudgetItem(
                category='Materiales',
                subcategory='Bandeja',
                description='Bandeja tipo escalera 600mm',
                quantity=tray_length,
                unit='m',
                unit_cost=tray_price,
                total_cost=tray_cost
            ))
            cost += tray_cost

        return cost

    def _calculate_piping_cost(self, routing_result, budget_items):
        """Calcula costo de tuberias."""
        summary = routing_result.summary
        cost = 0

        # Por cada tamano de tuberia
        pipe_schedule = summary.get('pipe_schedule', [])

        for pipe_info in pipe_schedule:
            nps = pipe_info.get('size', 6)
            count = pipe_info.get('count', 1)
            material = pipe_info.get('material', 'carbon_steel')

            # Estimacion de peso por tamano
            weight_per_m = {2: 5.4, 4: 16.1, 6: 28.3, 8: 43.8, 10: 60.3, 12: 77.0}
            weight = weight_per_m.get(nps, 28.3)

            # Longitud por tuberia
            length = summary.get('total_length', 30000) / 1000  # m

            total_weight = weight * length * count
            unit_price = self.material_db.PIPE_PRICES.get(material, 32)
            pipe_cost = total_weight * unit_price

            budget_items.append(BudgetItem(
                category='Materiales',
                subcategory='Tuberias',
                description=f'Tuberia {nps}" {material}',
                quantity=total_weight,
                unit='kg',
                unit_cost=unit_price,
                total_cost=pipe_cost
            ))

            cost += pipe_cost

        return cost

    def _calculate_insulation_cost(self, routing_result, budget_items):
        """Calcula costo de aislamiento."""
        summary = routing_result.summary
        cost = 0

        # Longitud de aislamiento (estimacion)
        total_length = summary.get('total_length', 30000) / 1000  # m
        insulated_pipes = len([p for p in summary.get('pipe_schedule', [])
                              if p.get('insulated', True)])

        if insulated_pipes > 0:
            # Promedio de costo por metro lineal
            avg_cost = 350  # MXN/m incluyendo cladding
            insulation_cost = total_length * insulated_pipes * avg_cost

            budget_items.append(BudgetItem(
                category='Materiales',
                subcategory='Aislamiento',
                description='Aislamiento y recubrimiento',
                quantity=total_length * insulated_pipes,
                unit='m',
                unit_cost=avg_cost,
                total_cost=insulation_cost
            ))

            cost = insulation_cost

        return cost

    def _calculate_fabrication_cost(self, rack_data, budget_items):
        """Calcula costo de fabricacion."""
        summary = rack_data.summary
        weight = summary['total_weight']

        # Horas por tonelada (promedio)
        hrs_per_ton = {
            'cutting': 4,
            'welding': 12,
            'drilling': 3,
            'assembly': 6,
        }

        tons = weight / 1000
        total_cost = 0

        for operation, hrs in hrs_per_ton.items():
            op_hours = hrs * tons
            rate = self.labor_db.FABRICATION_RATES[operation]
            op_cost = op_hours * rate

            budget_items.append(BudgetItem(
                category='Fabricacion',
                subcategory=operation.title(),
                description=f'{operation.title()} - {op_hours:.1f} hrs',
                quantity=op_hours,
                unit='hr',
                unit_cost=rate,
                total_cost=op_cost
            ))

            total_cost += op_cost

        return total_cost

    def _calculate_finishing_cost(self, rack_data, finishing, budget_items):
        """Calcula costo de acabados."""
        summary = rack_data.summary
        weight = summary['total_weight']

        # Estimacion de area (m2/ton de acero)
        area_per_ton = 25
        area = (weight / 1000) * area_per_ton

        if finishing == 'galvanize_hot':
            # Galvanizado por peso
            unit_price = self.material_db.FINISHING_PRICES['galvanize_hot']
            cost = weight * unit_price
            unit = 'kg'
            qty = weight
        else:
            unit_price = self.material_db.FINISHING_PRICES.get(finishing, 280)
            cost = area * unit_price
            unit = 'm2'
            qty = area

        budget_items.append(BudgetItem(
            category='Acabados',
            subcategory=finishing.replace('_', ' ').title(),
            description=f'Acabado {finishing}',
            quantity=qty,
            unit=unit,
            unit_cost=unit_price,
            total_cost=cost
        ))

        # Preparacion de superficie
        prep_cost = area * 150
        budget_items.append(BudgetItem(
            category='Acabados',
            subcategory='Preparacion',
            description='Limpieza y preparacion',
            quantity=area,
            unit='m2',
            unit_cost=150,
            total_cost=prep_cost
        ))

        return cost + prep_cost

    def _calculate_transport_cost(self, rack_data, budget_items):
        """Calcula costo de transporte."""
        summary = rack_data.summary
        weight = summary['total_weight']

        # Numero de viajes segun peso
        load_capacity = 20000  # kg por viaje
        trips = math.ceil(weight / load_capacity)

        trip_cost = 8500  # MXN por viaje
        total_cost = trips * trip_cost

        budget_items.append(BudgetItem(
            category='Transporte',
            subcategory='Flete',
            description=f'{trips} viajes a obra',
            quantity=trips,
            unit='viaje',
            unit_cost=trip_cost,
            total_cost=total_cost
        ))

        # Maniobras
        maniobras = weight * 2.5  # MXN/kg
        budget_items.append(BudgetItem(
            category='Transporte',
            subcategory='Maniobras',
            description='Carga y descarga',
            quantity=weight,
            unit='kg',
            unit_cost=2.5,
            total_cost=maniobras
        ))

        return total_cost + maniobras

    def _calculate_installation_cost(self, rack_data, support_result,
                                      routing_result, budget_items):
        """Calcula costo de instalacion."""
        summary = rack_data.summary
        weight = summary['total_weight']

        # Dias de trabajo
        tons = weight / 1000
        install_days = max(5, int(tons * 2))  # 2 dias por tonelada

        # Cuadrilla de instalacion
        daily_crew = (
            2 * self.labor_db.INSTALLATION_RATES['ironworker'] +
            1 * self.labor_db.INSTALLATION_RATES['welder_certified'] +
            2 * self.labor_db.INSTALLATION_RATES['helper'] +
            1 * self.labor_db.INSTALLATION_RATES['supervisor']
        )

        crew_cost = daily_crew * install_days

        budget_items.append(BudgetItem(
            category='Instalacion',
            subcategory='Mano de obra',
            description=f'Cuadrilla {install_days} dias',
            quantity=install_days,
            unit='dia',
            unit_cost=daily_crew,
            total_cost=crew_cost
        ))

        # Grua
        crane_days = max(3, install_days // 2)
        crane_rate = self.labor_db.EQUIPMENT_RATES['crane_30ton']
        crane_cost = crane_days * crane_rate

        budget_items.append(BudgetItem(
            category='Instalacion',
            subcategory='Equipo',
            description=f'Grua 30 ton - {crane_days} dias',
            quantity=crane_days,
            unit='dia',
            unit_cost=crane_rate,
            total_cost=crane_cost
        ))

        # Instalacion de soportes y tuberias
        if support_result:
            support_install = summary.get('total_supports', 0) * 150
            budget_items.append(BudgetItem(
                category='Instalacion',
                subcategory='Soportes',
                description='Instalacion de soportes',
                quantity=summary.get('total_supports', 0),
                unit='pza',
                unit_cost=150,
                total_cost=support_install
            ))
        else:
            support_install = 0

        return crew_cost + crane_cost + support_install

    def _format_budget(self, items, breakdown, summary):
        """Formatea el presupuesto."""
        lines = []
        lines.append("=" * 75)
        lines.append("PRESUPUESTO - RACK DE TUBERIAS PARAMETRICO")
        lines.append("=" * 75)
        lines.append("")
        lines.append(f"Longitud: {summary['rack_length']/1000:.1f} m")
        lines.append(f"Crujias: {summary['bay_count']}")
        lines.append(f"Niveles: {summary['tier_count']}")
        lines.append(f"Peso estructura: {summary['steel_weight']:.0f} kg")
        lines.append("")
        lines.append("-" * 75)

        # Por categoria
        categories = {}
        for item in items:
            if item.category not in categories:
                categories[item.category] = []
            categories[item.category].append(item)

        for category, cat_items in categories.items():
            cat_total = sum(item.total_cost for item in cat_items)
            lines.append(f"\n{category.upper()}")
            lines.append("-" * 55)

            for item in cat_items:
                desc = item.description[:38].ljust(38)
                qty = f"{item.quantity:.1f} {item.unit}".ljust(12)
                total = f"${item.total_cost:,.0f}".rjust(14)
                lines.append(f"  {desc} {qty} {total}")

            lines.append(f"  {'Subtotal '.ljust(50)} ${cat_total:,.0f}".rjust(14))

        lines.append("")
        lines.append("=" * 75)
        lines.append(f"TOTAL {summary['currency']}: ${summary['total_cost']:,.0f}".rjust(75))
        lines.append(f"Costo por metro: ${summary['cost_per_meter']:,.0f}/m".rjust(75))
        lines.append("=" * 75)

        return "\n".join(lines)


# Punto de entrada para Grasshopper
if __name__ == "__main__":
    calculator = PipeRackCostCalculator(
        location_factor=location_factor if 'location_factor' in dir() else 1.0
    )

    result = calculator.calculate(
        rack_data=rack_data if 'rack_data' in dir() else None,
        support_result=support_result if 'support_result' in dir() else None,
        routing_result=routing_result if 'routing_result' in dir() else None,
        material=material if 'material' in dir() else 'A36',
        finishing=finishing if 'finishing' in dir() else 'paint'
    )

    # Salidas
    total_cost = result.total_cost
    cost_breakdown = result.breakdown
    budget = result.budget_items
    unit_costs = result.unit_costs
    summary = result.summary
    formatted_budget = result.formatted_budget
