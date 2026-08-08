"""
Panel Classifier - Muro Cortina Parametrico
Clasifica y genera los paneles de vidrio, spandrel y solidos.

Inputs:
    cells (List[GridCell]): Celdas de la grilla
    glass_type (str): Tipo de vidrio (single/double/triple)
    spandrel_height (float): Altura del spandrel (mm)
    panel_pattern (str): Patron (vision/mixed/alternating/custom)
    vision_percent (float): Porcentaje de vision objetivo (%)
    floor_levels (List[float]): Niveles de piso (mm) - opcional

Outputs:
    vision_panels (List[Brep]): Paneles de vision (vidrio)
    spandrel_panels (List[Brep]): Paneles de spandrel
    solid_panels (List[Brep]): Paneles solidos
    panel_data (List[dict]): Datos de cada panel
    summary (dict): Resumen de paneles
"""

import Rhino.Geometry as rg
import math
from collections import namedtuple
from enum import Enum

# Tipos de panel
class PanelType(Enum):
    VISION = "vision"
    SPANDREL = "spandrel"
    SOLID = "solid"
    OPERABLE = "operable"
    LOUVER = "louver"


# Datos del panel
PanelData = namedtuple('PanelData', [
    'type', 'surface', 'brep', 'area', 'center',
    'normal', 'glass_type', 'u_value', 'shgc',
    'is_curved', 'curvature_type', 'index'
])

ClassificationResult = namedtuple('ClassificationResult', [
    'vision_panels', 'spandrel_panels', 'solid_panels',
    'operable_panels', 'panel_data', 'summary'
])


class GlassProperties:
    """Propiedades de diferentes tipos de vidrio."""

    GLASS_DATA = {
        'single_clear': {
            'thickness': 6,
            'u_value': 5.8,
            'shgc': 0.82,
            'vlt': 0.88,
            'weight': 15  # kg/m2
        },
        'single_tinted': {
            'thickness': 6,
            'u_value': 5.7,
            'shgc': 0.60,
            'vlt': 0.50,
            'weight': 15
        },
        'double_clear': {
            'thickness': 24,
            'u_value': 2.8,
            'shgc': 0.70,
            'vlt': 0.78,
            'weight': 30
        },
        'double_low_e': {
            'thickness': 24,
            'u_value': 1.6,
            'shgc': 0.42,
            'vlt': 0.70,
            'weight': 30
        },
        'double_low_e_argon': {
            'thickness': 24,
            'u_value': 1.1,
            'shgc': 0.38,
            'vlt': 0.68,
            'weight': 30
        },
        'triple_low_e': {
            'thickness': 44,
            'u_value': 0.8,
            'shgc': 0.35,
            'vlt': 0.60,
            'weight': 45
        },
        'triple_low_e_argon': {
            'thickness': 44,
            'u_value': 0.5,
            'shgc': 0.30,
            'vlt': 0.55,
            'weight': 45
        }
    }

    @classmethod
    def get_properties(cls, glass_type):
        """Obtiene propiedades del tipo de vidrio."""
        # Mapear tipos simplificados
        type_map = {
            'single': 'single_clear',
            'double': 'double_low_e',
            'triple': 'triple_low_e'
        }

        key = type_map.get(glass_type, glass_type)
        return cls.GLASS_DATA.get(key, cls.GLASS_DATA['double_low_e'])


class PanelClassifier:
    """Clasifica y genera paneles del muro cortina."""

    def __init__(self, glass_thickness=24, spandrel_insulation=50):
        """
        Args:
            glass_thickness: Espesor del vidrio (mm)
            spandrel_insulation: Espesor del aislamiento spandrel (mm)
        """
        self.glass_thickness = glass_thickness / 1000.0  # a metros
        self.spandrel_insulation = spandrel_insulation / 1000.0
        self.min_panel_area = 0.1  # m2 minimo

    def classify(self, cells, glass_type='double',
                 spandrel_height=900, panel_pattern='mixed',
                 vision_percent=70, floor_levels=None):
        """
        Clasifica y genera los paneles.

        Args:
            cells: Lista de GridCell
            glass_type: Tipo de vidrio
            spandrel_height: Altura spandrel (mm)
            panel_pattern: Patron de paneles
            vision_percent: Porcentaje de vision objetivo
            floor_levels: Niveles de piso (mm)

        Returns:
            ClassificationResult
        """
        if not cells:
            return ClassificationResult([], [], [], [], [], {})

        # Convertir spandrel_height a metros
        spandrel_h = spandrel_height / 1000.0

        # Obtener propiedades del vidrio
        glass_props = GlassProperties.get_properties(glass_type)

        # Clasificar cada celda
        vision_panels = []
        spandrel_panels = []
        solid_panels = []
        operable_panels = []
        panel_data = []

        for i, cell in enumerate(cells):
            # Determinar tipo de panel
            panel_type = self._determine_panel_type(
                cell, spandrel_h, panel_pattern,
                vision_percent, floor_levels
            )

            # Crear geometria del panel
            panel_brep = self._create_panel_geometry(
                cell, panel_type, glass_props
            )

            if panel_brep is None:
                continue

            # Determinar propiedades segun tipo
            if panel_type == PanelType.VISION:
                u_value = glass_props['u_value']
                shgc = glass_props['shgc']
            elif panel_type == PanelType.SPANDREL:
                u_value = 0.35  # Con aislamiento
                shgc = 0.0
            else:  # SOLID
                u_value = 0.25
                shgc = 0.0

            # Crear datos del panel
            data = PanelData(
                type=panel_type.value,
                surface=cell.surface,
                brep=panel_brep,
                area=cell.area,
                center=cell.center,
                normal=cell.normal,
                glass_type=glass_type if panel_type == PanelType.VISION else None,
                u_value=u_value,
                shgc=shgc,
                is_curved=not cell.is_planar,
                curvature_type=cell.curvature.get('type', 'flat'),
                index=i
            )
            panel_data.append(data)

            # Agregar a lista correspondiente
            if panel_type == PanelType.VISION:
                vision_panels.append(panel_brep)
            elif panel_type == PanelType.SPANDREL:
                spandrel_panels.append(panel_brep)
            elif panel_type == PanelType.OPERABLE:
                operable_panels.append(panel_brep)
            else:
                solid_panels.append(panel_brep)

        # Calcular resumen
        summary = self._calculate_summary(panel_data, glass_props)

        return ClassificationResult(
            vision_panels=vision_panels,
            spandrel_panels=spandrel_panels,
            solid_panels=solid_panels,
            operable_panels=operable_panels,
            panel_data=panel_data,
            summary=summary
        )

    def _determine_panel_type(self, cell, spandrel_height,
                               pattern, vision_percent, floor_levels):
        """
        Determina el tipo de panel para una celda.

        Returns:
            PanelType
        """
        center = cell.center

        # Verificar si esta en zona de spandrel (cerca de niveles de piso)
        if floor_levels and spandrel_height > 0:
            for level in floor_levels:
                level_m = level / 1000.0
                if abs(center.Z - level_m) < spandrel_height:
                    return PanelType.SPANDREL

        # Aplicar patron
        if pattern == 'vision':
            return PanelType.VISION

        elif pattern == 'spandrel':
            return PanelType.SPANDREL

        elif pattern == 'alternating':
            # Patron de tablero de ajedrez
            u_idx = cell.index_u if hasattr(cell, 'index_u') else 0
            v_idx = cell.index_v if hasattr(cell, 'index_v') else 0
            if (u_idx + v_idx) % 2 == 0:
                return PanelType.VISION
            else:
                return PanelType.SPANDREL

        elif pattern == 'horizontal_bands':
            # Bandas horizontales
            v_idx = cell.index_v if hasattr(cell, 'index_v') else 0
            if v_idx % 3 == 0:  # Cada tercera fila
                return PanelType.SPANDREL
            return PanelType.VISION

        elif pattern == 'mixed':
            # Usar porcentaje de vision con preferencia a paneles inferiores
            v_idx = cell.index_v if hasattr(cell, 'index_v') else 0
            # Paneles inferiores tienden a ser spandrel
            if v_idx == 0:
                return PanelType.SPANDREL
            return PanelType.VISION

        else:  # custom u otros
            return PanelType.VISION

    def _create_panel_geometry(self, cell, panel_type, glass_props):
        """
        Crea la geometria 3D del panel.

        Args:
            cell: GridCell
            panel_type: PanelType
            glass_props: Propiedades del vidrio

        Returns:
            Brep: Geometria del panel
        """
        surface = cell.surface
        if surface is None:
            return None

        # Determinar espesor segun tipo
        if panel_type == PanelType.VISION:
            thickness = glass_props['thickness'] / 1000.0
        elif panel_type == PanelType.SPANDREL:
            thickness = (glass_props['thickness'] / 1000.0 +
                        self.spandrel_insulation)
        else:
            thickness = 0.100  # 100mm para paneles solidos

        # Offset hacia interior
        offset = thickness / 2

        try:
            # Intentar crear offset de superficie
            offset_surfaces = rg.Surface.Offset(
                surface, offset, self.min_panel_area
            )

            if offset_surfaces and len(offset_surfaces) > 0:
                # Crear loft entre superficies
                breps = []
                breps.extend(rg.Brep.CreateFromOffsetFace(
                    surface.ToBrep().Faces[0],
                    thickness, self.min_panel_area,
                    True,  # solid
                    True   # extend
                ))
                if breps:
                    return breps[0]
        except:
            pass

        # Fallback: extrusion simple
        return self._extrude_surface(surface, thickness, cell.normal)

    def _extrude_surface(self, surface, thickness, normal):
        """Extrude una superficie en direccion de la normal."""
        try:
            brep = surface.ToBrep()
            if brep is None:
                return None

            # Direccion de extrusion
            direction = rg.Vector3d(normal)
            direction.Unitize()
            direction *= -thickness  # Hacia interior

            # Extruir
            extruded = brep.Faces[0].CreateExtrusion(
                rg.LineCurve(
                    rg.Point3d.Origin,
                    rg.Point3d(direction)
                ),
                True  # cap
            )

            return extruded
        except:
            return surface.ToBrep()

    def _calculate_summary(self, panel_data, glass_props):
        """Calcula resumen de paneles."""
        if not panel_data:
            return {}

        # Contadores
        vision_count = sum(1 for p in panel_data if p.type == 'vision')
        spandrel_count = sum(1 for p in panel_data if p.type == 'spandrel')
        solid_count = sum(1 for p in panel_data if p.type == 'solid')
        operable_count = sum(1 for p in panel_data if p.type == 'operable')

        # Areas
        vision_area = sum(p.area for p in panel_data if p.type == 'vision')
        spandrel_area = sum(p.area for p in panel_data if p.type == 'spandrel')
        solid_area = sum(p.area for p in panel_data if p.type == 'solid')
        total_area = sum(p.area for p in panel_data)

        # U-value promedio ponderado
        total_ua = sum(p.area * p.u_value for p in panel_data)
        avg_u_value = total_ua / total_area if total_area > 0 else 0

        # SHGC promedio (solo vision)
        if vision_area > 0:
            total_shgc = sum(p.area * p.shgc for p in panel_data if p.type == 'vision')
            avg_shgc = total_shgc / vision_area
        else:
            avg_shgc = 0

        # Paneles curvos
        curved_count = sum(1 for p in panel_data if p.is_curved)

        return {
            'total_panels': len(panel_data),
            'vision_panels': vision_count,
            'spandrel_panels': spandrel_count,
            'solid_panels': solid_count,
            'operable_panels': operable_count,
            'curved_panels': curved_count,
            'planar_panels': len(panel_data) - curved_count,
            'total_area': total_area,
            'vision_area': vision_area,
            'spandrel_area': spandrel_area,
            'solid_area': solid_area,
            'vision_percent': (vision_area / total_area * 100) if total_area > 0 else 0,
            'avg_u_value': avg_u_value,
            'avg_shgc': avg_shgc,
            'glass_weight': vision_area * glass_props['weight']
        }


class PanelOptimizer:
    """Optimiza la distribucion de paneles para eficiencia energetica."""

    def __init__(self, target_u_value=1.5, target_shgc=0.4):
        """
        Args:
            target_u_value: U-value objetivo (W/m2K)
            target_shgc: SHGC objetivo
        """
        self.target_u_value = target_u_value
        self.target_shgc = target_shgc

    def optimize_vision_percent(self, orientation, climate_zone='temperate'):
        """
        Recomienda porcentaje de vision segun orientacion.

        Args:
            orientation: Orientacion en grados (0=Norte)
            climate_zone: Zona climatica

        Returns:
            dict: Recomendacion
        """
        # Normalizar orientacion
        orientation = orientation % 360

        # Recomendaciones base por orientacion
        if 315 <= orientation or orientation < 45:  # Norte
            base_vision = 80
            recommended_glass = 'double_clear'
        elif 45 <= orientation < 135:  # Este
            base_vision = 65
            recommended_glass = 'double_low_e'
        elif 135 <= orientation < 225:  # Sur
            base_vision = 50
            recommended_glass = 'double_low_e'
        else:  # Oeste
            base_vision = 55
            recommended_glass = 'double_low_e'

        # Ajustar por clima
        if climate_zone == 'hot':
            base_vision *= 0.8
            if 'clear' in recommended_glass:
                recommended_glass = 'double_low_e'
        elif climate_zone == 'cold':
            base_vision *= 1.1
            recommended_glass = recommended_glass.replace('double', 'triple')

        return {
            'vision_percent': min(90, max(30, base_vision)),
            'recommended_glass': recommended_glass,
            'orientation': orientation,
            'orientation_name': self._get_orientation_name(orientation),
            'climate_zone': climate_zone,
            'notes': self._get_optimization_notes(orientation, climate_zone)
        }

    def _get_orientation_name(self, orientation):
        """Obtiene nombre de orientacion."""
        if 315 <= orientation or orientation < 45:
            return 'Norte'
        elif 45 <= orientation < 135:
            return 'Este'
        elif 135 <= orientation < 225:
            return 'Sur'
        else:
            return 'Oeste'

    def _get_optimization_notes(self, orientation, climate_zone):
        """Genera notas de optimizacion."""
        notes = []

        if 135 <= orientation < 225:  # Sur (en hemisferio norte)
            notes.append("Considerar elementos de sombreado horizontales")
            notes.append("Alta ganancia solar en invierno")

        if 45 <= orientation < 135 or 225 <= orientation < 315:  # Este/Oeste
            notes.append("Considerar elementos de sombreado verticales")
            notes.append("Ganancia solar en angulos bajos")

        if climate_zone == 'hot':
            notes.append("Priorizar SHGC bajo sobre VLT")
            notes.append("Considerar vidrio reflectivo")

        if climate_zone == 'cold':
            notes.append("Priorizar U-value bajo")
            notes.append("Maximizar ganancia solar pasiva")

        return notes


# Punto de entrada para Grasshopper
if __name__ == "__main__":
    # Variables de entrada de Grasshopper

    classifier = PanelClassifier()

    result = classifier.classify(
        cells=cell_data if 'cell_data' in dir() else [],
        glass_type=glass_type if 'glass_type' in dir() else 'double',
        spandrel_height=spandrel_height if 'spandrel_height' in dir() else 900,
        panel_pattern=panel_pattern if 'panel_pattern' in dir() else 'mixed',
        vision_percent=vision_percent if 'vision_percent' in dir() else 70,
        floor_levels=floor_levels if 'floor_levels' in dir() else None
    )

    # Salidas para Grasshopper
    vision_panels = result.vision_panels
    spandrel_panels = result.spandrel_panels
    solid_panels = result.solid_panels
    panel_data = result.panel_data
    summary = result.summary
