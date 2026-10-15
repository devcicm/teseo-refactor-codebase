# Incidente preexistente antes del refactor (v2.3)

Usar cuando un flujo crítico está YELLOW/RED antes del primer cambio.

## Regla causal

No cambies simultáneamente código, entorno y estado para "ver si revive".
Formula hipótesis y modifica/observa una variable por experimento. El objetivo es
identificar causa, no recuperar accidentalmente.

## Procedimiento agnóstico

1. Reproduce el síntoma y conserva error/log/salida exacta.
2. Ubica el fallo en el flow AS-IS: último nodo sano y primer nodo fallido.
3. Enumera las dependencias reales de ese tramo usando E(P) y el diagrama.
4. Para cada dependencia formula una hipótesis falsable.
5. Prefiere pruebas read-only/no destructivas y cambia una variable por vez.
6. Si el fallo apunta a una tecnología concreta, activa su adaptador opcional y
   consulta fuente primaria cuando la compatibilidad/versionado sea material.
7. Sólo marca causa CONFIRMED cuando una prueba aislada la reproduce o elimina.

No existe un orden universal tipo "runtime → DB → hardware". El orden lo dicta
la topología causal observada del sistema.

## Matriz

| Hipótesis | Capa/nodo AS-IS | Evidencia + | Evidencia - | Prueba no destructiva | Resultado |
|---|---|---|---|---|---|
| <causa candidata> | <E#/nodo> | | | | |

## Salida

- `ROOT_CAUSE_CONFIRMED`: prueba causal aislada suficiente.
- `LIKELY`: evidencia fuerte pero falta confirmación causal.
- `UNRESOLVED`: evidencia insuficiente/contradictoria.

Un fix queda fuera del refactor y requiere su propio test de regresión. Después
del fix, reconstruye las partes afectadas de AS-IS/E(P) antes de congelar baseline.
