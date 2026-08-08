"""
revit_exporter.py
Exporta paneles de Grasshopper a Revit como Adaptive Components.

Proyecto: Cubierta Orgánica de Museo
Autor: BIMAC
Versión: 1.0.0

IMPORTANTE: Este script requiere Rhino.inside.Revit activo.
            Ejecutar desde Grasshopper con RiR habilitado.

Uso en Grasshopper (con Rhino.inside.Revit):
    1. Asegurar que RiR está activo en Revit
    2. Agregar componente "Python Script" en Grasshopper
    3. Copiar este código
    4. Conectar inputs:
       - panels (List[Brep]): Lista de paneles
       - panel_types (List[str]): Tipo de cada panel
       - panel_costs (List[float]): Costo de cada panel
       - family_name (str): Nombre de familia adaptativa
    5. Outputs: result_message, created_ids

Inputs:
    panels (List[Brep]): Paneles a exportar
    panel_types (List[str]): Clasificación de cada panel
    panel_costs (List[float]): Costo de cada panel
    family_name (str): Nombre de la familia adaptativa en Revit

Outputs:
    result_message (str): Mensaje de resultado
    created_ids (List[int]): IDs de elementos creados en Revit
"""

import sys

# =============================================================================
# VERIFICACIÓN DE ENTORNO
# =============================================================================

# Intentar importar módulos de Rhino.inside.Revit
try:
    import clr
    clr.AddReference('RevitAPI')
    clr.AddReference('RevitAPIUI')
    clr.AddReference('RevitServices')
    clr.AddReference('RhinoInside.Revit')

    from Autodesk.Revit.DB import *
    from Autodesk.Revit.DB.Structure import *
    from RevitServices.Persistence import DocumentManager
    from RevitServices.Transactions import TransactionManager

    RIR_AVAILABLE = True
except ImportError:
    RIR_AVAILABLE = False
    print("ADVERTENCIA: Rhino.inside.Revit no disponible.")
    print("Este script debe ejecutarse desde Grasshopper con RiR activo.")

import Rhino.Geometry as rg

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

# Factor de conversión de mm (Rhino) a pies (Revit)
MM_TO_FEET = 1.0 / 304.8

# Nombre de familia por defecto
DEFAULT_FAMILY_NAME = "Cubierta_Panel_Adaptive"

# Nombres de parámetros en la familia
PARAM_NAMES = {
    "type": "BIMAC_PanelType",
    "cost": "BIMAC_TotalCost",
    "cost_per_m2": "BIMAC_CostPerM2",
    "material": "BIMAC_Material",
    "u_value": "BIMAC_UValue",
    "panel_id": "BIMAC_PanelID",
    "area": "BIMAC_Area"
}

# Mapeo de tipos a materiales
MATERIAL_MAP = {
    "flat": "Policarbonato Celular 16mm - Plano",
    "single_curve": "Policarbonato Celular 16mm - Curvo",
    "double_curve": "Policarbonato Sólido 10mm - Premium"
}

# Costos por m² por tipo
COST_PER_M2 = {
    "flat": 450.0,
    "single_curve": 680.0,
    "double_curve": 1250.0
}


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def rhino_point_to_revit(rhino_point):
    """
    Convierte un punto de Rhino a coordenadas de Revit.

    Args:
        rhino_point: Punto de Rhino (mm)

    Returns:
        XYZ: Punto de Revit (pies)
    """
    return XYZ(
        rhino_point.X * MM_TO_FEET,
        rhino_point.Y * MM_TO_FEET,
        rhino_point.Z * MM_TO_FEET
    )


def get_panel_vertices(panel):
    """
    Extrae los vértices de un panel (Brep).

    Args:
        panel (Brep): Panel de Rhino

    Returns:
        List[Point3d]: Lista de vértices (máximo 4)
    """
    if panel is None:
        return []

    vertices = []

    try:
        # Intentar obtener vértices de los bordes
        edges = list(panel.Edges)

        for edge in edges[:4]:  # Máximo 4 vértices para quad
            pt = edge.PointAtStart
            if pt not in vertices:
                vertices.append(pt)

        # Si no hay suficientes, intentar con DuplicateVertices
        if len(vertices) < 4:
            brep_vertices = panel.Vertices
            for v in brep_vertices:
                if v.Location not in vertices:
                    vertices.append(v.Location)
                if len(vertices) >= 4:
                    break

    except Exception as ex:
        print(f"Error extrayendo vértices: {ex}")

    return vertices[:4]  # Máximo 4 vértices


def get_panel_area(panel):
    """
    Calcula el área de un panel en m².

    Args:
        panel (Brep): Panel

    Returns:
        float: Área en m²
    """
    try:
        props = rg.AreaMassProperties.Compute(panel)
        if props:
            return props.Area / 1000000.0  # mm² a m²
    except:
        pass
    return 0.0


def find_family_symbol(doc, family_name):
    """
    Busca una familia adaptativa por nombre.

    Args:
        doc: Documento de Revit
        family_name (str): Nombre de la familia

    Returns:
        FamilySymbol o None
    """
    collector = FilteredElementCollector(doc).OfClass(FamilySymbol)

    for fs in collector:
        if fs.FamilyName == family_name:
            return fs

    return None


def set_element_parameter(element, param_name, value):
    """
    Establece el valor de un parámetro en un elemento.

    Args:
        element: Elemento de Revit
        param_name (str): Nombre del parámetro
        value: Valor a establecer
    """
    try:
        param = element.LookupParameter(param_name)

        if param is None:
            return False

        if param.IsReadOnly:
            return False

        if isinstance(value, str):
            param.Set(value)
        elif isinstance(value, bool):
            param.Set(1 if value else 0)
        elif isinstance(value, (int, float)):
            param.Set(float(value))

        return True

    except Exception as ex:
        print(f"Error estableciendo {param_name}: {ex}")
        return False


# =============================================================================
# FUNCIÓN PRINCIPAL DE EXPORTACIÓN
# =============================================================================

def export_panels_to_revit(panels, panel_types, panel_costs, family_name):
    """
    Exporta paneles de Grasshopper a Revit como Adaptive Components.

    Args:
        panels (List[Brep]): Lista de paneles
        panel_types (List[str]): Tipo de cada panel
        panel_costs (List[float]): Costo de cada panel
        family_name (str): Nombre de la familia adaptativa

    Returns:
        tuple: (mensaje_resultado, lista_ids_creados)
    """
    if not RIR_AVAILABLE:
        return "Error: Rhino.inside.Revit no disponible", []

    if panels is None or len(panels) == 0:
        return "Error: No hay paneles para exportar", []

    # Obtener documento activo
    try:
        doc = DocumentManager.Instance.CurrentDBDocument
    except Exception as ex:
        return f"Error obteniendo documento: {ex}", []

    # Buscar familia
    family_symbol = find_family_symbol(doc, family_name)

    if family_symbol is None:
        return f"Error: Familia '{family_name}' no encontrada en el proyecto", []

    # Activar tipo de familia si es necesario
    if not family_symbol.IsActive:
        try:
            TransactionManager.Instance.EnsureInTransaction(doc)
            family_symbol.Activate()
            doc.Regenerate()
        except Exception as ex:
            return f"Error activando familia: {ex}", []

    # Preparar listas de tipos y costos
    if panel_types is None:
        panel_types = ["flat"] * len(panels)
    if panel_costs is None:
        panel_costs = [0.0] * len(panels)

    # Asegurar que las listas tengan el mismo tamaño
    while len(panel_types) < len(panels):
        panel_types.append("flat")
    while len(panel_costs) < len(panels):
        panel_costs.append(0.0)

    # Crear adaptive components
    created_ids = []
    errors = []

    TransactionManager.Instance.EnsureInTransaction(doc)

    for i, panel in enumerate(panels):
        try:
            # Obtener vértices
            vertices = get_panel_vertices(panel)

            if len(vertices) < 3:
                errors.append(f"Panel {i}: Insuficientes vértices")
                continue

            # Convertir vértices a coordenadas de Revit
            revit_points = [rhino_point_to_revit(v) for v in vertices]

            # Crear Adaptive Component
            adaptive = AdaptiveComponentInstanceUtils.CreateAdaptiveComponentInstance(
                doc, family_symbol
            )

            # Obtener puntos de placement
            placement_ids = AdaptiveComponentInstanceUtils.GetInstancePlacementPointElementRefIds(
                adaptive
            )

            # Asignar posiciones
            for j, pt_id in enumerate(placement_ids):
                if j < len(revit_points):
                    pt_element = doc.GetElement(pt_id)
                    if pt_element is not None:
                        pt_element.Position = revit_points[j]

            # Obtener datos del panel
            ptype = panel_types[i] if i < len(panel_types) else "flat"
            pcost = panel_costs[i] if i < len(panel_costs) else 0.0
            parea = get_panel_area(panel)

            # Establecer parámetros
            set_element_parameter(adaptive, PARAM_NAMES["type"], ptype)
            set_element_parameter(adaptive, PARAM_NAMES["cost"], pcost)
            set_element_parameter(adaptive, PARAM_NAMES["cost_per_m2"], COST_PER_M2.get(ptype, 450))
            set_element_parameter(adaptive, PARAM_NAMES["material"], MATERIAL_MAP.get(ptype, ""))
            set_element_parameter(adaptive, PARAM_NAMES["panel_id"], f"PANEL-{i+1:04d}")
            set_element_parameter(adaptive, PARAM_NAMES["area"], parea)

            created_ids.append(adaptive.Id.IntegerValue)

        except Exception as ex:
            errors.append(f"Panel {i}: {str(ex)}")

    TransactionManager.Instance.TransactionTaskDone()

    # Preparar mensaje de resultado
    success_count = len(created_ids)
    error_count = len(errors)

    result_message = f"""
================================================================================
                     EXPORTACIÓN A REVIT COMPLETADA
================================================================================

RESUMEN:
--------------------------------------------------------------------------------
  Paneles procesados:    {len(panels)}
  Creados exitosamente:  {success_count}
  Errores:               {error_count}

FAMILIA UTILIZADA: {family_name}

"""

    if errors:
        result_message += "ERRORES:\n"
        for err in errors[:10]:  # Mostrar máximo 10 errores
            result_message += f"  - {err}\n"
        if len(errors) > 10:
            result_message += f"  ... y {len(errors) - 10} errores más\n"

    result_message += "================================================================================\n"

    return result_message, created_ids


# =============================================================================
# EJECUCIÓN PRINCIPAL
# =============================================================================

# Verificar inputs con valores por defecto
if 'panels' not in dir():
    panels = []
if 'panel_types' not in dir():
    panel_types = []
if 'panel_costs' not in dir():
    panel_costs = []
if 'family_name' not in dir() or family_name is None:
    family_name = DEFAULT_FAMILY_NAME

# Ejecutar exportación
result_message, created_ids = export_panels_to_revit(
    panels,
    panel_types,
    panel_costs,
    family_name
)

# Imprimir resultado
print(result_message)

# Outputs para Grasshopper
a = result_message
b = created_ids
