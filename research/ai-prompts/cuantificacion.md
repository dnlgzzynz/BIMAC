# Prompts de Cuantificación (5D)

---

## 1. Análisis de Cantidades Extraídas

**Nivel:** Intermedio

```
CONTEXTO: Extraje cantidades del modelo BIM para [SISTEMA/PARTIDA] y necesito validarlas antes de enviar al área de costos.

DATOS EXTRAÍDOS:
[Pegar tabla de cantidades: elemento, cantidad, unidad, ubicación]

INFORMACIÓN DE REFERENCIA:
- Superficie total del proyecto: [m²]
- Tipo de proyecto: [tipo]
- Fase: [fase]

ROL: Actúa como ingeniero de costos con experiencia en proyectos similares.

TAREA:
1. Identifica cantidades que parecen fuera de rango
2. Calcula ratios por m² para validación
3. Señala posibles errores de modelado o extracción
4. Sugiere verificaciones adicionales

FORMATO: Tabla con análisis + lista de banderas rojas
```

---

## 2. Comparación Presupuesto vs Modelo

**Nivel:** Avanzado

```
CONTEXTO: Necesito comparar las cantidades del presupuesto base contra las del modelo BIM actual.

PRESUPUESTO BASE:
[Pegar partidas con cantidades presupuestadas]

CANTIDADES DEL MODELO:
[Pegar cantidades extraídas del modelo]

TAREA:
1. Mapear partidas del presupuesto con elementos del modelo
2. Calcular variaciones (% y absoluto)
3. Identificar partidas con mayor desviación
4. Clasificar desviaciones por causa probable:
   - Error de modelado
   - Cambio de diseño
   - Diferencia de criterio de medición
   - Omisión en presupuesto

FORMATO: Tabla comparativa + resumen de impacto en costo total

RESTRICCIONES:
- Usar mismas unidades
- Indicar partidas sin equivalente en modelo
```

---

## 3. Generación de Catálogo de Conceptos

**Nivel:** Intermedio

```
CONTEXTO: Necesito generar un catálogo de conceptos para licitación basado en los elementos del modelo BIM.

ELEMENTOS DEL MODELO:
[Pegar lista de categorías y tipos con cantidades]

ESTÁNDAR DE CLASIFICACIÓN: [Uniformat/Masterformat/SINCO]

TAREA:
1. Organiza los elementos en estructura de catálogo
2. Genera descripción de concepto para cada partida
3. Define unidad de medición apropiada
4. Sugiere nivel de desglose (partidas, subpartidas)

FORMATO: Catálogo estructurado listo para presupuesto

RESTRICCIONES:
- Descripciones claras y sin ambigüedad
- Unidades estándar de la industria local
- Incluir notas de lo que incluye/excluye cada concepto
```

---

## 4. Análisis de Variaciones entre Versiones

**Nivel:** Avanzado

```
CONTEXTO: Necesito analizar las diferencias de cantidades entre dos versiones del modelo.

VERSIÓN ANTERIOR ([FECHA]):
[Pegar cantidades v1]

VERSIÓN ACTUAL ([FECHA]):
[Pegar cantidades v2]

TAREA:
1. Calcular delta por partida
2. Identificar partidas nuevas/eliminadas
3. Cuantificar impacto en costo (usar precio unitario si disponible)
4. Asociar cambios con órdenes de cambio o decisiones de diseño conocidas
5. Generar resumen ejecutivo de impacto

FORMATO: Reporte de variaciones con análisis de tendencia

RESTRICCIONES:
- Destacar cambios >10% en cantidad
- Agrupar por sistema o disciplina
```

---

## 5. Validación de Unidades y Criterios de Medición

**Nivel:** Básico

```
CONTEXTO: Necesito verificar que las cantidades extraídas usen las unidades correctas según el estándar del proyecto.

CANTIDADES EXTRAÍDAS:
[Pegar lista con elemento, cantidad, unidad actual]

ESTÁNDAR DE MEDICIÓN DEL PROYECTO:
[Describir criterios o pegar tabla de referencia]

TAREA:
1. Verificar cada unidad contra el estándar
2. Identificar conversiones necesarias
3. Señalar elementos con criterio de medición ambiguo
4. Sugerir correcciones

FORMATO: Tabla con: Elemento | Unidad Actual | Unidad Correcta | Factor de Conversión | Nota
```

---

## 6. Resumen Ejecutivo de Cuantificación

**Nivel:** Intermedio

```
CONTEXTO: Necesito preparar un resumen ejecutivo de cantidades para presentar a [AUDIENCIA].

DATOS COMPLETOS:
[Pegar resumen de cantidades por sistema]

INFORMACIÓN DEL PROYECTO:
- Nombre: [nombre]
- Superficie: [m²]
- Tipo: [tipo]
- Fecha de corte: [fecha]

TAREA: Genera un resumen ejecutivo que incluya:
1. Cantidades clave por sistema (top 10 por impacto)
2. Ratios principales ($/m², kg acero/m², etc.)
3. Comparación con benchmarks de proyectos similares
4. Observaciones y alertas
5. Próximos pasos recomendados

FORMATO: Presentación de 1 página con puntos clave

RESTRICCIONES:
- Lenguaje no técnico para directivos
- Enfocarse en decisiones, no en datos
```

---

## 7. Detección de Duplicados y Sobreposiciones

**Nivel:** Intermedio

```
CONTEXTO: Sospecho que hay elementos duplicados en el modelo que están inflando las cantidades.

INDICADORES:
- Cantidades inusualmente altas en: [partidas]
- Warnings de duplicados en Revit: [número]

DATOS:
[Pegar schedule con ID de elemento, tipo, ubicación, cantidad]

TAREA:
1. Identifica patrones de posibles duplicados
2. Agrupa elementos por ubicación para detectar sobreposiciones
3. Estima el % de inflación por duplicados
4. Sugiere filtros o verificaciones para limpiar

FORMATO: Lista de elementos sospechosos + recomendaciones de limpieza
```

---

## 8. Proyección de Cantidades para Fases Futuras

**Nivel:** Avanzado

```
CONTEXTO: Tengo cantidades de la fase actual y necesito proyectar para fases futuras del proyecto.

CANTIDADES FASE ACTUAL ([NOMBRE]):
[Pegar datos]

INFORMACIÓN DE FASES FUTURAS:
- Fase 2: [descripción, superficie, similitud con fase 1]
- Fase 3: [descripción, superficie, similitud]

TAREA:
1. Analizar patrones de la fase actual
2. Calcular ratios por m² o unidad funcional
3. Proyectar cantidades para fases futuras
4. Indicar nivel de confianza de la proyección
5. Listar supuestos utilizados

FORMATO: Tabla de proyección con rangos (mínimo, esperado, máximo)

RESTRICCIONES:
- Indicar claramente que son estimaciones
- Documentar todos los supuestos
```

---

## Ejemplos de Uso

### Ejemplo: Validación de Cantidades

**Input:**
```
Proyecto: Edificio de oficinas
Superficie: 5,000 m²

Cantidades extraídas:
- Muro de tablaroca: 15,000 m²
- Puertas: 45 pzas
- Plafón: 4,200 m²
```

**Output:**
```
## Análisis de Ratios

| Elemento | Cantidad | Ratio/m² | Benchmark | Status |
|----------|----------|----------|-----------|--------|
| Muros tablaroca | 15,000 m² | 3.0 m²/m² | 2.0-2.5 | ⚠️ Alto |
| Puertas | 45 pzas | 1/111 m² | 1/80-100 | ✓ OK |
| Plafón | 4,200 m² | 0.84 m²/m² | 0.85-0.95 | ✓ OK |

## Banderas Rojas
- **Muros tablaroca**: Ratio 20-50% arriba de benchmark.
  Verificar: ¿Muros dobles contados 2 veces? ¿Incluye acabados?

## Recomendación
Revisar schedule de muros filtrando por tipo para identificar
posible doble conteo.
```

---

*Biblioteca BIMAC - www.bimac.io*
