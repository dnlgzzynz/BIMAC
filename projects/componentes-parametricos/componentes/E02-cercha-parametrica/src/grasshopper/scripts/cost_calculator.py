"""
Cost Calculator - Cercha Parametrica
Calcula costos detallados de fabricacion e instalacion.

Inputs:
    member_data (List[MemberData]): Datos de miembros
    profile_results (List[SelectionResult]): Perfiles seleccionados
    node_result (NodeResult): Resultado de conexiones
    geometry_stats (dict): Estadisticas de geometria
    finishing (str): Tipo de acabado (primer/paint/galvanize)
    installation_type (str): Tipo de instalacion (crane/manual)

Outputs:
    total_cost (float): Costo total (MXN)
    cost_breakdown (dict): Desglose por categoria
    cost_per_kg (float): Costo por kilogramo
    cost_per_m (float): Costo por metro de luz
    report (str): Reporte formateado
"""

from collections import namedtuple
from enum import Enum

# Resultado de costos
CostItem = namedtuple('CostItem', [
    'category', 'item', 'quantity', 'unit',
    'unit_cost', 'subtotal', 'notes'
])

TrussCostResult = namedtuple('TrussCostResult', [
    'total_cost', 'breakdown', 'cost_per_kg', 'cost_per_m',
    'total_weight', 'total_length', 'summary'
])


class TrussCostDatabase:
    """Base de datos de costos para cerchas de acero."""

    # Costos en MXN (2025)
    COSTS = {
        # Material de acero (MXN/kg)
        'steel': {
            'A36': 28,
            'A500_Gr_B': 28,
            'A500_Gr_C': 30,
            'A572_Gr50': 32,
        },

        # Fabricacion (MXN/kg)
        'fabrication': {
            'cutting': {
                'saw': 3,
                'plasma': 5,
                'laser': 8,
            },
            'welding': {
                'manual': 18,
                'semi_auto': 15,
                'robot': 12,
            },
            'drilling': 4,  # por kg
            'assembly': 8,  # por kg
        },

        # Placas de nodo (MXN/kg)
        'gusset_plates': {
            'material': 32,
            'cutting': 8,
            'drilling': 6,
        },

        # Soldadura adicional (MXN/m)
        'welding_consumables': {
            'electrode': 45,
            'wire': 38,
            'gas': 12,
        },

        # Tornilleria (MXN/pieza)
        'bolts': {
            'A325_M16': 35,
            'A325_M20': 48,
            'A325_M22': 58,
            'A325_M24': 72,
            'A490_M20': 65,
            'A490_M24': 95,
            'washer': 8,
            'nut': 12,
        },

        # Acabados (MXN/m2)
        'finishing': {
            'sandblast': {
                'SA2': 65,
                'SA2.5': 85,
                'SA3': 110,
            },
            'primer': {
                'alkyd': 55,
                'epoxy': 85,
                'zinc_rich': 120,
            },
            'paint': {
                'alkyd': 65,
                'polyurethane': 95,
                'epoxy': 110,
            },
            'galvanize': {
                'hot_dip': 12,  # MXN/kg
            },
        },

        # Transporte (MXN)
        'transport': {
            'local_per_ton': 1200,       # < 50 km
            'regional_per_ton': 2500,    # 50-200 km
            'national_per_ton': 4500,    # > 200 km
            'oversize_factor': 1.5,      # piezas > 12m
        },

        # Instalacion (MXN)
        'installation': {
            'crane_per_day': 18000,
            'crane_operator': 2500,
            'rigger_per_day': 1800,
            'welder_per_day': 2200,
            'helper_per_day': 1200,
            'equipment_per_day': 3500,
        },

        # Indirectos (%)
        'indirect': {
            'engineering': 0.05,
            'quality_control': 0.03,
            'admin': 0.08,
            'profit': 0.10,
            'contingency': 0.05,
        },
    }

    @classmethod
    def get_cost(cls, category, item, sub_item=None):
        """Obtiene costo de la base de datos."""
        if category not in cls.COSTS:
            return 0

        cat_data = cls.COSTS[category]

        if isinstance(cat_data, dict):
            if item in cat_data:
                item_data = cat_data[item]
                if isinstance(item_data, dict) and sub_item:
                    return item_data.get(sub_item, 0)
                return item_data if not isinstance(item_data, dict) else 0
        return 0


class TrussCostCalculator:
    """Calculadora de costos para cerchas."""

    def __init__(self, currency='MXN'):
        self.currency = currency
        self.db = TrussCostDatabase()

    def calculate(self, member_data, profile_results, node_result,
                  geometry_stats, material='A500_Gr_B',
                  finishing='paint', installation_type='crane'):
        """
        Calcula el costo total de la cercha.

        Args:
            member_data: Datos de miembros
            profile_results: Perfiles seleccionados
            node_result: Resultado de conexiones
            geometry_stats: Estadisticas de geometria
            material: Tipo de acero
            finishing: Tipo de acabado
            installation_type: Tipo de instalacion

        Returns:
            TrussCostResult
        """
        breakdown = []

        # Calcular peso total
        total_weight = sum(pr.weight for pr in profile_results)
        total_length = geometry_stats.get('total_length', 0) / 1000  # mm a m

        # 1. Costo de material
        material_items = self._calculate_material_cost(
            profile_results, material
        )
        breakdown.extend(material_items)

        # 2. Costo de fabricacion
        fabrication_items = self._calculate_fabrication_cost(
            member_data, profile_results, total_weight
        )
        breakdown.extend(fabrication_items)

        # 3. Costo de placas de nodo
        gusset_items = self._calculate_gusset_cost(node_result)
        breakdown.extend(gusset_items)

        # 4. Costo de soldadura/tornilleria
        connection_items = self._calculate_connection_cost(node_result)
        breakdown.extend(connection_items)

        # 5. Costo de acabados
        finish_items = self._calculate_finishing_cost(
            profile_results, finishing
        )
        breakdown.extend(finish_items)

        # 6. Costo de transporte
        transport_items = self._calculate_transport_cost(
            total_weight, geometry_stats
        )
        breakdown.extend(transport_items)

        # 7. Costo de instalacion
        install_items = self._calculate_installation_cost(
            total_weight, geometry_stats, installation_type
        )
        breakdown.extend(install_items)

        # Calcular subtotal directo
        direct_cost = sum(item.subtotal for item in breakdown)

        # 8. Costos indirectos
        indirect_items = self._calculate_indirect_costs(direct_cost)
        breakdown.extend(indirect_items)

        # Total
        total_cost = sum(item.subtotal for item in breakdown)

        # Metricas
        span = geometry_stats.get('span', 12000) / 1000  # mm a m
        cost_per_kg = total_cost / total_weight if total_weight > 0 else 0
        cost_per_m = total_cost / span if span > 0 else 0

        # Resumen
        summary = self._create_summary(breakdown, total_weight, span)

        return TrussCostResult(
            total_cost=total_cost,
            breakdown=breakdown,
            cost_per_kg=cost_per_kg,
            cost_per_m=cost_per_m,
            total_weight=total_weight,
            total_length=total_length,
            summary=summary
        )

    def _calculate_material_cost(self, profile_results, material):
        """Calcula costo de material de acero."""
        items = []

        # Agrupar por perfil
        profile_weights = {}
        for pr in profile_results:
            name = pr.profile.name
            if name not in profile_weights:
                profile_weights[name] = 0
            profile_weights[name] += pr.weight

        unit_cost = self.db.get_cost('steel', material)

        for profile_name, weight in profile_weights.items():
            subtotal = weight * unit_cost

            items.append(CostItem(
                category='Material',
                item=profile_name,
                quantity=weight,
                unit='kg',
                unit_cost=unit_cost,
                subtotal=subtotal,
                notes=f'Acero {material}'
            ))

        return items

    def _calculate_fabrication_cost(self, member_data, profile_results, total_weight):
        """Calcula costo de fabricacion."""
        items = []

        # Corte
        n_cuts = len(member_data) * 2  # 2 cortes por miembro
        cut_cost = self.db.get_cost('fabrication', 'cutting', 'plasma')
        cut_total = total_weight * cut_cost

        items.append(CostItem(
            category='Fabricacion',
            item='Corte plasma',
            quantity=total_weight,
            unit='kg',
            unit_cost=cut_cost,
            subtotal=cut_total,
            notes=f'{n_cuts} cortes'
        ))

        # Soldadura
        weld_cost = self.db.get_cost('fabrication', 'welding', 'semi_auto')
        weld_total = total_weight * weld_cost

        items.append(CostItem(
            category='Fabricacion',
            item='Soldadura',
            quantity=total_weight,
            unit='kg',
            unit_cost=weld_cost,
            subtotal=weld_total,
            notes='Proceso semi-automatico'
        ))

        # Ensamble
        assembly_cost = self.db.get_cost('fabrication', 'assembly')
        assembly_total = total_weight * assembly_cost

        items.append(CostItem(
            category='Fabricacion',
            item='Ensamble en taller',
            quantity=total_weight,
            unit='kg',
            unit_cost=assembly_cost,
            subtotal=assembly_total,
            notes='Armado y ajuste'
        ))

        return items

    def _calculate_gusset_cost(self, node_result):
        """Calcula costo de placas de nodo."""
        items = []

        if node_result is None:
            return items

        # Estimar peso de placas
        n_gussets = len(node_result.gusset_plates) if node_result.gusset_plates else 0
        if n_gussets == 0:
            return items

        # Peso promedio por placa (estimado)
        avg_weight = 5.0  # kg
        total_weight = n_gussets * avg_weight

        # Material
        mat_cost = self.db.get_cost('gusset_plates', 'material')
        mat_total = total_weight * mat_cost

        items.append(CostItem(
            category='Placas de Nodo',
            item='Material placas',
            quantity=total_weight,
            unit='kg',
            unit_cost=mat_cost,
            subtotal=mat_total,
            notes=f'{n_gussets} placas'
        ))

        # Corte de placas
        cut_cost = self.db.get_cost('gusset_plates', 'cutting')
        cut_total = total_weight * cut_cost

        items.append(CostItem(
            category='Placas de Nodo',
            item='Corte de placas',
            quantity=total_weight,
            unit='kg',
            unit_cost=cut_cost,
            subtotal=cut_total,
            notes='Corte CNC'
        ))

        return items

    def _calculate_connection_cost(self, node_result):
        """Calcula costo de conexiones (soldadura o tornillos)."""
        items = []

        if node_result is None:
            return items

        # Soldadura
        weld_length = node_result.total_weld_length / 1000  # mm a m
        if weld_length > 0:
            consumable_cost = (
                self.db.get_cost('welding_consumables', 'electrode') +
                self.db.get_cost('welding_consumables', 'gas')
            )
            weld_total = weld_length * consumable_cost

            items.append(CostItem(
                category='Conexiones',
                item='Consumibles soldadura',
                quantity=weld_length,
                unit='m',
                unit_cost=consumable_cost,
                subtotal=weld_total,
                notes='Electrodo + gas'
            ))

        # Tornillos
        bolt_count = node_result.total_bolt_count
        if bolt_count > 0:
            bolt_cost = self.db.get_cost('bolts', 'A325_M20')
            washer_cost = self.db.get_cost('bolts', 'washer') * 2
            nut_cost = self.db.get_cost('bolts', 'nut')
            total_per_bolt = bolt_cost + washer_cost + nut_cost

            bolt_total = bolt_count * total_per_bolt

            items.append(CostItem(
                category='Conexiones',
                item='Tornillos A325 M20',
                quantity=bolt_count,
                unit='pza',
                unit_cost=total_per_bolt,
                subtotal=bolt_total,
                notes='Incluye tuercas y rondanas'
            ))

        return items

    def _calculate_finishing_cost(self, profile_results, finishing):
        """Calcula costo de acabados."""
        items = []

        # Calcular superficie total (perimetro * longitud)
        total_surface = 0
        total_weight = 0

        for pr in profile_results:
            profile = pr.profile
            length = pr.length / 1000  # mm a m

            # Perimetro segun tipo
            if profile.type == 'HSS':
                perimeter = 2 * (profile.dimensions[0] + profile.dimensions[1]) / 1000
            elif profile.type == 'PIPE':
                perimeter = 3.14159 * profile.dimensions[0] / 1000
            else:
                perimeter = 2 * (profile.dimensions[0] + profile.dimensions[1]) / 1000

            total_surface += perimeter * length
            total_weight += pr.weight

        # Sandblast
        sandblast_cost = self.db.get_cost('finishing', 'sandblast', 'SA2.5')
        sandblast_total = total_surface * sandblast_cost

        items.append(CostItem(
            category='Acabados',
            item='Sandblast SA 2.5',
            quantity=total_surface,
            unit='m2',
            unit_cost=sandblast_cost,
            subtotal=sandblast_total,
            notes='Preparacion de superficie'
        ))

        if finishing == 'paint':
            # Primer
            primer_cost = self.db.get_cost('finishing', 'primer', 'alkyd')
            primer_total = total_surface * primer_cost

            items.append(CostItem(
                category='Acabados',
                item='Primario alquidalico',
                quantity=total_surface,
                unit='m2',
                unit_cost=primer_cost,
                subtotal=primer_total,
                notes='1 capa'
            ))

            # Pintura
            paint_cost = self.db.get_cost('finishing', 'paint', 'alkyd')
            paint_total = total_surface * paint_cost

            items.append(CostItem(
                category='Acabados',
                item='Esmalte alquidalico',
                quantity=total_surface,
                unit='m2',
                unit_cost=paint_cost,
                subtotal=paint_total,
                notes='2 capas'
            ))

        elif finishing == 'galvanize':
            galv_cost = self.db.get_cost('finishing', 'galvanize', 'hot_dip')
            galv_total = total_weight * galv_cost

            items.append(CostItem(
                category='Acabados',
                item='Galvanizado por inmersion',
                quantity=total_weight,
                unit='kg',
                unit_cost=galv_cost,
                subtotal=galv_total,
                notes='Inmersion en caliente'
            ))

        return items

    def _calculate_transport_cost(self, total_weight, geometry_stats):
        """Calcula costo de transporte."""
        items = []

        tons = total_weight / 1000
        span = geometry_stats.get('span', 12000) / 1000  # mm a m

        # Costo base regional
        transport_cost = self.db.get_cost('transport', 'regional_per_ton')

        # Factor por tamano
        if span > 12:
            transport_cost *= self.db.get_cost('transport', 'oversize_factor')

        transport_total = tons * transport_cost

        items.append(CostItem(
            category='Transporte',
            item='Flete regional',
            quantity=tons,
            unit='ton',
            unit_cost=transport_cost,
            subtotal=transport_total,
            notes='50-200 km'
        ))

        return items

    def _calculate_installation_cost(self, total_weight, geometry_stats, installation_type):
        """Calcula costo de instalacion."""
        items = []

        # Estimar dias de instalacion
        # Regla: 1 ton por dia para cerchas
        tons = total_weight / 1000
        days = max(1, int(tons))

        if installation_type == 'crane':
            # Grua
            crane_cost = self.db.get_cost('installation', 'crane_per_day')
            crane_total = days * crane_cost

            items.append(CostItem(
                category='Instalacion',
                item='Renta de grua',
                quantity=days,
                unit='dia',
                unit_cost=crane_cost,
                subtotal=crane_total,
                notes='Grua de 25 ton'
            ))

            # Operador
            operator_cost = self.db.get_cost('installation', 'crane_operator')
            operator_total = days * operator_cost

            items.append(CostItem(
                category='Instalacion',
                item='Operador de grua',
                quantity=days,
                unit='dia',
                unit_cost=operator_cost,
                subtotal=operator_total,
                notes=''
            ))

        # Riggers
        n_riggers = 2
        rigger_cost = self.db.get_cost('installation', 'rigger_per_day')
        rigger_total = days * n_riggers * rigger_cost

        items.append(CostItem(
            category='Instalacion',
            item='Maniobristas',
            quantity=days * n_riggers,
            unit='jornada',
            unit_cost=rigger_cost,
            subtotal=rigger_total,
            notes=f'{n_riggers} personas'
        ))

        # Soldadores en campo
        n_welders = 2
        welder_cost = self.db.get_cost('installation', 'welder_per_day')
        welder_total = days * n_welders * welder_cost

        items.append(CostItem(
            category='Instalacion',
            item='Soldadores',
            quantity=days * n_welders,
            unit='jornada',
            unit_cost=welder_cost,
            subtotal=welder_total,
            notes=f'{n_welders} personas'
        ))

        # Equipo menor
        equip_cost = self.db.get_cost('installation', 'equipment_per_day')
        equip_total = days * equip_cost

        items.append(CostItem(
            category='Instalacion',
            item='Equipo y herramienta',
            quantity=days,
            unit='dia',
            unit_cost=equip_cost,
            subtotal=equip_total,
            notes='Andamios, plumas, etc.'
        ))

        return items

    def _calculate_indirect_costs(self, direct_cost):
        """Calcula costos indirectos."""
        items = []

        indirect_rates = self.db.COSTS['indirect']

        for item_name, rate in indirect_rates.items():
            subtotal = direct_cost * rate

            items.append(CostItem(
                category='Indirectos',
                item=item_name.replace('_', ' ').title(),
                quantity=1,
                unit='global',
                unit_cost=subtotal,
                subtotal=subtotal,
                notes=f'{rate*100:.0f}%'
            ))

        return items

    def _create_summary(self, breakdown, total_weight, span):
        """Crea resumen de costos."""
        # Agrupar por categoria
        by_category = {}
        for item in breakdown:
            if item.category not in by_category:
                by_category[item.category] = 0
            by_category[item.category] += item.subtotal

        total = sum(by_category.values())

        return {
            'by_category': by_category,
            'total_weight_kg': total_weight,
            'span_m': span,
            'total_cost': total,
            'cost_per_kg': total / total_weight if total_weight > 0 else 0,
            'cost_per_m': total / span if span > 0 else 0
        }

    def generate_report(self, result):
        """Genera reporte de costos formateado."""
        lines = [
            "=" * 75,
            "PRESUPUESTO DE CERCHA ESTRUCTURAL",
            "=" * 75,
            f"Peso total: {result.total_weight:,.1f} kg",
            f"Longitud total: {result.total_length:,.1f} m",
            "-" * 75,
            ""
        ]

        # Agrupar por categoria
        categories = {}
        for item in result.breakdown:
            if item.category not in categories:
                categories[item.category] = []
            categories[item.category].append(item)

        # Imprimir cada categoria
        for category, items in categories.items():
            lines.append(f"{category.upper()}")
            lines.append("-" * 50)

            for item in items:
                qty_str = f"{item.quantity:,.2f}" if isinstance(item.quantity, float) else f"{item.quantity:,}"
                lines.append(
                    f"  {item.item:<30} "
                    f"{qty_str:>8} {item.unit:<4} x "
                    f"${item.unit_cost:>8,.2f} = "
                    f"${item.subtotal:>12,.2f}"
                )
                if item.notes:
                    lines.append(f"    ({item.notes})")

            subtotal = sum(i.subtotal for i in items)
            lines.append(f"  {'Subtotal':<30} {'':>8} {'':>4}   {'':>8}   ${subtotal:>12,.2f}")
            lines.append("")

        # Totales
        lines.append("=" * 75)
        lines.append(f"{'TOTAL':>55} ${result.total_cost:>15,.2f} MXN")
        lines.append(f"{'COSTO POR KG':>55} ${result.cost_per_kg:>15,.2f} MXN/kg")
        lines.append(f"{'COSTO POR METRO DE LUZ':>55} ${result.cost_per_m:>15,.2f} MXN/m")
        lines.append("=" * 75)

        return "\n".join(lines)


# Punto de entrada para Grasshopper
if __name__ == "__main__":
    calculator = TrussCostCalculator()

    result = calculator.calculate(
        member_data=member_data if 'member_data' in dir() else [],
        profile_results=profile_results if 'profile_results' in dir() else [],
        node_result=node_result if 'node_result' in dir() else None,
        geometry_stats=geometry_stats if 'geometry_stats' in dir() else {'span': 12000, 'total_length': 50000},
        material=material if 'material' in dir() else 'A500_Gr_B',
        finishing=finishing if 'finishing' in dir() else 'paint',
        installation_type=installation_type if 'installation_type' in dir() else 'crane'
    )

    # Salidas para Grasshopper
    total_cost = result.total_cost
    cost_breakdown = result.breakdown
    cost_per_kg = result.cost_per_kg
    cost_per_m = result.cost_per_m
    report = calculator.generate_report(result)
