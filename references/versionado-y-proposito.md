# Contrato de versiones, propósito y compatibilidad — Teseo

## 1. Identidades independientes (no confundir)

| Identidad | Fuente autorizada | Qué controla |
|---|---|---|
| **Distribución** | `VERSION.json.release_version` (SemVer) | ZIP, README, release/tag, instalación. Una rama o un PR **no** son un release |
| **Protocolo de ejecución** | `VERSION.json.protocol_version` + lista de protocolos soportados | JSON del contrato runner/guard y migración de esquemas |
| **Catálogo** | `criteria.count` + SHA-256 de `references/criterios.md` | Conservación de los 77 criterios independientemente del software que los implementa |
| **Capacidades** | `CAPABILITIES.json` | Qué existe, qué se ha probado, qué es procedimiento documentado y qué NO se implementó |
| **Componentes históricos** | encabezado propio y tabla de procedencia | Documentos heredados v2.3/v2.4; su número histórico no se reescribe para simular evolución |
| **Proyecto auditado** | descubrimiento por evidencia | Versiones de ejecutables, toolchain, dependencias, protocolos, API, DB/estado, driver, etc. **solo si aplican** |

Un `2.5.0-rc.1` publicado en rama candidata sigue siendo candidato, no `2.5.0` estable. Una vez publicada una versión inmutable, las correcciones exigen una nueva versión; no sobrescribir tags ni artefactos. Reglas de compatibilidad basadas en SemVer 2.0.0: https://semver.org/spec/v2.0.0.html. Los artefactos de paquetes Python pueden usar PEP 440: https://peps.python.org/pep-0440/.

## 2. Auditoría del propósito (Purpose-Implementation Consistency)

Para cualquier proyecto investigado:

- Extrae promesa/propósito de **fuentes declarativas**: README, especificaciones, tests, interfaces, manifiestos; distingue fuentes actuales de históricos.
- Descubre flujos/contratos **observados** con top-down/bottom-up. Asocia evidencia reproducible por capacidad.
- Construye matriz `DECLARED -> IMPLEMENTED -> EXERCISED -> VERIFIED` (NO_INFERIBLE cuando falte evidencia).
- Si README promete funcionalidad sin implementación demostrada, registrar `CLAIM_UNVERIFIED` o `CLAIM_CONTRADICTED`, **no borrar la promesa ni inventar código**.
- La falta de un test no demuestra ausencia de la capacidad. Un archivo de código no prueba que funcione.
- Identifica si existen expectativas divergentes entre versión documentada, publicada, instalada y ejecutada.

## 3. Version-Compatibility Gate universal (antes de refactor)

Para cada dimensión E(P) *realmente activa*, declarar:

| Dimensión | Versión/estado declarado | Estado efectivo observado | Origen | Restricción/compatibilidad | Evidencia | Riesgo |
|---|---|---|---|---|---|---|
| Runtime/toolchain, si aplica | | | | | | |
| Dependencias + lock, si aplica | | | | | | |
| Schema/datos/protocolos, si aplica | | | | | | |
| Cliente/servidor/API, si aplica | | | | | | |
| Artifacts/build/deploy, si aplica | | | | | | |

**No imponer tecnologías:** todas las filas son condicionales. Capturar versión anunciada, versión resuelta en ejecución y rango compatible; no son necesariamente iguales. Diferenciar `DECLARED`, `OBSERVED`, `INFERRED`, `NOT_APPLICABLE`, `UNKNOWN`.

Para un cambio `PURE_REFACTOR` no incrementar automáticamente la versión de la aplicación: respetar su política de releases y congelar versiones activas durante el experimento. Si varía una dimensión E(P), clasificar `ENVIRONMENT_CHANGE`; si cambian protocolos/schema/contratos, separar MIGRATION o COMPATIBLE_EVOLUTION. El versionado acompaña la gestión de release, no autoriza mezclar objetivos de cambios.

## 4. Gate de release de la skill

1. `VERSION.json` debe indicar canal y propósito; el protocolo es independiente.
2. `CAPABILITIES.json` describe la implementación real; toda evidencia refiere un archivo existente (tests pasan en CI).
3. `SKILL.md`, README, distribuidor y ZIP muestran la **misma versión candidata**. Los documentos heredados no cuentan como errores si su procedencia está señalada.
4. SHA y cuenta del catálogo coinciden; el manifiesto protege el contenido distribuido.
5. La rama `feat/...` o un PR draft no es release; un tag `vX.Y.Z` sólo se publica tras aceptar controles y revisar compatibilidad.
6. Cambios en versiones de esquemas/protocolos requieren tests de compatibilidad; no forzar la interpretación del contrato antiguo cambiando un campo.
7. `--self-check` verifica estas declaraciones sin ejecutar programas del repositorio analizado.

## 5. Estados y evidencia

- `VERIFIED`: comprobación reproducida para escenario y versión específicos.
- `PARTIAL`: comprobación incompleta o evidencia insuficiente.
- `CLAIM_UNVERIFIED`: se declara, pero no hay evidencia positiva suficiente.
- `CLAIM_CONTRADICTED`: hay evidencia concreta contra una afirmación; investigar antes de cambiar.
- `VERSION_DRIFT`: versión documentada/resuelta o esquema operativo difiere de lo esperado.
- `BLOCKED`: cambio de alto riesgo requiere resolver contradicción de contrato/compatibilidad.

## 6. Entregable

`VERSION-PURPOSE-AUDIT.md`: estado, capacidades declaradas vs demostradas, mapa de versiones, riesgos, fuente de verdad, plan de compatibilidad y decisión del change-class. Conservar AS-IS/AS-BUILT del proyecto y lista de contradicciones.
