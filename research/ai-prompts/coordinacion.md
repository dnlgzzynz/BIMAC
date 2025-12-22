# Prompts de Coordinación BIM

---

## 1. Clasificación de Interferencias

**Nivel:** Intermedio

```
CONTEXTO: Acabo de correr un clash detection en Navisworks entre [DISCIPLINA A] y [DISCIPLINA B] y obtuve [NÚMERO] interferencias.

ROL: Actúa como coordinador BIM senior.

TAREA: Basado en la siguiente lista de clashes, clasifícalos en:
1. Críticos - Requieren cambio de diseño
2. Mayores - Requieren coordinación inmediata
3. Menores - Pueden resolverse en campo
4. Falsos positivos - Ignorar o ajustar tolerancia

LISTA DE CLASHES:
[Pegar exportación de clash report: elementos involucrados, distancia, ubicación]

FORMATO: Tabla agrupada por clasificación con justificación breve

CRITERIOS:
- Crítico: Afecta estructura, seguridad o función principal
- Mayor: Requiere modificación de más de una disciplina
- Menor: Ajuste local de una disciplina
- Falso positivo: Tolerancia de construcción, secuencia de obra
```

---

## 2. Redacción de Issue BCF

**Nivel:** Básico

```
CONTEXTO: Necesito crear un issue BCF claro y accionable para el siguiente conflicto.

INFORMACIÓN DEL CLASH:
- Elementos: [Elemento A] vs [Elemento B]
- Ubicación: [Nivel, Zona, Coordenadas]
- Distancia/Penetración: [valor]
- Disciplinas: [A] vs [B]

TAREA: Redacta un issue BCF con:
1. Título conciso (máx 10 palabras)
2. Descripción clara del problema
3. Sugerencia de solución
4. Asignación recomendada

FORMATO:
**Título:**
**Prioridad:** [Crítico/Mayor/Menor]
**Asignado a:** [Disciplina]
**Descripción:**
**Solución propuesta:**
```

---

## 3. Análisis de Impacto de Cambios

**Nivel:** Avanzado

```
CONTEXTO: Se propone el siguiente cambio de diseño en el proyecto:
[Describir cambio propuesto]

ROL: Actúa como director de coordinación BIM.

TAREA: Analiza el impacto del cambio en:
1. Otras disciplinas afectadas
2. Documentación que requiere actualización
3. Cronograma (estimación de retrasos)
4. Costos potenciales (orden de magnitud)
5. Riesgos asociados

INFORMACIÓN DEL PROYECTO:
- Fase actual: [fase]
- Disciplinas involucradas: [lista]
- Fecha de entrega: [fecha]

FORMATO: Análisis estructurado con recomendación de proceder/no proceder
```

---

## 4. Resumen de Sesión de Coordinación

**Nivel:** Intermedio

```
CONTEXTO: Acabo de terminar una sesión de coordinación BIM de [DURACIÓN] con [NÚMERO] participantes.

NOTAS DE LA REUNIÓN:
[Pegar notas en bruto]

TAREA: Genera un acta estructurada con:
1. Resumen ejecutivo (3-5 puntos clave)
2. Issues discutidos y estado
3. Acuerdos tomados
4. Acciones asignadas (quién, qué, cuándo)
5. Temas pendientes para siguiente sesión

FORMATO: Acta formal lista para distribución

RESTRICCIONES:
- Lenguaje profesional y neutral
- Acciones con responsable y fecha clara
- Máximo 2 páginas
```

---

## 5. Priorización de Issues Pendientes

**Nivel:** Intermedio

```
CONTEXTO: Tengo [NÚMERO] issues BCF abiertos y necesito priorizarlos para la próxima semana.

LISTA DE ISSUES:
[Pegar lista con: ID, título, disciplina asignada, fecha creación, descripción breve]

CRITERIOS DE PRIORIZACIÓN:
- Impacto en ruta crítica
- Dependencias entre disciplinas
- Facilidad de resolución
- Fecha de entrega más cercana

TAREA:
1. Ordena los issues por prioridad
2. Agrupa por disciplina responsable
3. Identifica dependencias entre issues
4. Sugiere issues que pueden cerrarse juntos

FORMATO: Lista priorizada con justificación
```

---

## 6. Análisis de Tendencias de Coordinación

**Nivel:** Avanzado

```
CONTEXTO: Quiero analizar el desempeño de coordinación del proyecto en las últimas [N] semanas.

DATOS:
- Semana 1: [X] issues creados, [Y] cerrados
- Semana 2: [X] issues creados, [Y] cerrados
[...]

DISTRIBUCIÓN POR DISCIPLINA:
- ARQ: [%]
- EST: [%]
- MEP: [%]

TAREA: Genera un análisis que incluya:
1. Tendencia general (mejorando/empeorando)
2. Disciplinas con más issues recurrentes
3. Tiempo promedio de resolución
4. Predicción para próximas semanas
5. Recomendaciones de mejora

FORMATO: Reporte ejecutivo con gráficos sugeridos (describir tipo de gráfico)
```

---

## 7. Matriz de Responsabilidades de Clash

**Nivel:** Básico

```
CONTEXTO: Necesito definir quién es responsable de resolver cada tipo de interferencia entre disciplinas.

DISCIPLINAS DEL PROYECTO:
[Lista de disciplinas]

TAREA: Genera una matriz de responsabilidad que indique:
1. Para cada combinación de disciplinas, quién lidera la resolución
2. Criterios para determinar responsabilidad
3. Escalamiento cuando no hay acuerdo

FORMATO: Matriz con disciplinas en filas y columnas + notas de criterio
```

---

## 8. Preparación de Reunión de Coordinación

**Nivel:** Intermedio

```
CONTEXTO: Debo preparar la agenda para la reunión de coordinación semanal.

ESTADO ACTUAL:
- Issues abiertos: [número por disciplina]
- Issues críticos: [lista]
- Entregables próximos: [lista con fechas]
- Temas pendientes de reunión anterior: [lista]

TAREA: Genera:
1. Agenda estructurada con tiempos
2. Lista de participantes requeridos por tema
3. Documentos/modelos a revisar
4. Preguntas clave a resolver
5. Decisiones necesarias

FORMATO: Agenda lista para enviar por correo
```

---

## Ejemplos de Uso

### Ejemplo: Issue BCF

**Input:**
```
Clash: Ducto de HVAC 600x400mm atraviesa viga IPR 400x200
Ubicación: Nivel 3, Eje C-5, Cuarto de máquinas
Penetración: 150mm
```

**Output:**
```
**Título:** Ducto HVAC penetra viga estructural Eje C-5 N3

**Prioridad:** Crítico

**Asignado a:** MEP (Mecánico)

**Descripción:**
Ducto de suministro de aire (600x400mm) del sistema HVAC
atraviesa viga IPR 400x200 en el cuarto de máquinas del
Nivel 3, cerca del eje C-5. Penetración de 150mm.

**Solución propuesta:**
Redirigir ducto por debajo de viga, verificando altura libre
mínima de 2.40m. Alternativa: Consultar con estructural si
es posible perforación con refuerzo (poco probable dado
tamaño de ducto vs viga).
```

---

*Biblioteca BIMAC - www.bimac.io*
