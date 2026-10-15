---
name: refactor-codebase
description: >
  Audita y refactoriza proyectos en cualquier lenguaje o paradigma
  preservando el comportamiento observable (equivalencia semántica).
  Usar cuando el usuario pida refactorizar, limpiar, reestructurar,
  deconstruir, deduplicar (DRY), optimizar complejidad (Big O) o mejorar
  el manejo de recursos e instanciación de código existente. Aplica el
  protocolo del barco de Teseo: reemplazo incremental verificable,
  pieza por pieza, sin perder la identidad funcional. Entrega auditoría
  trazable, arquitectura AS-IS/AS-BUILT, plan priorizado, refactor incremental
  verificado y reporte antes/después. NO usar para features, bug fixes,
  migraciones de stack, upgrades de dependencias ni cambios deliberados de
  contrato; se clasifican y documentan, pero no se ejecutan como refactor puro.
---

# Refactorización de codebase (protocolo de Teseo) — v2.5.0-rc.1

## Identidad de version, propósito y release

La fuente canónica del release es `VERSION.json` (`2.5.0-rc.1`, candidato
sin publicar como versión estable); el esquema de protocolo del runner es
`teseo-v2.5` y es **independiente** de la versión de la distribución.
Los 77 criterios se custodian por SHA-256 y cuenta, no por una promesa de
77 transformadores automáticos. `CAPABILITIES.json` es el inventario
verificable de lo implementado, probado, documental y pendiente.

Antes de refactorizar, reconcilia el **propósito declarado y comprobado**
del proyecto, su versionado efectivo y la compatibilidad de cada dimensión
activa E(P). Si la versión real es incierta, NO afirmar equivalencia total.
Ver `references/versionado-y-proposito.md` y `scripts/version_audit.py`.

## Principio rector

Refactorizar es cambiar la estructura sin cambiar el contrato funcional
observable. La skill modela tres dimensiones sin asumir ninguna tecnología:

- **C(P)**: contrato funcional observable: outputs, errores, orden visible,
  protocolos, efectos externos y cualquier propiedad no funcional contratada.
- **Q(P)**: calidad interna/no funcional no contratada: fugas, memoria accidental,
  trabajo redundante, complejidad y otras propiedades mejorables sin cambiar C.
- **E(P)**: sobre operacional realmente necesario para ejecutar P. Se descubre
  por evidencia del proyecto y puede incluir sustrato de ejecución/toolchain,
  resolución de dependencias, artefactos de build, configuración, sistema
  operativo/filesystem, estado persistente, servicios externos o dispositivos.
  **Una dimensión sólo entra en E(P) si hay evidencia de que el sistema depende
  de ella. No existe una lista tecnológica obligatoria.**

Refactor puro T exige **C(T(P), E₀) = C(P, E₀)**, **Q(T(P)) no peor que Q(P)**
y **E₁ = E₀** para las dimensiones activas durante el changeset. Una mejora de Q
está permitida; una variación deliberada de E es ENVIRONMENT_CHANGE/MIGRATION y
se aísla. No atribuyas al refactor una falla hasta descartar drift de las
precondiciones operacionales que el propio discovery demostró relevantes.

El código existente, aunque sea malo, ES la especificación. Los workarounds
raros suelen proteger casos que todavía no conoces.

Antes de tocar código responde: **¿cómo sé que sigue siendo el mismo barco?**
El barco de Teseo se mantiene mientras su contrato con el puerto se cumple. Si
no puedes verificarlo, tu siguiente tarea es construir el modo de verificarlo,
no editar código.

## Segundo mandato: deconstruir antes de construir

No es mover código: es entenderlo. Ninguna pieza se reemplaza hasta saber qué
entra, qué sale, qué asume, qué efectos causa y qué consumidor se rompe si
cambia. Una pieza mal leída produce un reemplazo elegante que falla en producción.

## Tercer mandato: una máquina del tiempo bajo custodia

Git ofrece historia y comparación de **código versionado**, no telemetría de ejecución
ni versiones automáticas de estado externo. Investiga cambios mediante una baraja de
operaciones de Git **combinadas según preguntas verificables**, no por comandos
aleatorios. Preserva siempre el worktree original, crea un worktree de refactor
separado y guarda evidencias por segmento, contrato y commit. Nunca asumas que
un hash, un commit o un diff prueban paridad funcional por sí solos.

Antes de una escritura resuelve intención, objetivo, ruta, rama, commit, segmento,
permisos, aislamiento de efectos externos y estado de contexto. Las escrituras
requieren un `RUN-CONTRACT.json` confiable, verificación de identidad pre/post y
un runner capaz de imponer restricciones reales. Las instrucciones Markdown o
un preflight opcional **no son un sandbox**. Ver `references/git-maquina-tiempo.md`,
`references/gobernanza-ejecucion.md` y `references/jugadas-git.md`.

## Cuarto mandato v2.5: evidencia y ejecución mínima verificable

La v2.5 añade `references/gobernanza-v2.5.md` y herramientas ejecutables
acotadas. La gobernanza real no nace de escribir reglas: antes de cada cambio
se verifica identidad Git, ámbito de archivo, autorización con caducidad,
preimagen y postimagen. Se emplea `scripts/path_policy.py` para detectar
symlinks/rutas fuera de alcance; `scripts/teseo_runner.py` sólo permite reemplazo
atómico/recuperación de archivos existentes bajo contrato confiable externo.
Cuando el entorno no permita enforcement verificable, **BLOCKED**: no habilitar
escrituras directas como atajo.

La inspección pasiva no debe ejecutar ejecutables encontrados en `PATH`, hooks,
fsmonitor, filtros o scripts del proyecto. El conjunto de invariantes se
verifica por contratos explícitos mediante `scripts/verify_invariants.py`;
`VERIFIED` es específico al alcance, no equivalencia absoluta. Los vínculos
de `scripts/evidence_graph.py` requieren fuente/hash, pero no prueban causalidad.

**No confundir el alcance implementado:** la primitiva v2.5 cubre archivos
regulares existentes en POSIX y recuperación de su contenido. No provee
transacciones multiarchivo, aislamiento de todos los procesos, recuperación
de efectos externos ni coordinación distribuida. Los demás flujos siguen
sujetos a aprobación, simulación/aislamiento y resultado `PARTIAL` o `BLOCKED`.

## Líneas rojas (no negociables)

1. **No reescribir desde cero.** Se transforma incrementalmente. Un proyecto
   paralelo "mejor" es otro barco, no un refactor.
2. **No mezclar objetivos.** Bugs detectados van a BUGS-DETECTADOS.md y NO se
   arreglan en el refactor. Features nuevas: fuera de alcance.
3. **Contratos públicos solo cambian con compatibilidad explícita.** APIs,
   eventos, formatos, claves persistidas, protocolos y exports consumidos.
4. **Sin red de seguridad no se toca código.** Git limpio + baseline/golden
   master verificable para el flujo afectado.
5. **Pasos atómicos.** Un criterio o grupo mecánico cohesivo por verificación.
6. **Deprecar antes que borrar.**
7. **No actualizar dependencias** en el mismo changeset del refactor.
8. **DRY hasta el nivel de conocimiento, no de texto.** Ver fundamentos.md.
9. **Optimizar complejidad sólo preservando semántica.** Orden, laziness,
   timeouts, límites y concurrencia pueden volver observable la estructura.
10. **Recursos: no-regresión.** Lo interno puede mejorar pero no degradarse;
    lo contratado pertenece a C(P) y exige paridad.
11. **Congela E(P), no una lista prefabricada.** Identifica primero qué
    dimensiones operacionales son realmente dependencias del sistema y congela
    únicamente ésas. Un cambio deliberado de una dimensión activa va separado.
12. **Un sistema roto no produce un golden master sano.** Un flujo crítico que
    falla antes del refactor se trata como incidente preexistente.
13. **Diagramas antes de cambios.** Ningún cambio empieza sin arquitectura
    AS-IS basada en evidencia y diagramas ASCII de pipelines/flows/workflows
    aplicables. Una flecha `[? UNVERIFIED]` es mejor que una inventada.
14. **Compatibilidad se investiga, no se supone.** Si una decisión depende de
    una versión, protocolo, formato, engine, herramienta o integración concreta,
    consulta la fuente primaria correspondiente. Si no puede verificarse,
    registra UNVERIFIED y bloquea cambios de alto riesgo que dependan de ello.
15. **Los ejemplos no son requisitos.** Toda tecnología concreta documentada en
    anexos sólo ilustra cómo implementar el protocolo. Nunca actives un gate por
    el ejemplo: actívalo exclusivamente por evidencia del proyecto.

16. **Identidad antes de escribir:** worktree, git-dir propio, git-common-dir,
    HEAD, rama esperada y target path dentro del alcance. Si difieren, BLOCKED.
17. **No confiar en la memoria conversacional:** rehidratar contrato de ejecución
    externo y ledger después de reanudación, compactación o cambio de segmento.
18. **Git no guarda todo:** detectar staged/unstaged/untracked/ignored relevantes,
    submódulos y efectos fuera de Git; jamás inventar un baseline limpio.
19. **Worktree no aísla servicios:** aislar procesos, datos y efectos según E(P).
20. **No ejecutar operaciones destructivas automáticamente:** reset --hard,
    clean, rebase, push --force, reemplazo de refs, borrado de worktrees, etc.
21. **Las cartas Git son medios, no objetivos:** todo diagnóstico requiere
    hipótesis, prueba falsable, evidencia e incertidumbre explícita.

## Clasificación obligatoria del cambio (v2.3)

- **PURE_REFACTOR**: C(P) idéntico; Q igual o mejor. Puede ejecutarse aquí.
- **COMPATIBLE_EVOLUTION**: agrega/moderniza manteniendo contrato anterior con
  compatibilidad explícita. Se documenta y requiere alcance autorizado.
- **FIX**: corrige comportamiento defectuoso observable. Fuera del changeset.
- **FEATURE**: agrega capacidad nueva. Fuera de alcance.
- **MIGRATION**: cambia stack, protocolo o contrato deliberadamente. Fuera.
- **ENVIRONMENT_CHANGE**: cambia una dimensión activa de E(P). Se investiga y
  documenta, pero se ejecuta aislado del refactor.

**Gate:** ante duda entre PURE_REFACTOR y otra clase, NO ejecutar. Registrar como
candidato hasta obtener evidencia suficiente.

## Workflow

### Fase 0A — Discovery estructural
Detecta lenguajes, paradigmas, frameworks, tamaño, tests, git, manifests,
entrypoints y fronteras externas. En repos medianos/grandes crea un Candidate
Map; no recorras ciegamente 77 criterios × todos los archivos. Usa
`scripts/discover.py` y `references/detectores.md` como apoyo.

### Fase 0B — Arqueología operativa obligatoria
Antes de auditar para cambiar, reconstruye cómo funciona HOY el sistema.
Produce como mínimo:

- `ESTADO-INICIAL.md`: qué funciona/falla, comandos reales, smoke tests y
  GREEN/YELLOW/RED por flujo crítico.
- `ARQUITECTURA-AS-IS.md`: componentes y diagramas ASCII basados en evidencia.
- `ENTORNO-OPERACIONAL.md`: fingerprint E(P) **derivado del proyecto**, con sólo
  las dimensiones activas demostradas.
- `FUENTES-TECNICAS.md`: fuentes primarias consultadas cuando una afirmación de
  compatibilidad dependa de tecnología/versionado concreto.

**Diagramas ASCII obligatorios cuando apliquen** (`references/diagramas.md`):
1. Contexto/componentes y fronteras.
2. Bootstrap/arranque.
3. Pipelines de transformación de datos/artefactos.
4. Flows de ejecución críticos.
5. Workflows de negocio/usuario con decisiones y estados.
6. Persistencia/estado durable, **sólo si existe**.
7. Integraciones externas o dispositivos, **sólo si existen**.
8. Ruta de error/fallo si el sistema ya presenta avería.

Cada nodo/flecha cita evidencia (`archivo:línea`, manifest/config, log, comando,
test o fuente primaria). Lo inferido: `[INFERRED]`; desconocido:
`[? UNVERIFIED]`. No conviertas hipótesis en arquitectura declarada.

### Fase 0C — Gate de salud pre-refactor
Ejecuta smoke tests de los flujos críticos antes de tocar código:

- **GREEN**: reproducible + baseline confiable → elegible para refactor.
- **YELLOW**: parcial/no reproducible → sólo zonas aisladas con baseline propio.
- **RED**: flujo crítico roto → `INCIDENTE-PREEXISTENTE.md`; no tomar ese fallo
  como comportamiento sano ni atribuirlo al refactor.

Para un incidente, investiga las capas que **el AS-IS demuestre relevantes**.
Parte del síntoma y recorre hacia atrás sus dependencias: código, sustrato de
ejecución/build, resolución de dependencias, configuración/rutas, estado durable,
OS/filesystem/red, integraciones externas o dispositivos. El orden es causal y
adaptativo, no una checklist tecnológica fija. Un FIX se hace en changeset
separado; después se regenera 0B/0C y recién entonces se congela el baseline sano.

### Fase 0D — Fingerprint adaptativo E(P)
Construye E(P) por **activación condicional**. Para cada dimensión candidata:

1. demuestra que el sistema depende de ella;
2. registra identidad/versión/configuración suficiente para reproducirla;
3. define cómo detectar drift antes/después;
4. define una prueba no destructiva o marca `UNVERIFIED`;
5. documenta la fuente primaria si la compatibilidad depende de versión/formato.

Usa `references/entorno-operacional.md` para el contrato y
`references/adaptadores.md` para perfiles tecnológicos **opcionales**. Los
adaptadores son ejemplos de implementación del contrato, no requisitos.
`scripts/environment_probe.py` da inventario pasivo sin ejecutar herramientas detectadas; scripts bajo
`scripts/adapters/` sólo se usan cuando el discovery confirma esa tecnología.

### Fase 0E — Reconstrucción bidireccional y segmentación
Construye vistas top-down (capacidades → workflows → contratos) y bottom-up
(efectos/código → relaciones → capacidades), reconcilia diferencias y asigna
segmentos funcionales con IDs. Para cada relación guarda OBSERVED, INFERRED o
UNKNOWN y evidencia; los ciclos recursivos requieren visited-set, límites de
profundidad y salida UNRESOLVED. Reflexiona buscando evidencia que **refute**
las inferencias. No fuerces una arquitectura idealizada sobre el repositorio.
Ver `references/reconstruccion-bidireccional.md`.

### Fase 0F — Custodia Git e integridad del contexto
Antes de cualquier refactor: fingerprint del repositorio y worktree, cambios
indexados/no indexados/no rastreados/ignorados relevantes, baseline commit,
contrato de alcance, segmentación, entorno y estado de salud. Si Git falta,
marcar LIMITATION y crear un snapshot seguro sólo mediante autorización.

- Los comandos de lectura/historia son autónomos; cambios de worktree/branch
  requieren un plan aprobado. Escrituras de código sólo en worktree autorizado.
- Crea worktree baseline separado (detached) y worktree refactor en rama exclusiva
  cuando Git y el estado del repo lo permitan. No reutilices una rama activa.
- Persiste `RUN-CONTRACT.json`, `RUN-STATE.json` y ledger fuera del árbol
  modificable, administrados por coordinador confiable; el agente no puede
  redefinir el alcance unilateralmente.
- Preflight de identidad y postflight de alcance **por operación**, rehidratación
  después de pérdida/compactación de contexto. Prohibir cambios de rama o
  repositorio implícitos. Un cambio HEAD esperado por commit validado se acepta
  sólo tras actualizar checkpoint por el coordinador.
- `scripts/git_guard.py` evita fsmonitor/hook de Git configurado en el repo al inspeccionar y sirve para detectar deriva;
  no puede impedir escrituras que pasen por fuera de él. El aislamiento fuerte
  requiere runner/permissions o sandbox OS. Ver gobernanza-ejecucion.md.

### Fase 0G — Plan de jugadas Git, riesgos y cobertura
Elige una **jugada documentada** de `references/jugadas-git.md` para responder
una pregunta: arqueología, reconstrucción, causa de regresión, comparación de
cambios, custodia o recuperación. Planea la prueba diferencial sobre flujos
GREEN del baseline; distinguir VERIFIED/PARTIAL/BLOCKED. Inspecciona primero
los efectos de scripts/tests; nunca ejecutar scripts arbitrarios por venir del
repo. `git bisect` sólo en worktree diagnóstico desechable y entorno aislado.

### Fase 1 — Deconstrucción y golden master
Primero comprender, luego congelar:
- Deconstruye cada pieza candidata: entradas, salidas, supuestos, efectos,
  consumidores y posición en AS-IS.
- Congela C(P) sólo para flujos GREEN y E₀ sólo para dimensiones activas.
- Captura outputs por canal aplicable: protocolo/API/CLI/UI/eventos/archivos/
  estado durable/integraciones, según lo que el sistema realmente exponga.
- Identifica nondeterminismo y define comparadores explícitos; ver paridad.md.
- Registra Q(P): recursos internos relevantes detectados.
Éxito: C(P) idéntico + Q no peor + E activo sin drift no autorizado.

### Fase 2 — Auditoría
Aplica `references/criterios.md` (N, D, FE, BE, ALG, RES, OBJ) sobre Candidate
Map y arquitectura deconstruida. Cada hallazgo incluye ID, ubicación, evidencia,
severidad, riesgo, clase y estado CONFIRMED/CANDIDATE/NOT_APPLICABLE. Un
hallazgo dependiente de `[? UNVERIFIED]` no puede ser CONFIRMED. Sólo CONFIRMED
entra al plan. Un dominio limpio se reporta como limpio.

### Fase 3 — Plan
Prioriza severidad × riesgo y dependencias. El plan puro contiene sólo
CONFIRMED + PURE_REFACTOR sobre flujos con baseline válido. Para cada paso fija:
contrato, nodos AS-IS afectados, segmentos y relaciones, comparador, fingerprint operacional esperado, identidad Git, pre/post-check y
rollback de código + recuperación de estado externo cuando aplique. Presenta el plan y espera confirmación.

### Fase 4 — Ejecución incremental
Por paso: rehidrata contrato, verifica identidad y scope con el runner confiable del entorno (para sustituciones acotadas existe `teseo_runner.py`); registra pre-state (git/hash + E₀ activo), ejecuta el cambio mínimo en worktree autorizado,
corre paridad y smoke test, vuelve a medir E/Q, audita archivos alterados y actualiza changelog/ledger. **Si una
dimensión activa de E cambia sin autorización, el paso falla aunque los tests
pasen.** Si C rompe paridad: detén el cambio, diagnostica con Git y revierte exclusivamente las modificaciones atribuibles al paso y autorizadas; nunca uses `reset --hard`/`clean` como recuperación automática. Nunca actualices el golden
master para hacer verde el cambio.

### Fase 5 — Reporte y arquitectura AS-BUILT
Entrega conteos, cobertura, paridad, no-regresión, drift operacional,
incidentes, bugs y decisiones, cobertura VERIFIED/PARTIAL/BLOCKED, segmentación, cambios Git por commit y límites de diagnóstico. Genera `ARQUITECTURA-AS-BUILT.md` con los mismos
diagramas relevantes del AS-IS y delta explícito. En refactor puro, caminos
externamente observables se conservan; cambios internos se rastrean
AS-IS → paso → AS-BUILT.

## Gating de permisos Git (obligatorio)
- **READ:** status, log, show, diff, blame, rev-parse, merge-base, reflog show,
  worktree list; permitido en contexto ya autorizado, con límites de salida.
- **PREPARE:** worktree add, branch nueva, commit de cambios verificados;
  requiere alcance/plan aprobado y preflight/postflight por runner.
- **DIAGNOSE:** bisect, cherry-pick -n, restore temporal y pruebas históricas:
  sólo en zona diagnóstica aislada con plan y sin tocar el baseline.
- **PROTECTED:** switch/checkout del original, reset --hard, clean -fd,
  rebase, force push, ref changes, eliminar worktrees: nunca automático.
- **EXTERNAL:** push, publicación, escrituras en servicios/DB externos:
  requieren autorización separada y controles específicos.

## Interacción con el usuario
- Alcance ambiguo: pregunta antes de auditar.
- Auditoría y plan se confirman antes de ejecutar.
- Ruptura de paridad = bloqueo inmediato, no "ajuste menor".
- Idioma: el del usuario en todo lo generado.

## Cuándo NO usar esta skill
- Proyecto desde cero (no hay P que preservar).
- Pedidos de features o fixes.
- Migración deliberada de stack/contrato: requiere otro changeset/protocolo.
