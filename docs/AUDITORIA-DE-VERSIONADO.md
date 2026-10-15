# Auditoría de coherencia de versiones y propósito — Teseo 2.5.0-rc.1

**Fecha:** 2026-10-14. **Alcance:** evolución candidata de la rama `feat/teseo-v2.5`; no altera `main` ni declara una release estable.

## Contradicciones detectadas y corrección

| Superficie | Hallazgo AS-IS | Tratamiento AS-BUILT | Verificación |
|---|---|---|---|
| Identidad de release | Etiqueta `v2.5` sin distinción entre desarrollo y versión final | `VERSION.json` = `2.5.0-rc.1`, canal `release_candidate`; el empaquetador usa el valor, no un nombre hardcoded | `scripts/version_audit.py --self-check` + generador |
| Protocolo de ejecución | `teseo_runner.py` esperaba `teseo-v2.5`, mientras `git_guard.py` aceptaba `teseo-v2.4`; el runner sustituía temporalmente la versión | La compatibilidad del guard se declara y comprueba (`v2.4` y `v2.5`) y el runner ya no reescribe el protocolo | Tests original/runner y contrato de versión |
| Documentación histórica | Referencias v2.2, v2.3 y v2.4 bajo distribución v2.5 parecían contradicciones | Se conservan como procedencia histórica; `references/versionado-y-proposito.md` declara el significado de cada identidad | Revisión de documentos y self-check |
| Catálogo | Se mencionan 78 IDs incluyendo `N-01` retirado, pero hay 77 criterios **activos** | `criteria.count=77`, SHA del archivo; excluir sólo `N-01` en recuento de vigentes | Test explícito de catálogo |
| Capacidades / propósito | La documentación enumera procedimientos que no son ejecuciones automatizadas | `CAPABILITIES.json` distingue `TESTED_SCOPE`, `IMPLEMENTED_LIMITED`, `DOCUMENTED_PROCEDURE`, `NOT_IMPLEMENTED` | Verificación de existencia y estado; fixtures separados |
| Proyecto a refactorizar | Sin gate explícito para comparar propósito anunciado y arquitectura real o versiones activas vs declaradas | Guía agnóstica `VERSION-PURPOSE-AUDIT.md` y `version_audit.py --project` como discovery estático; runtime queda `UNVERIFIED` | Pruebas estáticas y adversariales |

## Fuente de verdad y restricciones

1. `VERSION.json` contiene la versión **de la distribución**, el protocolo runner y fingerprint del catálogo. Cambiar un archivo no constituye por sí solo un release.
2. `CAPABILITIES.json` es una declaración auditable. Sus referencias a scripts no significan cobertura universal de seguridad o integración. Las pruebas indicadas sólo respaldan el alcance descrito.
3. No se renombra históricamente `crear_skill_refactor_v2.4.py`, los anexos antiguos ni `docs/VALIDACION-v2.4.md`: alterar historia para ocultar versiones anteriores sería incorrecto.
4. La rama candidata conserva Git Time Machine y los 77 criterios de Teseo. El versionado de programas ajenos **se descubre por evidencia**, sin imponer SemVer ni Python a todos los proyectos.
5. La nueva compuerta no ejecuta programas del proyecto ni afirma que haya probado compatibilidad operativa. Los estados reportados en `--project` son `DECLARED_CANDIDATE` y `UNVERIFIED`.

## Diferencia entre lo declarado y lo comprobable

```
PROPOSITO DECLARADO (README / SPEC)
                 |
                 v
CAPACIDAD ALEGADA ---[EVIDENCIA]---> IMPLEMENTACION
                 |                         |
                 v                         v
 VERSION PUBLICADA/DECLARADA        CONTRATOS / TESTS
                 \                        /
                  v                      v
               RECONCILIACION
                   |
       +-----------+-----------+
       |           |           |
     VERIFIED    PARTIAL    CONTRADICTED
                   |
            VERSION-PURPOSE GATE
                   |
         REFACTOR / BLOCKED / REPORT
```

La ausencia de evidencia suficiente no autoriza afirmar que una función no existe. Las pruebas no son equivalencia total. El desarrollo de un proyecto puede emplear otro esquema de versionado; su propia política manda.

## Proceso de promoción

`2.5.0-rc.1` → auditoría y CI en PR → aceptación explícita → `2.5.0` en cambio posterior con revalidación → tag inmutable y release firmado cuando se decida publicarlo. Nunca etiquetar el commit candidato como release final sin cambios de metadatos y nueva validación.

## Límites

El guard no intercepta otras escrituras, el runner no impone sandbox OS, `version_audit.py` no verifica versiones reales de procesos, y la comparación de propósitos necesita evidencia manual/dinámica. Todas estas limitaciones se conservan expresamente para evitar promesas engañosas.
