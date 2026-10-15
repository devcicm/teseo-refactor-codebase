# Sobre operacional E(P) — contrato agnóstico (v2.3)

Este anexo define **cómo descubrir y congelar las precondiciones de ejecución**
sin asumir lenguaje, runtime, base de datos, framework, despliegue o hardware.

## Principio de activación

Una dimensión operacional sólo forma parte de E(P) cuando existe evidencia de
que el sistema depende de ella. No llenes campos porque aparezcan en una
plantilla. `NO_APLICA` es preferible a inventar una dependencia.

Para cada dimensión activa registra cinco cosas:

1. **Evidencia de dependencia**: qué parte del sistema la usa.
2. **Identidad baseline**: versión/hash/configuración/ruta/contrato suficiente.
3. **Comparador de drift**: exacto, normalizado, compatible, conjunto, etc.
4. **Probe no destructivo**: cómo medirla sin modificar el sistema.
5. **Riesgo si deriva**: qué flujo podría dejar de ser reproducible.

## Taxonomía abierta de dimensiones

No es una checklist obligatoria; es un vocabulario para clasificar lo encontrado.

| Dimensión | Ejemplos posibles | Actívala sólo si... |
|---|---|---|
| EXECUTION_SUBSTRATE | intérprete, VM, runtime, loader | ejecuta/carga el programa |
| TOOLCHAIN_BUILD | compilador, linker, transpiler, generador | el artefacto depende de su salida |
| DEPENDENCY_RESOLUTION | gestor, lockfile, vendor tree | resuelve código/artefactos externos |
| CONFIG_PATHS | config, CWD, rutas, flags | altera qué recursos/contratos usa P |
| PERSISTENT_STATE | SQL/NoSQL/KV/archivos/object store | el flujo lee/escribe estado durable |
| SCHEMA_MIGRATION | schema, versión, migraciones | existe evolución estructural del estado |
| OS_FILESYSTEM | OS, arquitectura, permisos, locale | afecta ejecución observable/reproducible |
| NETWORK_PROTOCOL | DNS, TLS, puertos, protocolo | el flujo depende de comunicación |
| EXTERNAL_SERVICE | API, broker, cache, auth, SaaS | un flujo cruza esa frontera |
| DEVICE_INTEGRATION | dispositivo, driver, SDK | un flujo depende de hardware/periférico |
| GENERATED_ARTIFACT | bundles, código generado, assets | se consume como parte del sistema |
| OTHER | cualquier precondición demostrada | no cabe arriba pero tiene efecto causal |

## Research Gate

Investiga documentación primaria **sólo para las dimensiones activas cuya
compatibilidad sea relevante para una decisión**. Registra componente, versión/
identidad local, fuente, fecha, hecho verificado y decisión que soporta.

No conviertas blogs/issues en verdad normativa cuando exista especificación o
documentación oficial. Si no puede verificarse: `UNVERIFIED`.

## Regla de drift

Para un PURE_REFACTOR:

```text
E_active_before == E_active_after
```

La igualdad no tiene por qué ser byte-a-byte; cada dimensión define su comparador.
Ejemplos: hash exacto de lockfile, versión exacta de toolchain, esquema
normalizado, contrato de servicio compatible, identificador de dispositivo.

Una dimensión de E puede variar deliberadamente sólo como
`ENVIRONMENT_CHANGE`/`MIGRATION`, aislada del refactor y con su propia validación.

## Configuración y secretos

Registra **origen y nombres**, no valores secretos. Ejemplo conceptual:
`DATABASE_URL: env` o `config.production.json: key X`, nunca el secreto.

## Estado durable

Si existe persistencia, primero determina **qué estado real consume el flujo**:
archivo, servidor, namespace, bucket, base, colección, esquema o equivalente.
No supongas que un archivo encontrado es el activo. Congela identidad, estructura
relevante, mecanismo de migración y una prueba de integridad/lectura segura que
sea idiomática para la tecnología detectada.

## Integraciones y dispositivos

Si existen, separa capas y fronteras. Por ejemplo genérico:

```text
[App] -> [Adapter/Client] -> [Protocol/SDK] -> [External System]
```

El baseline debe decir qué artefacto cruza cada frontera y cómo se sabe que la
capa está sana. No presupongas identificadores, callbacks, formatos ni drivers.

## Matriz de E(P)

| Dimensión activa | Evidencia | Baseline | Comparador | Probe | Riesgo de drift |
|---|---|---|---|---|---|
| <tipo> | <archivo/log/test> | <identidad> | <regla> | <read-only> | <flujo> |
