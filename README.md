# Teseo — Refactor Codebase Skill v2.5

Skill de **refactorización incremental con trazabilidad y comprobación de contratos**, fundamentada en el barco de Teseo. Independiente del lenguaje, framework, base de datos o sistema operativo analizado.

## Evolución v2.5

El catálogo **77 criterios originales** (N 10, D 6, FE 24, BE 22, ALG 5, RES 5, OBJ 5) se conserva sin renumeraciones. V2.5 agrega guardas ejecutables de alcance e integridad, pero **no implementa automáticamente los 77 criterios como transformaciones**.

- Arqueología top-down/bottom-up, diagramas ASCII AS-IS/AS-BUILT, segmentación y clasificación de evidencias.
- Baseline C(P), Q(P), E(P), análisis diferencial e integral de cambios acumulados.
- Máquina del tiempo de Git, worktrees de referencia/refactor, historia y diagnóstico.
- Discovery pasivo sin lanzar herramientas externas detectadas y lectura confinada contra symlinks.
- Git guard resistente al fsmonitor configurado en el repositorio y matcher de rutas por componentes.
- Runner acotado POSIX `teseo_runner.py`: escritura atómica de **archivo existente**, control de versión/hash, autorización con expiración, registro PREPARED/COMMITTED, y recuperación del before-image.
- Verificación independiente *conceptual* de invariantes observados y validación estructural de Evidence Graph.

## Estructura

```text
SKILL.md
MANIFEST.sha256
references/                 # 77 criterios, fundamentos, gobernanza y v2.5
scripts/
  path_policy.py            # rutas seguras / matcher sin sobrealcance
  discover.py               # candidatos del código; nunca pruebas concluyentes
  environment_probe.py      # inventario PASIVO del entorno
  git_guard.py              # identidad Git; no sandbox
  teseo_runner.py           # primitivas de edición y recuperación acotadas
  verify_invariants.py      # comparadores de invariantes observados
  evidence_graph.py         # esquema / relaciones de evidencia
  adapters/                 # ejemplos tecnológicos opcionales
 tests/                     # pruebas sintéticas y adversariales
crear_skill_refactor_v2.5.py # empaquetador reproducible
crear_skill_refactor_v2.4.py # generador original, conservado por historia
```

## Instalación

```bash
git clone https://github.com/devcicm/teseo-refactor-codebase.git
mkdir -p ~/.claude/skills
cp -a teseo-refactor-codebase ~/.claude/skills/refactor-codebase
```

La versión empaquetada contiene exclusivamente `SKILL.md`, `references/`, `scripts/`, `tests/` y `MANIFEST.sha256`. También puede instalarse en `.claude/skills/refactor-codebase/` de un proyecto.

## Verificación y empaquetado

```bash
python -m unittest discover -s tests -v
python crear_skill_refactor_v2.5.py --check
python crear_skill_refactor_v2.5.py
(cd dist/refactor-codebase && sha256sum -c MANIFEST.sha256)
```

Para un cambio autorizado de fuentes, primero ejecutar tests y luego `python crear_skill_refactor_v2.5.py --sync-manifest`; CI **no edita** el árbol del repositorio ni hace push automático.

## Frontera de confianza / limitaciones

Una skill Markdown no impone permisos OS, y ejecutar el guard voluntariamente no impide escrituras directas. El runner sólo es un mecanismo de control cuando el **contrato, directorio de control y permisos pertenecen a un coordinador que el agente no puede modificar**. La herramienta no aísla servicios o datos externos ni demuestra equivalencia total con pruebas parciales. `RECOVER` restaura before-images de archivos existentes; no revierte transacciones externas.

Especificación y ejemplo de contrato: [`references/gobernanza-v2.5.md`](references/gobernanza-v2.5.md).

## Licencia

**Pendiente de elección por el titular**. Un repositorio público no implica permiso de redistribución o modificación por terceros.
