# Prompts de Modelado BIM

---

## 1. Revisión de Modelo por Disciplina

**Nivel:** Intermedio

```
CONTEXTO: Soy BIM Manager revisando un modelo de [DISCIPLINA] en fase de [FASE] para un proyecto de [TIPO DE PROYECTO].

ROL: Actúa como un auditor BIM senior con experiencia en ISO 19650.

TAREA: Revisa la siguiente lista de elementos/parámetros del modelo y proporciona:
1. Elementos que no cumplen con estándares
2. Información faltante crítica
3. Sugerencias de mejora
4. Priorización de correcciones

DATOS DEL MODELO:
[Pegar lista de elementos, warnings, o schedule exportado]

FORMATO: Tabla con columnas: Elemento | Problema | Severidad | Acción Recomendada

RESTRICCIONES:
- Enfocarse en problemas que afecten coordinación
- Priorizar issues de geometría sobre información
- Considerar LOD [NIVEL] como referencia
```

---

## 2. Análisis de Warnings de Revit

**Nivel:** Básico

```
CONTEXTO: Tengo un modelo Revit con múltiples warnings que necesito priorizar para limpieza.

ROL: Actúa como especialista en optimización de modelos Revit.

TAREA: Analiza la siguiente lista de warnings y:
1. Agrúpalos por categoría
2. Identifica los críticos (afectan geometría/exportación IFC)
3. Sugiere orden de resolución
4. Indica cuáles pueden ignorarse temporalmente

WARNINGS:
[Pegar lista de warnings exportada de Revit]

FORMATO:
## Críticos (resolver inmediatamente)
## Importantes (resolver antes de entrega)
## Menores (resolver si hay tiempo)
## Ignorables (no afectan calidad)
```

---

## 3. Validación de Nomenclatura

**Nivel:** Básico

```
CONTEXTO: Necesito validar que los nombres de [vistas/familias/archivos] cumplan con el estándar del proyecto.

ESTÁNDAR DE NOMENCLATURA:
[Describir patrón, ej: PRY-DIS-ZONA-TIPO-NUM]

LISTA A VALIDAR:
[Pegar lista de nombres]

TAREA:
1. Marca cada elemento como ✓ Correcto o ✗ Incorrecto
2. Para los incorrectos, sugiere el nombre correcto
3. Identifica patrones de error comunes

FORMATO: Tabla con: Nombre Actual | Estado | Nombre Sugerido | Nota
```

---

## 4. Sugerencias de Organización de Vistas

**Nivel:** Intermedio

```
CONTEXTO: Estoy organizando el navegador de proyectos de un modelo Revit de [TIPO] con [NÚMERO] vistas.

ROL: Actúa como BIM Manager con experiencia en plantillas de proyecto.

TAREA: Basado en las vistas listadas, sugiere:
1. Estructura de carpetas en el navegador
2. Parámetros de organización recomendados
3. Vistas que podrían eliminarse o consolidarse
4. Vistas faltantes según el tipo de proyecto

VISTAS ACTUALES:
[Pegar lista de vistas]

FORMATO: Árbol de estructura propuesto con justificación
```

---

## 5. Generación de Lista de Verificación de Modelo

**Nivel:** Avanzado

```
CONTEXTO: Necesito crear un checklist de control de calidad para modelos de [DISCIPLINA] en LOD [NIVEL].

ROL: Actúa como consultor BIM especializado en QA/QC.

TAREA: Genera un checklist completo que cubra:
1. Geometría y modelado
2. Información y parámetros
3. Estándares y nomenclatura
4. Coordinación y referencias
5. Exportación y entregables

FORMATO: Checklist con categorías, ítems verificables y criterios de aceptación

RESTRICCIONES:
- Alineado con ISO 19650
- Práctico para revisión en menos de 30 minutos
- Incluir verificaciones automáticas y manuales
```

---

## 6. Descripción de Familia Revit

**Nivel:** Básico

```
CONTEXTO: Necesito documentar una familia Revit para el catálogo del proyecto.

INFORMACIÓN DE LA FAMILIA:
- Nombre: [nombre]
- Categoría: [categoría]
- Tipos: [lista de tipos]
- Parámetros principales: [lista]

TAREA: Genera una descripción técnica que incluya:
1. Descripción general (2-3 oraciones)
2. Casos de uso recomendados
3. Parámetros editables y su función
4. Restricciones o notas importantes

FORMATO: Ficha técnica estructurada
```

---

## 7. Análisis de Complejidad de Modelo

**Nivel:** Avanzado

```
CONTEXTO: Tengo un modelo Revit con problemas de rendimiento y necesito identificar causas.

DATOS DEL MODELO:
- Tamaño de archivo: [MB]
- Número de elementos: [cantidad]
- Warnings: [cantidad]
- Familias in-place: [cantidad]
- Grupos: [cantidad]
- Vínculos: [cantidad]

ROL: Actúa como especialista en optimización de modelos BIM.

TAREA:
1. Identifica posibles causas de lentitud
2. Prioriza acciones de optimización
3. Sugiere métricas objetivo
4. Recomienda estrategia de limpieza

FORMATO: Diagnóstico con plan de acción priorizado
```

---

## Ejemplos de Uso

### Ejemplo: Análisis de Warnings

**Input:**
```
Warnings exportados:
1. Room is not in a properly enclosed region (45 instances)
2. Highlighted walls overlap (12 instances)
3. There are identical instances in the same place (8 instances)
4. Floor and Wall join warning (23 instances)
```

**Output esperado:**
```
## Críticos
- Highlighted walls overlap (12) → Afecta cuantificación y clash
- Identical instances (8) → Duplicados afectan IFC

## Importantes
- Room not enclosed (45) → Afecta áreas y schedules

## Menores
- Floor/Wall join (23) → Cosmético, resolver si hay tiempo
```

---

*Biblioteca BIMAC - www.bimac.io*
