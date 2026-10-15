# VALIDACIÓN — Teseo / refactor-codebase v2.4

Fecha: 2026-10-10.

## Conservación de la base v2.3

- Archivos anteriores en ZIP: 18.
- Archivos resultantes en ZIP: 25.
- Archivos anteriores sin pérdida: **18 de 18**.
- Archivos previos modificados deliberadamente: MANIFEST.sha256, SKILL.md, references/plantillas.md.
- `references/criterios.md` idéntico byte por byte: **SÍ**.
- `references/fundamentos.md`, `references/paridad.md`, `references/lenguajes.md`, scripts de discovery/entorno/adaptadores: conservados.
- IDs activos: **77**; conteos {'N': 10, 'D': 6, 'FE': 24, 'BE': 22, 'ALG': 5, 'RES': 5, 'OBJ': 5}.
- Nuevos anexos: Git Time Machine, jugadas, reconstrucción bidireccional, gobernanza, pruebas adversariales.
- Nuevo script: `scripts/git_guard.py` (detección read-only).
- Nuevos tests: `tests/test_git_guard.py`.

## Resultados ejecutados

- `python -m unittest discover -s refactor-codebase/tests`: **12/12 PASS**.
- Incluye identidad, rama, HEAD, gitdir, ruta fuera de alcance, symlink, rename, dirty fuera del scope y falta de permisos.
- `environment_probe.py --self-test`: **PASS**.
- `runtime_probe.py --self-test`: **PASS**, se conservó compatibilidad v2.2.
- Manifiesto SHA-256: **24 de 24 hashes correctos**.
- Prueba de integridad ZIP: **PASS**.
- Generador autocontenido reconstruye ZIP **idéntico byte a byte**: **PASS**.

## Límites y riesgos residuales (NO cubiertos como enforcement)

- `git_guard.py` **detecta**, no intercepta escrituras ni controla al agente fuera del propio comando. Necesita un runner/sandbox confiable para bloquear acciones reales.
- Git Worktree no aísla bases de datos, APIs, dispositivos ni procesos.
- La inspección de Git no captura automáticamente archivos ignorados o estado externo.
- TOCTOU: identidad puede cambiar entre preflight y escritura; evitar mediante operaciones atómicas/runner, validación pre/post y permisos.
- Los tests verifican detección de desviaciones en un repositorio temporal, no equivalencia funcional sobre un proyecto real.
- No se ejecutaron operaciones Git destructivas ni cambios en repositorios de usuario.

## SHA-256

- ZIP: `1c970465c2f3b7ad051e26c609507c8ad524e33f05decc3f6ce7ae9458fa78b3`.
- Generador: `f2faf71a30783232471de3f95d4279dcc13d3dbda29eacb9df6cede886ab034d`.