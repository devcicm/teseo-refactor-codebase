# Validación técnica — Teseo v2.5.0-rc.1

**Fecha:** 2026-10-14. **Base:** Teseo v2.4 (original local preservado y worktree separado). **Cambios:** v2.5 en `feat/teseo-v2.5`.

## Paridad documental

- `references/criterios.md`: idéntico al de v2.4; 77 IDs N10, D6, FE24, BE22, ALG5, RES5, OBJ5.
- `crear_skill_refactor_v2.4.py`: conservado por compatibilidad histórica.
- Fuentes v2.5 canónicas en árbol Git; nuevo empaquetador sólo lee las fuentes y verifica manifiesto.

## Pruebas ejecutadas localmente

| Grupo | Resultado | Alcance |
|---|---|---|
| Suite original Git | 12/12 PASS | preflight, ramas, HEAD, symlink, alcance |
| Falsificación PATH | PASS | inventario no ejecuta el binario sintético |
| Symlink en discovery | PASS | no lee contenido fuera del directorio |
| Glob por componentes | PASS | `src/*.py` no incluye subdirectorios |
| `core.fsmonitor` sintético | PASS | no ejecuta monitor externo durante status |
| Runner: escritura atómica/idempotencia | PASS | un archivo regular, worktree descartable |
| Runner: recuperación y evento PREPARED | PASS | restaura before-image bajo precondiciones |
| Runner: caducidad, HEAD, alcance, hash | PASS | BLOCKED en desvíos |
| Evidence Graph | PASS | estructura y referencias verificadas, sin causalidad inferida |
| Comparadores | PASS | FAIL crítico bloquea, falta de evidencia PARTIAL |
| Suite completa | **29/29 PASS** | Python unittest sobre fixtures sintéticos |
| MANIFEST SHA-256 | PASS | se genera desde fuentes v2.5 y verifica paquete |
| ZIP determinista | PASS | reproducible sobre la misma fuente |

## Identidad de versión auditada

La distribución candidata se identifica en `VERSION.json` como `2.5.0-rc.1`;
el runner usa el protocolo `teseo-v2.5`, admitido ahora explícitamente por
`git_guard.py` junto al protocolo histórico `teseo-v2.4`. El catálogo se
mantiene con cuenta 77 + SHA-256 y existe `CAPABILITIES.json` para separar
promesas, implementación y cobertura de pruebas. Para pruebas actualizadas,
consultar `scripts/version_audit.py --self-check` y suite actual de tests.

## Límites / NO VERIFICADO

- La suite verifica herramientas y fixtures; **NO** demuestra equivalencia completa de aplicaciones ajenas.
- No se ha probado un runner con aislamiento fuerte de principal/OS, porque esta ejecución local no dispone de un coordinador independiente. No prometer enforcement universal.
- No se ha validado recuperación de estados externos, servicios ni transacciones distribuidas.
- No se ha implementado enforcement de commits, renombrados multiarchivo, movimiento de ramas ni concurrencia distribuida.
- No se han ejecutado los 77 criterios como analizadores automáticos; son catálogo de auditoría.
- El CI remoto de GitHub se verifica por separado tras publicar; pruebas locales no implican CI remoto correcto.

## Comandos reproducibles

```bash
python -m unittest discover -s tests -v
python crear_skill_refactor_v2.5.py --check
python crear_skill_refactor_v2.5.py
(cd dist/refactor-codebase && sha256sum -c MANIFEST.sha256)
```
