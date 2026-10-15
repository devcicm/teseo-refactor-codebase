# Baraja de jugadas Git — orquestación condicional

Cada jugada define pregunta, combinación de comandos, evidencia esperada,
restricciones y una condición de salida. NO ejecutar jugadas por rutina: las
elige la hipótesis y el permiso. Las operaciones de lectura pueden realizarse
sin mutar el repo; las otras pasan por `Execution Governance`.

## CARTA A — Arqueología histórica (READ)

**Pregunta:** ¿qué decisión/estado originó una pieza?

```
 git log --oneline --decorate -- <ruta>
   + git blame -L <inicio>,<fin> <commit> -- <ruta>
   + git show --stat <commit>
   + git show <commit>:<ruta>
                |
                v
    evidencia de historia + contrato actual
```

`blame` atribuye líneas en un commit, no intención ni culpabilidad. Rutas
renombradas o no versionadas requieren búsqueda adicional.

## CARTA B — Identidad y custodia (READ + PREPARE)

**Pregunta:** ¿estoy en el worktree/branch autorizado?

```
 git rev-parse --show-toplevel
   + --absolute-git-dir
   + --path-format=absolute --git-common-dir
   + git symbolic-ref -q HEAD
   + git rev-parse HEAD
   + git status --porcelain=v1 -z
   + git worktree list --porcelain
                     |
                     v
           [WORKTREE GUARD]
              /       \
          permit     BLOCKED
```

Nunca inferir que un nombre de carpeta implica identidad; usar rutas
canónicas, gitdir privado, gitdir común, ref y OID.

## CARTA C — Primera divergencia (READ)

**Pregunta:** ¿qué modificó el comportamiento del flujo?

```
 baseline smoke + refactor smoke
                   |
                divergencia
                   |
 git diff <base>..<refactor> -- <segmento>
   + git log --ancestry-path <base>..<refactor>
   + git show <candidato>
                   |
           hipótesis falsable
                   |
     reproducciones A/B con E(P) controlado
```

No confundir diffs sintácticos con diferencias semánticas. Comparar outputs,
state, orden de eventos y entorno sobre casos representativos.

## CARTA D — Aislamiento causal de commits (DIAGNOSE)

**Pregunta:** ¿cuál commit introdujo el síntoma reproducible?

```
 known GOOD + known BAD + prueba automatizable
                    |
           diagnóstico worktree aislado
                    |
             git bisect start
                    |
       git bisect run <script confiable>
                    |
      primer commit sospechoso + reproducción
                    |
             git bisect reset
```

Sólo si good y bad son comparables en E(P). Códigos de test 0=good,
1..127 excepto 125=bad, 125=skip. No ejecutar scripts del repo sin análisis.
Bisect altera checkout del worktree en que se invoca: prohibido en original y
worktree principal de refactor. `bisect` puede acabar inconcluso.

## CARTA E — Comparar alternativas de transformación (READ)

**Pregunta:** ¿dos series de commits implementan el mismo cambio?

```
 git merge-base A B
   + git diff A...B
   + git range-diff <serie1> <serie2>
                 |
        revisión humana + tests
```

`range-diff` es salida humana, NO API estable para parsear. Distintas series
pueden producir un tree semejante sin preservar la misma semántica.

## CARTA F — Investigaciones de recuperación (READ → autorización)

**Pregunta:** ¿dónde quedó el estado anterior de una referencia?

```
 git reflog show <ref>
   + git show <OID>
   + git diff <OID> <HEAD>
                 |
      plan de recuperación no destructivo
```

Reflog local y sujeto a expiración: no hay garantía de recuperar objetos
perdidos. Git no restaura base de datos o servicios no versionados.

## CARTA G — Reconciliación top-down / bottom-up

**Pregunta:** ¿qué flujos afectados tienen implementación diferente?

```
 capability/workflow W-001
       |
 segment SEG-003 --E12--> función F
       |                        |
 git log -- <archivos>      blame/show/diff
       |                        |
       +--- grafo de relaciones-+
                    |
            evidencia/C(P) tests
```

Si faltan relaciones, marcar UNKNOWN; no reparar según arquitectura inferida.

## Política de elección

Prioriza READ → hipótesis → evidencia → cambios PREPARE autorizados →
verificación → commit. Sólo usar DIAGNOSE si un test reproduce fallo; no usar
rebase/reset para "limpiar" una investigación. Evitar ejecución prolongada si
no hay cobertura adecuada; retornar PARTIAL/BLOCKED.
