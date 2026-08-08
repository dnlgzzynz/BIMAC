# Workflow de Diseño - Cubierta Orgánica de Museo

## Diagrama de Flujo General

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           WORKFLOW DE DISEÑO                                 │
└─────────────────────────────────────────────────────────────────────────────┘

     ┌──────────────┐
     │   INICIO     │
     └──────┬───────┘
            │
            ▼
┌───────────────────────┐
│  1. DEFINIR PARÁMETROS │
│  - Ancho: 15m          │
│  - Largo: 26m          │
│  - Altura: 8.5m        │
│  - Tensión: 0.65       │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  2. GENERAR GEOMETRÍA │
│  - Curvas guía         │
│  - Superficie Loft     │
│  - Subdivisión         │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  3. VALIDAR ESTRUCTURA│◄───────────────┐
│  - Luz libre ≤ 15m    │                │
│  - Pendiente ≥ 2%     │                │
│  - Continuidad        │                │
└───────────┬───────────┘                │
            │                            │
            ▼                            │
      ┌─────────────┐                    │
      │  ¿VÁLIDO?   │───── NO ──────────►│
      └─────┬───────┘     (Ajustar)      │
            │ SÍ                          │
            ▼                             │
┌───────────────────────┐                │
│  4. PANELIZAR         │                │
│  - Grid U×V           │                │
│  - Racionalizar       │                │
│  - Clasificar tipo    │                │
└───────────┬───────────┘                │
            │                            │
            ▼                            │
┌───────────────────────┐                │
│  5. CALCULAR COSTOS   │◄───────────────┘
│  - Por tipo de panel  │
│  - Estructura 25%     │
│  - Instalación 15%    │
└───────────┬───────────┘
            │
            ▼
      ┌─────────────┐
      │  ¿CUMPLE    │───── NO ──────────► Optimizar
      │ PRESUPUESTO?│
      └─────┬───────┘
            │ SÍ
            ▼
┌───────────────────────┐
│  6. EXPORTAR A REVIT  │
│  - Adaptive Components│
│  - Parámetros BIM     │
│  - Schedules          │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  7. DOCUMENTACIÓN     │
│  - Planos fabricación │
│  - Reportes costos    │
│  - IFC export         │
└───────────┬───────────┘
            │
            ▼
     ┌──────────────┐
     │     FIN      │
     └──────────────┘
```

---

## Fases del Workflow

### Fase 1: Definición de Parámetros

**Objetivo:** Establecer las variables de diseño iniciales.

**Inputs:**
| Parámetro | Slider GH | Rango | Default |
|-----------|-----------|-------|---------|
| Ancho_Museo | Number Slider | 10-18 m | 15 m |
| Largo_Museo | Number Slider | 20-30 m | 26 m |
| Altura_Cenit | Number Slider | 6-12 m | 8.5 m |
| Tension_Curva | Number Slider | 0-1 | 0.65 |

**Acciones:**
1. Ajustar sliders en Grasshopper
2. Verificar preview de curvas guía
3. Confirmar dimensiones con cliente

---

### Fase 2: Generación de Geometría

**Objetivo:** Crear la superficie base de la cubierta.

**Componentes GH:**
```
[Curve] Curva Base Inferior
    ↓
[Curve] Curva Cenit Superior
    ↓
[Loft] Superficie Principal
    ↓
[Rebuild] Reconstruir con 50 puntos
```

**Verificaciones:**
- [ ] Superficie continua (sin huecos)
- [ ] Curvatura suave (sin pliegues)
- [ ] Orientación correcta (normal hacia arriba)

---

### Fase 3: Validación Estructural

**Objetivo:** Asegurar que la geometría cumple restricciones.

**Script:** `structural_validator.py`

**Validaciones:**
| Check | Límite | Acción si falla |
|-------|--------|-----------------|
| Luz libre | ≤ 15m | Reducir ancho o agregar apoyo |
| Pendiente | ≥ 2% | Aumentar altura cenit |
| Continuidad | Sin gaps | Regenerar superficie |

**Output esperado:**
```
[OK] Luz Libre Máxima
     Luz: 7.50m / Máx: 15.0m (Margen: 7.50m)

[OK] Pendiente Mínima (Drenaje)
     Pendiente mín: 3.25% / Requerida: 2.0%

[OK] Continuidad de Superficie
     Superficie continua
```

---

### Fase 4: Panelización

**Objetivo:** Subdividir superficie en paneles fabricables.

**Componentes GH:**
```
[Lunchbox: Quad Panel]
    U Count: 13
    V Count: 10
        ↓
[Pufferfish: Panel Planarize]
    Tolerance: 5mm
        ↓
[Python: curvature_analyzer.py]
    → flat_panels
    → single_curve
    → double_curve
```

**Distribución óptima:**
- 78% Paneles planos
- 18% Curvatura simple
- 4% Doble curvatura

---

### Fase 5: Cálculo de Costos

**Objetivo:** Estimar costo total y verificar presupuesto.

**Script:** `cost_calculator.py`

**Inputs:**
- flat_panels (de Fase 4)
- single_curve (de Fase 4)
- double_curve (de Fase 4)
- budget: 280,000 MXN

**Output esperado:**
```
COSTO TOTAL PROYECTO:  $257,400.00 MXN
Presupuesto:           $280,000.00 MXN
Margen:                 $22,600.00 MXN (8.1%)

ESTADO: [OK] DENTRO DE PRESUPUESTO
```

---

### Fase 6: Exportación a Revit

**Objetivo:** Transferir geometría a modelo BIM.

**Requisitos:**
- Rhino.inside.Revit activo
- Familia `Cubierta_Panel_Adaptive.rfa` cargada
- Proyecto Revit abierto

**Script:** `revit_exporter.py`

**Parámetros transferidos:**
| Parámetro Revit | Valor |
|-----------------|-------|
| BIMAC_PanelType | flat / single_curve / double_curve |
| BIMAC_TotalCost | Costo calculado |
| BIMAC_Material | Tipo de policarbonato |
| BIMAC_PanelID | PANEL-0001, PANEL-0002, ... |

---

### Fase 7: Documentación

**Objetivo:** Generar entregables finales.

**Entregables:**

1. **Schedules de Revit**
   - Listado de paneles por tipo
   - Resumen de costos
   - Cantidades de material

2. **Exportación IFC**
   - Configuración: BIMAC_IFC4_COBie
   - Property sets incluidos

3. **Reportes**
   - PDF de análisis de costos
   - Excel con desglose por panel
   - BCF con observaciones

---

## Iteraciones de Optimización

### Si excede presupuesto:

```
Estrategia 1: Aumentar módulo de panel
  - De 2.0×1.5m a 2.5×2.0m
  - Reduce cantidad de paneles
  - Ahorro estimado: 15%

Estrategia 2: Simplificar curvatura
  - Aumentar tolerancia de planarización
  - Convertir doble curva → curva simple
  - Ahorro estimado: 8%

Estrategia 3: Material alternativo
  - PETG en lugar de policarbonato
  - Ahorro estimado: 20%
```

### Si no cumple luz libre:

```
Opción 1: Reducir ancho
  - Slider Ancho_Museo: 15m → 12m
  - Verificar proporciones

Opción 2: Agregar apoyo intermedio
  - Columna central cada 12m
  - Actualizar modelo estructural

Opción 3: Cambiar tipología
  - De cubierta libre a segmentada
  - Múltiples módulos de 12m
```

---

## Tiempos Estimados por Fase

| Fase | Duración | Dependencias |
|------|----------|--------------|
| 1. Parámetros | 15 min | Cliente |
| 2. Geometría | 30 min | Fase 1 |
| 3. Validación | 10 min | Fase 2 |
| 4. Panelización | 20 min | Fase 3 |
| 5. Costos | 10 min | Fase 4 |
| 6. Revit | 45 min | Fase 5 |
| 7. Documentación | 60 min | Fase 6 |
| **TOTAL** | **~3 horas** | |

---

## Checklist de Entrega

### Pre-entrega:
- [ ] Todas las validaciones pasadas
- [ ] Costo dentro de presupuesto
- [ ] Sin warnings en Grasshopper
- [ ] Modelo Revit sincronizado

### Entregables:
- [ ] Archivo `.gh` definitivo
- [ ] Modelo `.rvt` con schedules
- [ ] Exportación `.ifc`
- [ ] Reporte de costos `.pdf`
- [ ] Desglose `.xlsx`

### Documentación:
- [ ] README actualizado
- [ ] Parámetros documentados
- [ ] Changelog actualizado
