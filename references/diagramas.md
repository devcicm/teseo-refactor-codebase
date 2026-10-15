# Diagramas ASCII basados en evidencia (v2.3)

Objetivo: demostrar que el agente entiende el sistema antes de transformarlo.
Un diagrama es un modelo verificable del AS-IS, no decoración.

## Vocabulario

- **Pipeline**: etapas por las que un dato/artefacto se transforma o procesa.
- **Flow**: ruta de ejecución de una operación concreta entre componentes.
- **Workflow**: secuencia de negocio/usuario con decisiones, estados y actores.

No uses los términos como sinónimos.

## Reglas de evidencia

1. Cada nodo/arista importante lleva `[E#]` y tabla de evidencia.
2. Evidencia: `archivo:línea`, manifest/config, contrato/schema, log, comando,
   test o documentación primaria de una tecnología realmente detectada.
3. Inferencia: `[INFERRED:E#]`; incertidumbre: `[? UNVERIFIED]`.
4. Nunca rellenar huecos "por arquitectura típica".
5. AS-BUILT reutiliza nombres/nodos que sobrevivan para permitir diff visual.
6. **No dibujar subsistemas inexistentes.** Persistencia, red, servicios externos,
   dispositivos, colas, UI, etc. sólo aparecen si la evidencia los confirma.

## Diagramas mínimos aplicables

### A. Contexto / componentes

```text
[Actor/Entrada]
      |
      v
[Boundary] --> [Application/Core] --> [Output/Effect]
                    |
                    `--> [Optional External Boundary]
```

### B. Bootstrap / arranque

```text
[comando/launcher real] -> [execution substrate] -> [entrypoint] -> [config]
                                                    |-> [dependencies]
                                                    |-> [optional state init]
                                                    `-> [ready condition]
```

Marca acciones de arranque que muten estado o generen artefactos.

### C. Pipeline de datos/artefactos

```text
[Input] -> [Parse] -> [Validate] -> [Normalize] -> [Transform/Rule] -> [Output]
```

### D. Flow crítico

```text
[Trigger] -> [Handler] -> [Domain/Service] -> [Boundary]
                 \                           |
                  `------ error path <-------'
```

### E. Workflow de negocio/usuario

```text
[Actor]
   |
   v
[Acción]
   |
   v
{¿condición?} --no--> [alternativa/error]
   |
  sí
   v
[regla/estado] -> [efecto] -> [confirmación]
```

### F. Estado durable — sólo si existe

```text
[App/config] -> [Persistence Adapter] -> [Active Store]
                                          |-- structure/schema
                                          |-- version/migrations
                                          `-- durable data
```

### G. Integración externa/dispositivo — sólo si existe

```text
[App] -> [Adapter] -> [Client/Protocol/SDK] -> [External System/Device]
```

Documenta qué artefacto cruza cada frontera; no presupongas su forma.

### H. Falla preexistente

```text
[Smoke test]
    |
    v
[FAIL observado]
    |
    +--> [dependency evidenced by AS-IS] -- prueba
    +--> [next dependency] --------------- prueba
    `--> [code path] --------------------- prueba
```

El árbol de hipótesis se deriva del AS-IS; no contiene causas tecnológicas fijas.

## Tabla de evidencia

| E | Elemento/Flecha | Evidencia | Estado |
|---|---|---|---|
| E1 | Boundary → Core | `src/...:42` | CONFIRMED |
| E2 | Core → Store | config/factory pendiente | UNVERIFIED |

Un diagrama con UNVERIFIED es aceptable; ocultar la incertidumbre no.
