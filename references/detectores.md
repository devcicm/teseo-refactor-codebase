# Discovery Pass y detectores objetivos (v2.3)

Objetivo: reducir costo de auditoría sin reducir cobertura. El Discovery Pass
NO confirma smells arquitectónicos; produce candidatos y evidencia para decidir
dónde profundizar.

## Pass A — inventario determinista

- manifests/build: package.json, pyproject.toml, requirements*, *.sln/*.csproj,
  pom.xml/gradle, go.mod, Cargo.toml, composer.json, Gemfile, Makefile, Docker*.
- extensiones y volumen por lenguaje.
- tests por convenciones del stack.
- entrypoints y archivos de config.
- archivos muy grandes (señal, no hallazgo).

## Pass B — patrones candidatos

Búsquedas textuales/AST pueden candidatear: secretos/URLs, `innerHTML`,
`==`, `var`, `readFileSync`, `console.log`, `new` en loops, listeners/timers,
archivos `copy/final/v2`, etc. Una coincidencia NO equivale a CONFIRMED.

## Pass C — expansión contextual

Por cada candidato, inspecciona definición + consumidores + tests + frontera
externa. Los criterios D-01/D-02/D-04, N-06/N-07 y OBJ-01 requieren esta fase;
no deben confirmarse por grep.

## Repos grandes

Prioriza por: entrypoints → fronteras externas → módulos de alto fan-in →
hotspots de cambio si git está disponible → candidatos objetivos. Excluye
`node_modules`, `.git`, `vendor`, artefactos compilados y dependencias vendorizadas
salvo que formen parte explícita del alcance.

## Salida Candidate Map

Por archivo/módulo: stack, rol inferido, criterios candidatos, evidencia,
confianza y razón para profundizar. El Candidate Map es índice de auditoría,
no una lista de cambios autorizados.


## Pass 0 — huella operacional antes del análisis de smells

Antes de confirmar candidatos construye una primera lista de **dimensiones
candidatas de E(P)** a partir de evidencia: sustrato de ejecución/toolchain,
artefactos de resolución de dependencias, configuración/rutas, estado durable,
OS/filesystem/red, integraciones externas, dispositivos y artefactos generados.

No todas aplican. Una coincidencia en un manifest, extensión, import o archivo
produce una **pregunta/evidencia candidata**, no activa automáticamente un gate.
Activa una dimensión sólo después de seguirla hasta un flujo real del AS-IS.

Cuando una tecnología concreta quede confirmada, carga el adaptador opcional
correspondiente o deriva uno usando `references/adaptadores.md`.
