# Plantillas de entregables (v2.3)

El idioma sigue al usuario. No omitir secciones aplicables; `NO_APLICA` y
`UNVERIFIED` son estados válidos. Los artefactos de Fase 0 preceden al plan.

---

## ESTADO-INICIAL.md

# Estado inicial — <proyecto>
- Commit/tree: <hash>
- Comando/launcher real: <...>
- Contexto de ejecución relevante: <...>
- Fecha: <...>

| Flujo crítico | Smoke test | Resultado | Salud | Evidencia |
|---|---|---|---|---|
| <flujo> | <pasos> | <observado> | GREEN/YELLOW/RED | <log/test> |

## Fallos preexistentes
<remisión a INCIDENTE-PREEXISTENTE.md si aplica>

---

## ARQUITECTURA-AS-IS.md

# Arquitectura AS-IS — <proyecto>
Incluye sólo los diagramas aplicables de `references/diagramas.md` y tabla E1..En.
Como mínimo: contexto, bootstrap y los pipelines/flows/workflows críticos. Añade
persistencia, integraciones o dispositivos sólo si existen. Marca `[INFERRED]` y
`[? UNVERIFIED]`.

---

## ENTORNO-OPERACIONAL.md

| Dimensión E(P) activa | Por qué aplica | Baseline | Comparador | Probe | Evidencia |
|---|---|---|---|---|---|
| <EXECUTION_SUBSTRATE/...> | <dependencia real> | <valor> | <regla> | <read-only> | <E#> |

### Dimensiones evaluadas pero no activas
| Dimensión | Estado | Evidencia |
|---|---|---|
| <tipo> | NO_APLICA/UNVERIFIED | <...> |

---

## FUENTES-TECNICAS.md

| Componente/identidad | Fuente primaria | Consultada | Hecho verificado | Decisión |
|---|---|---|---|---|
| | | | | |

---

## INCIDENTE-PREEXISTENTE.md

# Incidente — <flujo>
- Síntoma exacto:
- Primera reproducción:
- Salud: RED/YELLOW
- Último estado conocido funcional:
- Último nodo sano / primer nodo fallido:

| Hipótesis | Nodo/capa | Evidencia + | Evidencia - | Prueba | Resultado |
|---|---|---|---|---|---|
| | | | | | |

- Causa: ROOT_CAUSE_CONFIRMED / LIKELY / UNRESOLVED
- Fix separado requerido: sí/no
- Criterio para volver a Fase 1: <smoke test verde>

---

## AUDITORIA.md

# Auditoría de refactor — <proyecto>
- Stack detectado: <...>
- Alcance: <...>
- Git: <limpio/sucio/ausente>
- Salud baseline: <GREEN/YELLOW/RED>
- Golden master: <generado/bloqueado>
- E(P) activo: <hash/resumen>
- AS-IS: <completo/pendiente>

| Dominio | 🔴 | 🟠 | 🟡 | ⚪ | Total |
|---|---|---|---|---|---|
| Núcleo | | | | | |
| DRY | | | | | |
| Frontend | | | | | |
| Backend | | | | | |
| ALG | | | | | |
| RES | | | | | |
| OBJ | | | | | |

### Hallazgos confirmados
| # | Criterio | Ubicación | Evidencia | Estado | Clase | Sev | Riesgo | Diagrama/nodo |
|---|---|---|---|---|---|---|---|---|
| 1 | <ID> | <archivo:línea> | <...> | CONFIRMED | PURE_REFACTOR | | | <E#> |

### Candidatos
| # | Criterio | Ubicación | Duda/evidencia faltante |
|---|---|---|---|

### Zonas limpias
<...>

---

## PLAN-REFACTOR.md

### Precondiciones
- git limpio: <sí/no>
- baseline GREEN para flujos tocados: <sí/no>
- golden master: <sí/no>
- AS-IS + E(P) activo congelados: <sí/no>
- si alguna es no: NO ejecutar ese paso.

| Paso | P | Criterio(s) | Clase | Archivos | Nodo AS-IS | Verificación | E esperado | Rollback |
|---|---|---|---|---|---|---|---|---|
| 1 | P1 | <IDs> | PURE_REFACTOR | | | exact/... | sin drift | <...> |

---

## CHANGELOG-REFACTOR.md

| Paso | Criterio | Cambio | Antes→Después | C(P) | Q(P) | E(P) | Custodia |
|---|---|---|---|---|---|---|---|
| 1 | <ID> | | | ✅ | ✅ | ✅ sin drift | <commit/tree hash> |

---

## BUGS-DETECTADOS.md

| # | Ubicación | Descripción | Urgencia | Evidencia | Por qué no se arregló aquí |
|---|---|---|---|---|---|

---

## ARQUITECTURA-AS-BUILT.md

Repetir diagramas AS-IS aplicables con misma nomenclatura y agregar:

| Nodo/arista | AS-IS | AS-BUILT | Motivo | Contrato externo cambió |
|---|---|---|---|---|
| | | | | NO para PURE_REFACTOR |

---

## REPORTE-REFACTOR.md

# Reporte — <proyecto>

### Ocurrencias
| Criterio | Antes | Después |
|---|---|---|

### Paridad
| Contrato | Comparador | Baseline | Actual | Resultado |
|---|---|---|---|---|

### Sobre operacional
| Dimensión E(P) activa | Baseline | Final | Drift | Resultado |
|---|---|---|---|---|

### Recursos
| Recurso | Regla | Baseline | Final | Resultado |
|---|---|---|---|---|

### Arquitectura
- AS-IS: <archivo>
- AS-BUILT: <archivo>
- Delta: <resumen>

### Incidentes/bugs/deprecaciones/fuera de alcance
<...>

---

## Extensión v2.4 — Git Power / Custodia (sin eliminar plantillas anteriores)

### GIT-CUSTODIA.md

| Paso | Jugada Git | Pregunta | baseline OID | pre OID | post OID | worktree | rama | segmento | evidencia | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| | A/B/C/D/E/F/G | | | | | | | | | VERIFIED/PARTIAL/BLOCKED |

- Identidad de root/gitDir/gitCommonDir validada:
- Estado staged/unstaged/untracked/ignored relevante:
- Drift E(P) detectado o descartado:
- Recursos externos aislados o limitaciones:
- Última operación aceptada por el coordinador:
- Siguiente operación autorizada (si existe):

### MATRIZ-SEGMENTOS.md

| Segmento | Capacidad | Workflow | Contrato | Módulos/archivos | Relaciones | Evidencia top-down | Evidencia bottom-up | Incertidumbre |
|---|---|---|---|---|---|---|---|---|

### PLAN DE JUGADAS

| Hipótesis | Jugada | Comandos READ | Operaciones mutantes | Aislamiento | Prueba falsable | Permiso | Salida |
|---|---|---|---|---|---|---|---|

### RUN-CONTRACT.json / RUN-STATE.json / TRACE-LEDGER.jsonl

El contrato persistido y su ledger están **fuera del worktree editable** y
bajo administración del ejecutor confiable. Rehidratar y verificar Git tras
resumen de contexto, cambio de segmento, reinicio o anomalía.

Campos obligatorios del ledger: runId, segmento, objetivo, operación,
identidad pre/post, rutas cambiadas, evidencia, prueba, autorización y
resultado; nunca guardar secretos ni diffs íntegros indiscriminadamente.
