# Gobernanza operativa v2.5 — diseño, implementación y límites

## 1. Cambio de modelo

El contrato `RUN-CONTRACT.json` NO nace del agente que solicita escribir. Un
coordinador con permisos distintos o una supervisión externa autoriza cada
alcance y su caducidad. El agente recibe únicamente capacidades necesarias.

- `scripts/git_guard.py`: pre/postflight observable y no mutante **de intención**;
  evita ejecutar fsmonitor/hook externos del repositorio por su configuración.
  No promete sandbox ni impide acceso directo a Git o al sistema de archivos.
- `scripts/teseo_runner.py`: primitiva acotada de sustitución atómica de **un
  archivo regular ya existente** y recuperación del before-image.
  No permite shell arbitrario, edición de `.git`, rutas escapadas, renombrados
  cruzados ni escritura de archivos nuevos.
- `scripts/path_policy.py`: matcher por componentes, lectura confinada POSIX
  `dir_fd/O_NOFOLLOW`, no siguiendo enlaces simbólicos. Si la plataforma carece
  de garantías requeridas se rechaza, no se finge aislamiento.
- `scripts/verify_invariants.py`: verificación tipada de observaciones, nunca
  equivalencia matemática de todo el sistema.
- `scripts/evidence_graph.py`: valida estructura/procedencia declarada, no la
  veracidad de pruebas externas ni causalidad.

**Frontera de confianza:** si el mismo proceso/principal puede alterar el
contrato, los respaldos o los permisos del runner, no existe enforcement contra
ese agente. Se necesita un principal/servicio independiente o sandbox OS que
impida invocaciones alternativas. Llamarlo «runner confiable» es condicional.

## 2. Modelo de contrato (ejemplo; NO autorizado ni ejecutable sin valores reales)

```json
{
  "protocol": "teseo-v2.5",
  "runId": "RUN-REEMPLAZAR",
  "approved": false,
  "expiresAt": "2026-12-01T00:00:00Z",
  "stateDir": "/directorio-controlado-fuera-de-worktree",
  "authorizedOperations": ["WRITE", "RECOVER"],
  "repository": {
    "refactorWorktree": "/ruta-real-worktree-refactor",
    "gitDir": "/ruta-gitdir-propio",
    "gitCommonDir": "/ruta-common-gitdir",
    "expectedBranch": "refs/heads/feat/teseo",
    "lastVerifiedCommit": "OID-GIT-VERIFICADO",
    "baselineCommit": "OID-GIT-VERIFICADO"
  },
  "scope": {
    "segment": "SEG-001",
    "allowedPaths": ["src/*.py"]
  }
}
```

`approved: false` es intencional. La autorización la emite el coordinador y
caduca; editar este ejemplo no genera permiso. El runner comprueba que
contract/state no estén dentro del worktree y que no sean escribibles por
otros grupos, pero **no demuestra separación entre agente y coordinador**.

Intent `WRITE`:

```json
{
  "runId": "RUN-REEMPLAZAR",
  "stepId": "STEP-001",
  "target": "src/modulo.py",
  "expectedBeforeSha256": "HASH-REAL-ANTES",
  "expectedAfterSha256": "HASH-REAL-DESPUES"
}
```

Uso condicionado al contrato confiable:

```bash
python scripts/teseo_runner.py write --contract /control/run.json \
  --intent /control/intent.json --content-file /control/contenido-nuevo
python scripts/teseo_runner.py recover --contract /control/run.json \
  --intent /control/intent.json
```

La sustitución exige coincidencia del contenido original por SHA-256. El
estado `PREPARED` y el before-image se almacenan **antes** de sustituir el
archivo; `COMMITTED` se anota tras validación. En interrupción después de
`PREPARED`, una nueva escritura del mismo paso queda bloqueada, y un operador
puede solicitar `RECOVER` si el estado coincide con el before-/after-image.
No se borra automáticamente el árbol ni se ejecuta `git reset --hard`.

## 3. Estados, rehidratación e integridad de contexto

```text
ISSUED -> DISCOVERY -> BASELINED -> AUTHORIZED
                                       |
                                     WRITE
                                       |
                               PREPARED + backup
                                   /      \
                              COMMITTED  INTERRUPTED
                                  |           |
                                VERIFY       RECOVER
                                  |           |
                           ACCEPT/PARTIAL    REVALIDATE
```

Cada reanudación revalida identidad Git, ruta, rama, HEAD, fecha y alcance.
Checkpoint/ledger fuera del worktree, pero el JSONL por sí solo no es un
almacenamiento inmutable o criptográficamente autenticado. Un coordinador
exclusivo debe protegerlo y resolver multiagente / CAS entre procesos y hosts.

## 4. Limitaciones abiertas y restricciones de v2.5

1. Este runner admite únicamente archivos **existentes y regulares** en POSIX.
   `git add/commit`, nuevas rutas, reestructuración multiarchivo y cambios
   externos siguen en modo plan/documentación; deben pasar por un runner
   expandido con atomicidad a nivel de paso, no por operaciones no supervisadas.
2. El runner usa un lock POSIX local, que **no coordina máquinas distintas**.
   Procesos que no cooperen pueden modificar el archivo tras preflight.
   La sustitución es atómica en el directorio padre; no equivale a aislamiento
   global y sigue existiendo un límite TOCTOU frente a otros escritores.
3. Restaurar un before-image **no revierte** datos, correos, eventos, recursos
   externos ni migraciones. Evaluar cada efecto según E(P), aislar y ensayar
   recuperación separada. Ante efectos irreversibles, no ejecutar prueba real.
4. Los procesos/compiladores de terceros no se ejecutan por discovery pasivo.
   Un test de integración real requiere sandbox y permiso explícito.
5. Un test/evidence graph generado por el mismo ejecutor no certifica por sí
   mismo su integridad; un verificador independiente debe validar las capturas.
6. En sistemas no POSIX o repositorios con submódulos/symlinks especiales, el
   runner informa incompatibilidad. Nunca degradar las garantías silenciosamente.

## 5. Diferencial, integral e invariantes

Diferencial: contrastar el cambio local y sus dependencias afectadas respecto a
un baseline con entorno fijo. Integral (analogía): comprobar que una secuencia
de pasos aceptados no acumula desviaciones entre S0 y Sn.

La aceptación requiere evidencias separadas por invariante: funcional, datos,
transacciones, seguridad, estado temporal, y rendimiento contratado. No se
resume con una nota global que esconda un `FAIL` crítico. `VERIFIED` significa
solo que **las observaciones declaradas pasaron**, `PARTIAL` que hubo lagunas,
y `BLOCKED` que un contrato crítico falló o el aislamiento no es confiable.

## 6. Integración opcional con Code Graph

`devcicm/code-graph` ofrece análisis estructural y señales de impacto. Puede
proporcionar nodos y relaciones **como observaciones** bajo un adaptador
opcional. Teseo deberá verificar su procedencia y no convertir puntuaciones de
riesgo ni inferencias en autorizaciones. No impone Node ni dependencia
obligatoria al protocolo de refactor.
