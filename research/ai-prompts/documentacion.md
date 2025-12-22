# Prompts de Documentación

---

## 1. Redacción de Especificación Técnica

**Nivel:** Intermedio

```
CONTEXTO: Necesito redactar la especificación técnica para [SISTEMA/ELEMENTO] del proyecto.

INFORMACIÓN DEL ELEMENTO:
- Tipo: [descripción]
- Ubicación: [dónde se aplica]
- Cantidad aproximada: [cantidad]
- Referencia de diseño: [marca/modelo base, si aplica]

REQUISITOS DE DESEMPEÑO:
[Listar requisitos funcionales]

ROL: Actúa como especificador técnico senior.

TAREA: Genera una especificación que incluya:
1. Alcance y descripción general
2. Normas de referencia aplicables
3. Materiales y características técnicas
4. Requisitos de desempeño
5. Ejecución e instalación
6. Control de calidad y pruebas
7. Criterios de aceptación

FORMATO: Especificación en formato CSI 3-part

RESTRICCIONES:
- Lenguaje prescriptivo, no descriptivo
- Evitar marcas específicas (o indicar "o equivalente")
- Incluir normas mexicanas/locales cuando aplique
```

---

## 2. Generación de Minuta de Reunión

**Nivel:** Básico

```
CONTEXTO: Necesito documentar la reunión de [TIPO] celebrada el [FECHA].

NOTAS EN BRUTO:
[Pegar notas tomadas durante la reunión]

ASISTENTES:
[Lista de participantes con rol]

TAREA: Genera una minuta formal con:
1. Encabezado (proyecto, fecha, lugar, duración)
2. Lista de asistentes
3. Orden del día
4. Desarrollo de cada punto
5. Acuerdos y compromisos (tabla: acción, responsable, fecha)
6. Temas pendientes
7. Fecha de próxima reunión

FORMATO: Documento formal listo para firma y distribución

RESTRICCIONES:
- Redacción neutral y objetiva
- Compromisos con fecha específica
- Máximo 3 páginas
```

---

## 3. Descripción de Entregable BIM

**Nivel:** Básico

```
CONTEXTO: Necesito redactar la descripción del entregable [NOMBRE] para incluir en la transmisión.

INFORMACIÓN DEL ENTREGABLE:
- Nombre del archivo: [nombre]
- Versión: [versión]
- Fecha: [fecha]
- Formato: [formato]
- Autor: [empresa/persona]

CONTENIDO:
[Describir qué incluye el entregable]

TAREA: Genera una descripción que incluya:
1. Propósito del entregable
2. Contenido y alcance
3. LOD alcanzado
4. Limitaciones y exclusiones
5. Instrucciones de uso
6. Contacto para aclaraciones

FORMATO: Nota de transmisión profesional
```

---

## 4. Resumen Ejecutivo de Proyecto

**Nivel:** Avanzado

```
CONTEXTO: Necesito preparar un resumen ejecutivo del estado del proyecto para [AUDIENCIA].

INFORMACIÓN:
- Proyecto: [nombre]
- Fase actual: [fase]
- Avance general: [%]
- Presupuesto: [ejercido vs autorizado]
- Programa: [días adelanto/atraso]

LOGROS RECIENTES:
[Lista de hitos alcanzados]

PROBLEMAS/RIESGOS:
[Lista de issues principales]

TAREA: Genera un resumen ejecutivo de 1 página que incluya:
1. Estado general (semáforo)
2. Avance físico y financiero
3. Logros del período
4. Problemas y acciones de mitigación
5. Proyección a cierre
6. Decisiones requeridas

FORMATO: Informe ejecutivo visual (describir gráficos sugeridos)

RESTRICCIONES:
- Enfocarse en decisiones, no en datos
- Lenguaje para no-técnicos
- Incluir recomendaciones claras
```

---

## 5. Redacción de RFI (Request for Information)

**Nivel:** Intermedio

```
CONTEXTO: Necesito emitir un RFI para aclarar [TEMA] con el equipo de diseño.

INFORMACIÓN:
- Ubicación: [referencia en planos/modelo]
- Documentos relacionados: [lista]
- Impacto si no se aclara: [descripción]

DUDA/CONFLICTO:
[Describir la inconsistencia o falta de información]

TAREA: Genera un RFI formal con:
1. Número y fecha
2. Asunto claro y conciso
3. Referencia a documentos
4. Descripción detallada del problema
5. Pregunta específica
6. Sugerencia de solución (si aplica)
7. Fecha límite de respuesta

FORMATO: Formulario RFI estándar

RESTRICCIONES:
- Una pregunta principal por RFI
- Incluir capturas/referencias visuales
- Indicar impacto en programa si no se responde a tiempo
```

---

## 6. Narrativa de Memoria Descriptiva

**Nivel:** Avanzado

```
CONTEXTO: Necesito redactar la memoria descriptiva de [DISCIPLINA/SISTEMA] para el proyecto.

INFORMACIÓN TÉCNICA:
[Pegar datos técnicos, especificaciones, criterios de diseño]

TIPO DE PROYECTO: [tipo]
NORMATIVA APLICABLE: [normas]

TAREA: Genera una memoria descriptiva que incluya:
1. Introducción y alcance
2. Normativa y referencias
3. Criterios de diseño
4. Descripción del sistema
5. Componentes principales
6. Especificaciones técnicas clave
7. Consideraciones de construcción
8. Operación y mantenimiento básico

FORMATO: Documento técnico formal

RESTRICCIONES:
- Redacción técnica pero comprensible
- Referenciar planos y cálculos
- Incluir tablas resumen de datos clave
```

---

## 7. Carta de Transmisión de Documentos

**Nivel:** Básico

```
CONTEXTO: Necesito preparar una carta de transmisión para enviar [DOCUMENTOS] al [DESTINATARIO].

DOCUMENTOS A TRANSMITIR:
[Lista con nombre, versión, número de copias]

INFORMACIÓN:
- Proyecto: [nombre]
- Fase: [fase]
- Propósito: [para revisión/aprobación/construcción/información]

TAREA: Genera carta de transmisión con:
1. Encabezado formal
2. Referencia del proyecto
3. Lista de documentos (tabla)
4. Propósito de la transmisión
5. Acciones requeridas del destinatario
6. Fecha límite de respuesta (si aplica)
7. Pie con datos de contacto

FORMATO: Carta formal de una página
```

---

## 8. Texto para Presentación de Proyecto

**Nivel:** Intermedio

```
CONTEXTO: Necesito preparar el texto para una presentación de [DURACIÓN] minutos sobre el proyecto.

AUDIENCIA: [tipo de audiencia]
OBJETIVO: [informar/vender/aprobar/celebrar]

INFORMACIÓN DEL PROYECTO:
[Datos clave del proyecto]

PUNTOS A CUBRIR:
[Lista de temas obligatorios]

TAREA: Genera:
1. Guión de presentación con tiempos por sección
2. Puntos clave por diapositiva (bullets)
3. Notas del presentador
4. Preguntas anticipadas y respuestas sugeridas

FORMATO: Guión estructurado por diapositiva

RESTRICCIONES:
- Mensajes claros y memorables
- Datos duros limitados (máx 3 por slide)
- Incluir "hooks" para mantener atención
```

---

## Ejemplos de Uso

### Ejemplo: RFI

**Input:**
```
Ubicación: Plano A-401, Detalle 5
Problema: El detalle muestra ventana de 1.20m pero en
planta aparece de 1.50m. ¿Cuál es la dimensión correcta?
```

**Output:**
```
# REQUEST FOR INFORMATION (RFI)

**RFI No.:** PRY-ARQ-015
**Fecha:** [fecha]
**Proyecto:** [nombre]
**De:** Constructora XYZ
**Para:** Arquitecto de Proyecto

## Asunto
Inconsistencia en dimensión de ventana - Nivel 4

## Referencias
- Plano A-401, Detalle 5
- Plano A-201, Planta Nivel 4

## Descripción
Se detectó inconsistencia en la dimensión de ventana V-12
del Nivel 4, fachada norte:
- Detalle 5 (A-401): Ancho = 1.20 m
- Planta arquitectónica (A-201): Ancho = 1.50 m

## Pregunta
¿Cuál es la dimensión correcta del ancho de la ventana V-12?

## Sugerencia
Verificar con catálogo de cancelería seleccionado.

## Impacto
Requerimos respuesta antes del [fecha] para no afectar
fabricación de marcos (ruta crítica).

**Fecha límite de respuesta:** [fecha + 5 días]
```

---

*Biblioteca BIMAC - www.bimac.io*
