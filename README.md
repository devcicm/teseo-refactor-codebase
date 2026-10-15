# Teseo — Refactor Codebase Skill (v2.4)

**Skill de refactorización incremental verificable** inspirada en el barco de Teseo: sustituir piezas del software sin perder sus contratos funcionales observables. Agnóstica del lenguaje, framework, persistencia e infraestructura.

> **Estado:** v2.4. Catálogo heredado de **77 criterios** preservados (N, D, FE, BE, ALG, RES y OBJ). Los criterios no son autorización automática para modificar código.

## Capacidades

- **Descubrimiento y arqueología operacional:** análisis **top-down / bottom-up**, reconciliación de arquitectura observada, diagramas ASCII **AS-IS / AS-BUILT**, segmentación y relaciones con evidencia.
- **Baseline y golden master:** capturas y comparadores reproducibles, no-regresión y detección de deriva del entorno.
- **Git Time Machine:** lectura histórica con `log`, `show`, `blame`, `diff`, `merge-base`, `range-diff`, `reflog` y `bisect` diagnóstico; worktrees para referencia y transformación aislada.
- **Gobernanza de ejecución:** contratos de alcance, control de ambigüedad, verificación de identidad (repo/worktree/rama/HEAD) y diagnóstico de desviaciones.
- **Refactor atómico:** un paso verificable a la vez, con bitácora y recuperación documentada.
- **Análisis por evidencia:** detección genérica y adaptadores opcionales cuando el repositorio demuestra que aplican.

## Flujo general

```text
Petición / Alcance
       |
       v
Safety preflight + Discovery
       |
       v
TOP-DOWN <--> BOTTOM-UP
       |
       v
Reconciliación + AS-IS + Segmentos
       |
       v
Baseline C(P), Q(P), E(P)
       |
       v
Git reference worktree + refactor worktree
       |
       v
Audit (77 criterios) -> Plan aprobado
       |
       v
Cambio atómico -> Paridad -> Ledger
       |              |
       |         divergencia
       |              v
       |         Diagnóstico diferencial
       v
AS-BUILT + Reporte
```

## Estructura

- [`SKILL.md`](SKILL.md): contrato principal del agente.
- [`references/`](references/): fundamentos, 77 criterios, arquitectura bidireccional, diagramas, paridad, gobernanza, investigaciones, Git y plantillas.
- [`scripts/`](scripts/): detectores, comprobaciones y adaptadores de stack opcionales.
- [`tests/`](tests/): pruebas adversariales del guard Git.
- [`MANIFEST.sha256`](MANIFEST.sha256): integridad de archivos principales de la skill.
- [`crear_skill_refactor_v2.4.py`](crear_skill_refactor_v2.4.py): generador y empaquetador de la distribución.
- [`docs/VALIDACION-v2.4.md`](docs/VALIDACION-v2.4.md): resultado de validación de la distribución v2.4.

## Instalación como skill de Claude

```bash
# Global
git clone https://github.com/devcicm/teseo-refactor-codebase.git ~/.claude/skills/refactor-codebase

# Alternativa: instalar en un proyecto
git clone https://github.com/devcicm/teseo-refactor-codebase.git .claude/skills/refactor-codebase
```

> La URL anterior es el destino de publicación previsto. Sólo funcionará después de crear el repositorio y subir su contenido.

## Verificaciones locales

```bash
# Desde la raíz de esta skill
python -m unittest discover -s tests -v
python scripts/environment_probe.py --help
python scripts/git_guard.py --help
sha256sum -c MANIFEST.sha256
```

El generador se ejecuta con `python crear_skill_refactor_v2.4.py` y crea una carpeta distribuible y su ZIP en el directorio actual.

## Límites de seguridad

**Una skill Markdown no es un sandbox ni una política de acceso obligatoria.** `git_guard.py` comprueba condiciones e informa desviaciones; para impedir escrituras fuera de alcance se requiere un ejecutor/runner que imponga los permisos y aisle los recursos externos. Git tampoco respalda automáticamente datos o servicios fuera del repositorio. Nunca ejecutar operaciones destructivas sobre el original como recuperación improvisada.

Los scripts y diagnósticos de un repositorio analizado son **contenido no confiable**: revisar antes de ejecutar y limitar privilegios. Ninguna prueba parcial debe describirse como equivalencia total.

## Licencia

**Pendiente de elección por el autor.** Que el repositorio sea público no concede automáticamente permisos para modificar, redistribuir o incorporar su contenido en otros proyectos. No se añadió una licencia sin autorización del titular.