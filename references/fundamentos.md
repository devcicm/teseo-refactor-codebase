# Fundamentos: la matemática y la filosofía del refactor

Cargar este anexo cuando se necesite JUSTIFICAR una decisión,
resolver un caso borde, o antes de aplicar dominios D, ALG, RES, OBJ.

## §1. El modelo formal

En v2.3 el modelo se descompone para hacer explícito qué debe ser idéntico
y qué puede mejorar:

**C(P)** : Σentrada → Σsalida — contrato funcional observable: respuestas
HTTP, stdout contractual, DOM/ARIA consumido, archivos, storage, eventos,
orden visible, dinero movido y propiedades no funcionales que hayan sido
contratadas explícitamente (p. ej. timeout máximo de una API).

**Q(P)** — sobre de calidad interna/no contractual: consumo accidental de
recursos, complejidad, trabajo redundante, handles fugados y métricas que
no formen parte del contrato externo.

Refactor puro T: **C(T(P)) = C(P)** y **Q(T(P)) ⪯ Q(P)** (no regresión;
mejoras permitidas).
Corolario 1: igualdad de C permite cambiar por completo la estructura.
Corolario 2: mejorar complejidad temporal/espacial es refactor mientras no
filtre cambios hacia C(P).
Corolario 3: si una propiedad de Q era observable/contratada en ese sistema,
se reclasifica dentro de C y exige paridad.



## §1.1. El sistema real incluye un sobre operacional E

Un repositorio no ejecuta en el vacío. Para una ejecución concreta, modela:

`S = Código + E(precondiciones operacionales activas)`

E no es una lista fija. Se deriva de la arquitectura real: puede contener
sustrato de ejecución, toolchain/build, resolución de dependencias,
configuración/rutas, estado durable, OS/filesystem/red, servicios externos,
dispositivos u otras precondiciones demostradas. Dos árboles de código idénticos
pueden comportarse distinto si cambia una de esas dependencias.

Por ello un experimento de paridad válido mantiene **las dimensiones activas de
E** fijas. Si una cambia entre baseline y candidato, primero explica esa deriva;
el test deja de aislar la variable "código refactorizado". Es diseño experimental:
cambia una variable por vez. Casos tecnológicos concretos pertenecen a
`adaptadores.md` y nunca definen el modelo universal.

### Estado roto antes del refactor

Preservar ciegamente un fallo preexistente no equivale a preservar la intención
del sistema. Separa **observación histórica** de **baseline autorizado**:
- el fallo se documenta como incidente y evidencia;
- su causa se investiga sin mezclar cambios de refactor;
- el fix, si procede, vive en changeset independiente;
- el golden master funcional se congela después de recuperar un estado válido,
  o se limita explícitamente a los flujos GREEN que sí son reproducibles.


## §2. El barco de Teseo como protocolo

La pregunta de Teseo (¿sigue siendo el mismo barco si cambio todas
las piezas?) tiene respuesta operativa aquí: el barco ES su función,
no sus tablones. Se mantiene mientras el contrato con el puerto se
cumple.

Protocolo: T se descompone como P₀ → P₁ → ... → Pₙ con verificación
C(Pᵢ) = C(P₀) y Q(Pᵢ) no peor que Q(P₀) en cada paso. La verificación
local es la custodia de la identidad. Consecuencias prácticas:
- Un cambio grande sin verificar equivale a construir otro barco
  al lado y cambiarlo de noche. Eso no es Teseo, es contrabando.
- Si un paso no es verificable, se subdivide hasta que lo sea.
- La cadena documenta la continuidad: cada Pᵢ está a un paso
  verificable del anterior. Así, el final es el barco original
  por inducción, no por fe.

## §3. Deconstrucción: cómo leer una pieza antes de reemplazarla

Para cada unidad candidata (función, módulo, clase), contestar:
1. ENTRA: qué datos y en qué tipos/forma.
2. SALE: qué produce, por qué canal, en qué orden (el orden ES
   semántica si alguien puede observarlo).
3. SUPONE: invariantes que da por sentadas (estado global, formato
   de datos, tiempo disponible).
4. TOCA: qué efectos externos causa y en qué orden.
5. ROMPE: qué consumidor externo se vería afectado si su firma,
   su orden o sus efectos cambian.
Solo se reemplaza una pieza con las 5 respuestas escritas. Las
piezas con respuestas "no sé" en TOCA o ROMPE se deconstruyen más
antes de tocar.

## §4. DRY en cinco niveles (dominio D)

Definición fundacional (Hunt & Thomas): toda pieza de conocimiento
debe tener una única representación autoritaria, inequívoca y
completa dentro del sistema. NOTA: DRY es sobre conocimiento,
NO sobre texto.

Niveles de duplicación, de más profundo a más superficial:
L1 Conocimiento — la misma regla del negocio expresada en formas
   distintas (IVA calculado en frontend y backend con constantes
   separadas: textos distintos, un solo conocimiento).
L2 Responsabilidad — dos módulos que se creen dueños de la misma
   decisión (quién decide el precio final: la vista o el servidor).
L3 Implementación — el mismo algoritmo escrito dos veces
   (fechaDeHoy en 3 archivos).
L4 Abstracción — dos tipos/interfaces que modelan el mismo concepto
   (Money y Precio; Repository y Dao).
L5 Helpers — utilidades de soporte duplicadas (formatMoney y
   formatMoney2).

La herramienta: la PREGUNTA DEL CAMBIO ÚNICO. "Si esta regla de
negocio cambia mañana, ¿cuántos lugares debo tocar?" N > 1 ⇒ hay
N−1 duplicaciones de conocimiento (no de texto).

Contraejemplo CRÍTICO — la duplicación accidental: dos códigos
textualmente similares que expresan conocimientos DISTINTOS (dos
validadores de email similares donde uno valida registro y otro
recuperación de cuenta, con reglas de vida propia). Consolidarlos
acopla dos reglas que evolucionarán por separado y alguien pagará
ese acoplamiento en el futuro. DRY exige unicidad de CONOCIMIENTO,
no de forma. Ante la duda, preguntar: "¿cambiarían juntos, por la
misma razón, en el mismo momento?" Si la respuesta es no → no
consolidar.

## §5. Complejidad (Big O) y paridad

La mejora asintótica (O(n²)→O(n)) es refactor legítimo: [[·]] no
incluye tiempo. EXCEPCIONES — fugas donde la estructura se vuelve
observable (si ocurre una, la paridad se rompe y el paso se revierte):
F1 Orden de iteración: cambiar List→Set/HashMap altera el orden
   visible de salidas si alguien depende de él.
F2 Laziness: evaluar antes/después cambia qué efectos ocurren
   si un flujo corto-circuita.
F3 Timeouts y límites: la operación que ahora cabe en el presupuesto
   de tiempo/recurso puede cambiar qué se completa.
F4 Números de punto flotante: reordenar sumas cambia el resultado
   decimal visible. La aritmética flotante NO es asociativa.
F5 Concurrencia: si el orden observable de efectos depende del
   timing, acelerar puede cambiar el interleaving.

Regla de severidad para ALG: se calcula con los datos REALES del
sistema hoy, no en abstracto. Un O(n²) sobre n=20 ventas es ⚪;
el mismo algoritmo sobre n=2M facturas es 🟠/🔴.

## §6. Recursos y Σ (dominio RES)

Un recurso adquirido y no liberado degrada Q(P) y puede terminar
filtrándose hacia C(P) por agotamiento, timeout o bloqueo. Por eso el
golden master incluye pruebas de no-regresión: contar handles abiertos
(fds, conexiones, locks, suscripciones) tras N operaciones. El resultado
final puede ser MENOR (mejora) pero no MAYOR sin justificación. Si el
conteo/límite es parte de un contrato explícito, entonces pertenece a C(P)
y sí exige igualdad.

La adquisición y la liberación deben ser invariantes ante CUALQUIER
camino de salida, incluidas excepciones. Las estructuras idiomáticas
por lenguaje están en lenguajes.md §recursos.

## §7. Instanciación y sustituibilidad (dominio OBJ)

El antipatrón no es la palabra `new`; es el `new` que COARTA la
evolución: acoplar una pieza a una implementación concreta cuando
el dominio del problema ya anticipa que habrá otra. Criterio de
olor objetivo: "si mañana necesito una implementación distinta
de esta dependencia (test doble, otra fuente de datos, otro
proveedor), ¿puedo inyectarla sin tocar este código?" Si la
respuesta es no, el new está en el lugar equivocado.

CASOS CORRECTOS de new (no tocar):
- Objetos de valor inmutables: new Money(19,99), new Date(), new
  Email("a@b.co"). No hay sustituibilidad que desear: son el concepto.
- DTOs/records sin comportamiento.
- Creación local dentro de la misma unidad de cohesión, sin sustituto
  concebible.
CASO LÍMITE: la clase que crea sus propios colaboradores PERO los
expone para sustitución (constructor parametrizado con default) es
la transición aceptable mínima cuando un contenedor de DI no existe.

## §8. Clases de cambio: frontera del refactor

PURE_REFACTOR preserva C y no degrada Q. COMPATIBLE_EVOLUTION conserva el
contrato anterior pero añade/modifica una ruta nueva mediante compatibilidad.
FIX cambia C para corregir un defecto. FEATURE añade capacidad. MIGRATION
cambia deliberadamente plataforma o contrato. Solo PURE_REFACTOR pertenece
al alcance por defecto de esta skill. La clasificación se hace por OCURRENCIA,
no por ID: el mismo criterio puede ser refactor puro en un lugar y evolución
en otro según qué sea observable.

## §9. Niveles de evidencia

- CONFIRMED: detección objetiva + contexto suficiente + consumidor/efecto
  entendido; puede planearse.
- CANDIDATE: existe olor pero falta demostrar razón de cambio, consumidor,
  tipo, orden u otra precondición; se investiga, no se modifica.
- NOT_APPLICABLE: el criterio fue evaluado y su excepción aplica.

Regla: la ausencia de evidencia NO se convierte en certeza por intuición del
agente. Ante dos interpretaciones razonables, permanece CANDIDATE.
