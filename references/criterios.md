# Catálogo de criterios de refactorización

> v2.2 — Los 77 IDs se preservan sin cambios. Los gates de arquitectura AS-IS,
> salud pre-refactor y compatibilidad E(P) son **precondiciones transversales**,
> no criterios adicionales; por eso no alteran numeración ni estadísticas.


Leyenda de severidad (qué pasa si NO se arregla):
🔴 crítica · 🟠 alta · 🟡 media · ⚪ baja
Leyenda de riesgo (qué puede romperse si SE arregla):
🟢 bajo · 🟡 medio · 🔴 alto (requiere capa de compatibilidad)

Regla de uso: un criterio solo aplica si su detección es objetiva.
Ante duda, se registra como CANDIDATE con la duda explícita, no como
CONFIRMED. Además, cada OCURRENCIA se clasifica como PURE_REFACTOR,
COMPATIBLE_EVOLUTION, FIX, FEATURE o MIGRATION. La severidad del smell no
autoriza por sí sola a ejecutar un cambio que altere C(P).

## Matriz de priorización (v1.0.1 — corrige un hueco de v1.0)

| Prioridad | Condición | Acción |
|---|---|---|
| P1 | sev 🔴/🟠 · riesgo 🟢 | Hacer primero. Cambio de alto valor y bajo peligro, verificable por inspección |
| P2 | sev 🔴/🟠 · riesgo 🟡/🔴 | Con verificación de paridad estricta. Si el riesgo es 🔴, exige capa de compatibilidad |
| P3 | sev 🟡/⚪ · riesgo 🟢/🟡 | Al final; agrupable en pasos mecánicos por dominio |
| P4 | sev 🟡/⚪ · riesgo 🔴 | Documentar y omitir: queda en el reporte como recomendación, no se ejecuta |

Corrección respecto a v1.0: la columna "riesgo 🟡" no tenía celda
propia y caía ambigua entre P2 y P3. Queda resuelta arriba: riesgo
medio siempre acompaña a su severidad.

### Gate de ejecución v2.1

La matriz P1–P4 prioriza VALOR/RIESGO, no define si un cambio es refactor.
Después de priorizar se aplica el gate de clase:

`CONFIRMED ∧ PURE_REFACTOR` → ejecutable por esta skill.
Cualquier otra combinación → documentar/separar, salvo autorización
explícita de un alcance distinto.

Guardas conocidas:
- **FE-14**: `==`→`===` solo es PURE_REFACTOR si se demuestra equivalencia
  de tipos/valores para el dominio observado; si cambia casos aceptados, FIX.
- **FE-18**: cambiar generación de IDs solo es puro si el ID no sale de la
  frontera ni participa en persistencia, URLs, claves, orden o fixtures.
- **BE-05/06/08/09/10**: modernización HTTP/rutas suele ser
  COMPATIBLE_EVOLUTION o MIGRATION; una ruta/alias viejo debe conservarse si
  se autoriza evolución compatible.
- **BE-17/19**: hardening que modifica quién accede o qué error recibe el
  cliente cambia C(P); clasificar como FIX/COMPATIBLE_EVOLUTION, no ocultarlo
  bajo la etiqueta refactor.
- **RES-01..05**: una mejora de recursos es válida si C(P) permanece igual y
  Q(P) mejora/no regresa.

---

## A. Núcleo (stack-agnostic)

Nota v2.0: N-01 (duplicación) fue RETIRADO y migrado al dominio D
(D-03), que lo subsume con el modelo de conocimiento de 5 niveles.
Los IDs retirados no se reutilizan.

| ID | Smell → Refactor | Sev | Riesgo |
|---|---|---|---|
| N-02 | Valores mágicos sin nombre (0.16, 5, rutas) → constantes nombradas o config | 🟡 | 🟢 |
| N-03 | Archivos duplicados/sufijos (v2, final, copia) → consolidar; elegir el vigente por evidencia de uso | 🟠 | 🟡 |
| N-04 | Comentarios de miedo ("no borrar", "no sé por qué") → resolver la causa o convertir en decisión documentada | 🟡 | 🟡 |
| N-05 | Config/URLs/credenciales hardcodeadas → config + variables de entorno + .env.example (secrets JAMÁS al repo) | 🔴 | 🟢 |
| N-06 | Capas cruzadas (UI conoce persistencia; rutas hacen I/O de datos) → dependencias unidireccionales UI→lógica→datos | 🟠 | 🟡 |
| N-07 | Funciones de responsabilidad múltiple (valida+pinta+guarda) → una responsabilidad por función | 🟡 | 🟡 |
| N-08 | Convención de nombres rota (mezcla idiomas, estilos) → convención única documentada | ⚪ | 🟢 |
| N-09 | Estado global mutable compartido entre módulos → encapsular y exponer acceso controlado | 🟠 | 🟡 |
| N-10 | Código comentado "por si acaso" → eliminar (git es el archivo muerto) | ⚪ | 🟢 |
| N-11 | Condiciones que no pueden darse, `if(x==true)`, comparaciones redundantes → simplificar | ⚪ | 🟢 |

Excepciones N-04: si el workaround protege un caso real desconocido,
el refactor es extraerlo como decisión consciente (constante, guard
nombrado), no eliminarlo.

## B. Frontend

### Estructura y módulos

| ID | Smell → Refactor | Sev | Riesgo |
|---|---|---|---|
| FE-01 | Scripts globales sin módulos, estado en window/vars globales → ES modules (import/export) | 🟠 | 🟡 |
| FE-02 | Archivo cajón con responsabilidades mezcladas → módulos por dominio | 🟡 | 🟡 |
| FE-03 | Orden de carga de scripts frágil (depende del orden en cada HTML) → dependencias explícitas vía import | 🟠 | 🟡 |
| FE-04 | Detección de página por existencia de elementos (`if (el == null) return`) → un entry point por página | 🟡 | 🟡 |

### HTML semántico y accesibilidad

| ID | Smell → Refactor | Sev | Riesgo |
|---|---|---|---|
| FE-05 | Etiquetas deprecated (`font`, `center`, `marquee`, `b` para énfasis) → CSS + semántica real | ⚪ | 🟢 |
| FE-06 | divitis / falta de landmarks → `header`, `nav`, `main`, `table` con `th`/`caption`, formularios con `label` | 🟡 | 🟢 |
| FE-07 | Estilos inline repetidos en elementos → clases; los inline restantes solo si son dinámicos | 🟡 | 🟢 |
| FE-08 | Formularios sin `label`, sin `name`, sin atributos de tipo correctos → reparar semántica | 🟡 | 🟢 |

### CSS

| ID | Smell → Refactor | Sev | Riesgo |
|---|---|---|---|
| FE-09 | Cascada rota a fuerza de `!important` → eliminar causa: una hoja de origen, orden documentado, specificity sana | 🟡 | 🟡 |
| FE-10 | Múltiples hojas que se pisan → consolidar en una + tokens (variables CSS para colores/medidas) | 🟡 | 🟡 |
| FE-11 | Reglas muertas o vacías → eliminar | ⚪ | 🟢 |
| FE-12 | Layout con floats + anchos px fijos → flex/grid + unidades relativas; verificar en viewport angosto | 🟡 | 🟡 |

### JavaScript

| ID | Smell → Refactor | Sev | Riesgo |
|---|---|---|---|
| FE-13 | `var` generalizado → `const` por defecto, `let` solo si hay reasignación | 🟡 | 🟢 |
| FE-14 | `==` / `!=` → `===` / `!==` | 🟠 | 🟢 |
| FE-15 | `innerHTML` con datos concatenados → `textContent`, `createElement` o escape (XSS) | 🔴 | 🟡 |
| FE-16 | Handlers inline (`onclick=`) → `addEventListener` o delegación de eventos | 🟡 | 🟡 |
| FE-17 | `location.reload()` como estrategia de refresco de UI → función render idempotente | 🟡 | 🟡 |
| FE-18 | IDs débiles (`Math.random`, `Date.now` puro) → `crypto.randomUUID()` o contador con semilla persistente | 🟠 | 🟢 |
| FE-19 | `JSON.parse(storage.getItem(...))` sin manejo de null/corrupto → lectura con default + try/catch | 🟠 | 🟢 |
| FE-20 | Esperas temporales para "ya cargó" (`setTimeout` tras onload) → eventos correctos (`DOMContentLoaded`, `defer`) | 🟡 | 🟡 |
| FE-21 | try/catch vacío o que no puede atrapar el error real → manejo real del error o eliminar el catch | 🟠 | 🟡 |
| FE-22 | Estado duplicado sin fuente de verdad (localStorage + API a la vez) → una fuente de verdad + estrategia de caché explícita | 🔴 | 🔴 |
| FE-23 | Datos sin normalizar en el borde (precio string/number mezclados) → parseo único al ingresar, tipos consistentes después | 🟠 | 🟡 |
| FE-24 | Peticiones síncronas bloqueantes (XHR async=false) → fetch async con estados de error visibles | 🟠 | 🟡 |

Excepciones:
- FE-14: un `x == null` deliberado (cubre null y undefined) se respeta
  y se documenta. Para cualquier otro `==`, primero demuestra que coerción y
  comparación estricta coinciden sobre el dominio; si no, no es refactor puro.
- FE-13: cuidado con `var` en closures dentro de loops: el cambio
  mecánico a `let` CAMBIA comportamiento (a veces arregla un bug:
  eso va a BUGS-DETECTADOS.md, no se arregla en silencio).
- FE-18: si el identificador cruza la frontera del módulo, su forma/orden puede
  ser contrato. `crypto.randomUUID()` no se sustituye mecánicamente.

## C. Backend

### Arquitectura

| ID | Smell → Refactor | Sev | Riesgo |
|---|---|---|---|
| BE-01 | Monolito de rutas con lógica inline → capas: routes / controllers / services / repositories | 🟠 | 🟡 |
| BE-02 | Reglas de negocio en handlers → servicios puros testeables | 🟡 | 🟡 |
| BE-03 | Acceso a datos disperso y repetido → repositorio único por entidad | 🟡 | 🟡 |
| BE-04 | Utilidades copiadas del frontend → módulo compartido o paquete interno (nunca copiar) | 🟡 | 🟢 |

### Diseño de API

| ID | Smell → Refactor | Sev | Riesgo |
|---|---|---|---|
| BE-05 | Errores con HTTP 200 + `ok:false` → códigos correctos (4xx/5xx) + body de error uniforme | 🟠 | 🔴 |
| BE-06 | Verbos inventados (`POST /borrarProducto`) → REST + alias deprecado que mantiene el contrato viejo | 🟡 | 🔴 |
| BE-07 | Endpoint omnicanal (`/api/todo` con switch de acción) → eliminar tras verificar consumidores | 🟠 | 🔴 |
| BE-08 | Contrato sin versión → `/api/v1/...` con la ruta vieja como alias | 🟡 | 🔴 |
| BE-09 | GET que muta estado → POST + documentar el cambio de contrato | 🟠 | 🔴 |
| BE-10 | Naming inconsistente de rutas → convención única (recurso plural) | ⚪ | 🔴 |

### Persistencia

| ID | Smell → Refactor | Sev | Riesgo |
|---|---|---|---|
| BE-11 | I/O bloqueante en handlers (readFileSync por request) → async + lectura con caché si procede | 🟠 | 🟡 |
| BE-12 | Escritura sin manejo de error / no segura → escritura atómica o motor real; si es archivo: temp + rename | 🔴 | 🟡 |
| BE-13 | Datos inconsistentes en el "esquema" → validación al escribir + migración/normalización al leer | 🟠 | 🟡 |
| BE-14 | Cálculo de negocio duplicado cliente/servidor → servidor como autoridad única | 🟠 | 🟡 |
| BE-15 | Arranque que muere ante archivo faltante sin mensaje útil → fail-fast con diagnóstico claro | 🟡 | 🟢 |

### Seguridad

| ID | Smell → Refactor | Sev | Riesgo |
|---|---|---|---|
| BE-16 | Credenciales, tokens o llaves en el código → leer de config/env. La ROTACIÓN de un valor ya comprometido es un fix (va a BUGS con urgencia), la extracción a env es refactor | 🔴 | 🟢 |
| BE-17 | CORS permisivo (`*` en origen o en headers) → orígenes y headers explícitos por config; los consumidores conocidos deben seguir funcionando (verificar contra golden master) | 🔴 | 🔴 |
| BE-18 | Autenticación desactivada o comentada (middleware fuera) → el refactor NO la habilita (cambiaría comportamiento); se documenta la decisión y se registra en BUGS con urgencia alta | 🔴 | 🔴 |
| BE-19 | Respuestas que filtran interioridades (stack traces, `err` completo, rutas del servidor) → mensaje controlado al cliente + detalle completo en log interno | 🟠 | 🟡 |

Excepciones/guardas de seguridad:
- BE-16: si el valor comprometido ya está versionado en git, la extracción no
  basta — la rotación es FIX urgente y va en changeset separado.
- BE-17: restringir CORS altera clientes aceptados; por defecto no es
  PURE_REFACTOR aunque sea una mejora de seguridad.
- BE-19: ocultar detalles que hoy recibe el cliente cambia el body observable;
  clasificar como FIX o evolución compatible y verificar consumidores.

### Errores y logging

| ID | Smell → Refactor | Sev | Riesgo |
|---|---|---|---|
| BE-20 | `console.log` como única observabilidad + mensajes de debug muertos ("ignorar este") → logger con niveles; los mensajes existentes se conservan en su nivel correspondiente | 🟡 | 🟢 |
| BE-21 | try/catch vacío o que traga el error → registrar con contexto y propagar al handler central | 🟠 | 🟡 |
| BE-22 | Formato de error inventado handler por handler → error handler central con contrato único (apoya BE-05) | 🟡 | 🟡 |

---

## D. DRY — unicidad de conocimiento

| ID | Smell → Refactor | Sev | Riesgo |
|---|---|---|---|
| D-01 | Conocimiento de negocio en ≥2 lugares (pregunta del cambio único falla) → una representación autoritaria única, los demás puntos la consumen | 🟠 | 🟡 |
| D-02 | Responsabilidad repartida: ≥2 módulos deciden sobre el mismo asunto → un dueño único de la decisión | 🟠 | 🔴 |
| D-03 | Implementación del mismo algoritmo en ≥2 archivos → módulo único compartido | 🟡 | 🟢 |
| D-04 | Dos abstracciones para el mismo concepto → una; el nombre gana por evidencia de uso | 🟡 | 🟡 |
| D-05 | Helpers/utilidades duplicados → módulo utilitario único | 🟡 | 🟢 |
| D-06 | Duplicación ACCIDENTAL consolidada indebidamente (dos formas iguales, conocimientos distintos) → separar; es falsa duplicación | 🟠 | 🟡 |

D-02 con riesgo 🔴 porque mover una responsabilidad cambia quién responde
cuando la decisión se toma en el borde entre módulos: requiere capa de
compatibilidad o verificación exhaustiva de los flujos que cruzan ese
borde. D-06 es el criterio INVERSO de DRY: castiga la consolidación
prematura, no la duplicación. Se detecta pidiendo el historial de
cambios o preguntando por las razones de vida de cada copia.

## ALG. Complejidad algorítmica (ver fundamentos.md §5)

| ID | Smell → Refactor | Sev | Riesgo |
|---|---|---|---|
| ALG-01 | Búsqueda lineal O(n) por clave donde existe acceso O(1)/O(log n) (Map, índice, diccionario) → estructura indexada | calculada con datos reales | 🟡 |
| ALG-02 | Bucles anidados evitables: O(n²) que un índice convierte en O(n) | ídem | 🟡 |
| ALG-03 | Invariante recalculado dentro del bucle → hoisting fuera del ciclo | 🟡 | 🟢 |
| ALG-04 | Estructura de datos inadecuada al patrón de acceso (lista para búsquedas, diccionario para recorridos ordenados) → estructura correcta | 🟡 | 🔴 |
| ALG-05 | Copias completas de colecciones en iteración → vistas/streams/iteradores | 🟡 | 🟡 |

La columna de severidad de ALG-01/02 se LLENA durante la auditoría con
el volumen real: se estima n actual y el crecimiento previsto, y se
asigna ⚪ (n pequeño y estable), 🟡 (n creciente), 🟠 (degrada la
experiencia observable hoy), 🔴 (impide operar con datos reales).
Riesgo 🔴 en ALG-04: cambiar estructura de datos altera orden de
iteración (fuga F1) — verificar paridad de orden en salidas.

## RES. Recursos y ciclo de vida (ver fundamentos.md §6)

| ID | Smell → Refactor | Sev | Riesgo |
|---|---|---|---|
| RES-01 | Recurso adquirido sin liberación garantizada ante excepciones → try/finally, with, using, defer, RAII, finally | 🔴 | 🟡 |
| RES-02 | Liberación dispersa en manos del llamador → ciclo de vida encapsulado en el dueño del recurso | 🟠 | 🟡 |
| RES-03 | Adquisición por iteración de recurso reutilizable (conexión/reader por ciclo) → adquisición única y reutilización | 🟠 | 🟡 |
| RES-04 | Limpieza confiada a finalizer/destructor no determinista → liberación determinista explícita | 🟠 | 🟡 |
| RES-05 | Suscripciones/listeners/temporizadores sin cancelación al morir el dueño → registro + baja en el mismo lugar | 🟠 | 🟡 |

Verificación obligatoria de todo paso RES: prueba de no-regresión del
golden master tras N operaciones. `final <= baseline` es aceptable para
recursos internos comparables; si el recurso es contrato explícito, exige
la condición exacta definida para C(P).

## OBJ. Instanciación y sustituibilidad (ver fundamentos.md §7)

| ID | Smell → Refactor | Sev | Riesgo |
|---|---|---|---|
| OBJ-01 | `new` de dependencia concreta dentro de lógica de negocio → inyección por parámetro, factory o contenedor | 🟠 | 🟡 |
| OBJ-02 | Selección de comportamiento por if/switch sobre tipo → polimorfismo: jerarquía o strategy, una rama por clase | 🟡 | 🟡 |
| OBJ-03 | Singleton mutable de acceso global → módulo con estado cerrado o instancia única gestionada | 🟠 | 🔴 |
| OBJ-04 | Instanciación de objetos pesados dentro de bucle → fuera del bucle o pooling | 🟠 | 🟢 |
| OBJ-05 | API que retorna/expone tipo concreto cuando el dominio pide la abstracción → exponer la interfaz | 🟡 | 🔴 |

Excepciones transversales del dominio: objetos de valor inmutables,
DTOs y creación local sin sustituto concebible NO se tocan (el criterio
de olor: "¿puedo inyectar una implementación distinta sin editar este
código?" — si no hay razón para responder "algún día sí", es correcto
así). OBJ-03 y OBJ-05 con riesgo 🔴: el patrón de acceso global y la
forma del retorno son contratos para consumidores existentes.

---

## Dependencias de orden (guía, no ley)

Dentro de una misma prioridad, estos órdenes evitan retrabajo:

1. **N-05 antes que todo**: casi cualquier paso posterior puede
   necesitar la config extraída.
2. **FE-01 / BE-01 antes de D-03**: la deduplicación necesita un
   destino donde vivir.
3. **FE-22 antes de FE-24 y BE-14**: la fuente de verdad define cómo
   se piden los datos y quién calcula.
4. **BE-22 antes de BE-05**: el código de estado requiere un formato
   de error central que lo emita.
5. **FE-15 junto a FE-16/FE-17**: son toques al mismo render; separarlos
   triplica la verificación de paridad.
6. **BE-11 y BE-12 juntos**: misma capa de persistencia.
7. **D-01/D-02 antes que N-02**: la extracción de constantes necesita
   saber primero quién es el dueño del conocimiento.
8. **RES-01 antes que RES-02/03**: primero la liberación garantizada,
   después se centraliza.
9. **ALG-04 siempre como paso aislado** (riesgo 🔴 por fuga de orden):
   nunca agrupado con otros criterios.

## Cómo extender este catálogo

Un criterio nuevo debe responder las 5 preguntas: **ID · Detección ·
Refactor · Severidad · Riesgo · Excepciones**.

**Prueba de admisión**: enuncia la detección como instrucción verificable.
Si dos revisores aplicándola pueden llegar a resultados distintos,
todavía es una opinión, no un criterio.

Reglas de ID:
- Se asigna el siguiente número del dominio; los retirados no se reutilizan.
- Cambiar severidad o riesgo de un criterio NO cambia su ID: la
  trazabilidad manda.
- Todo cambio al catálogo se anota con fecha en el encabezado de este archivo.

---
*Catálogo v2.1 — conserva íntegros 10 Núcleo · 6 DRY · 24 Frontend · 22 Backend · 5 ALG · 5 RES · 5 OBJ = 77 criterios de v2.0*
*Retirados: N-01 (migra a D-03). IDs retirados no se reutilizan.*
