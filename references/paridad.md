# Paridad, normalización y comparadores (v2.3)

Este anexo define CÓMO demostrar que un paso conserva C(P) sin convertir el
golden master en una comparación frágil. La normalización es parte del
contrato de prueba y debe quedar documentada.

## Regla 1 — comparar con el comparador más estricto que sea correcto

1. `exact`: bytes/texto/valor idéntico. Preferido por defecto.
2. `normalized`: igualdad tras una normalización declarada y limitada.
3. `ordered`: misma secuencia y valores.
4. `unordered`: mismo multiconjunto cuando el contrato NO garantiza orden.
5. `schema`: misma forma/tipos/campos cuando valores son deliberadamente
   variables y el contrato es estructural.
6. `numeric_tolerance`: solo si el dominio admite tolerancia explícita;
   registrar epsilon y por qué.
7. `resource_non_regression`: para Q(P), compara una métrica con una relación
   (`<=`, estabilidad, ausencia de crecimiento), no necesariamente igualdad.

## Regla 2 — nondeterminismo permitido no significa campo irrelevante

Candidatos típicos: timestamps de creación, UUIDs generados, paths temporales,
puertos efímeros, tokens nonce, duración medida. Antes de ignorarlos responde:
"¿un consumidor puede depender legítimamente de este valor, su formato, orden o
relación con otros campos?" Si sí/no se sabe, NO normalizar.

## Regla 3 — normalizadores pequeños y auditables

Cada normalizador declara: `campo/patrón`, `transformación`, `justificación`,
`alcance` y un contraejemplo que NO debe normalizar. No usar regex globales que
borren diferencias arbitrarias.

## Regla 4 — errores también son contrato

Congelar éxito Y error: status/protocolo, shape, códigos de negocio y campos
consumidos. Un cambio "más correcto" de 200 a 4xx es cambio de C(P), no paridad.

## Regla 5 — baseline inmutable durante un paso

Si una prueba falla, no se edita el baseline para hacerla verde. Se revierte o
se reclasifica el cambio. Un baseline solo se regenera como operación explícita
fuera del paso de refactor y con justificación documentada.


## Regla 6 — paridad del experimento exige E activo estable

Cada dimensión activa de E(P) declara su propio comparador. Ejemplos de clases
de comparador, no de tecnologías:

- `environment_exact`: identidad exacta cuando cualquier cambio invalida el
  experimento (p. ej. hash/version/config contractual).
- `environment_normalized`: igualdad tras normalización explícita de valores no
  contractuales.
- `compatibility_constraint`: no exige identidad, pero sí satisfacer una
  restricción documentada de compatibilidad.
- `state_structure_exact`: estructura/versionado del estado durable sin drift
  cuando el refactor no incluye migración.
- `integration_contract`: misma frontera/protocolo observable para una
  integración externa o dispositivo confirmado.

Un test funcional verde con una dimensión activa de E en FAIL no demuestra que
el refactor sea seguro: cambió más de una variable.

## Regla 7 — preservar la identidad del estado/recurso correcto

Si un flujo usa estado durable, configuración por ruta, recurso externo o
artefacto generado, identifica **el recurso efectivo que la aplicación consume**,
no uno encontrado por nombre. Congela la identidad mínima necesaria (ruta,
namespace, endpoint, hash, versión o equivalente idiomático) para detectar que el
refactor no cambió accidentalmente de recurso.
