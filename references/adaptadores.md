# Adaptadores tecnológicos opcionales (v2.3)

Los adaptadores implementan el contrato de E(P) para tecnologías detectadas.
**No son requisitos de la skill.** Un adaptador se activa únicamente cuando el
repo/config/ejecución aporta evidencia de esa tecnología.

## Contrato de un adaptador

Todo adaptador debe declarar:

1. `detect`: evidencia objetiva para activarlo.
2. `dimensions`: qué dimensiones de E(P) cubre.
3. `capture`: campos baseline mínimos.
4. `probe`: comandos/lecturas no destructivas.
5. `compare`: reglas de drift.
6. `hazards`: acciones que NO deben ejecutarse durante el refactor.
7. `sources`: documentación primaria necesaria para compatibilidad/versionado.
8. `failure_signals`: síntomas que justifican investigar esa capa.

## Familias de ejemplo — no normativas

### Runtime/VM/intérprete
Puede aplicar a JavaScript runtimes, Python, JVM, .NET, Ruby, PHP u otros.
Captura versión/loader/ABI sólo si el proyecto realmente depende de esos datos.

### Toolchain nativo/compilado
Puede aplicar a C/C++, Rust, Go, Swift u otros cuando compilador, target, libc,
linker o flags formen parte de la reproducibilidad del artefacto.

### Resolución de dependencias
Aplica donde existen manifests, lockfiles, vendor trees, registries o módulos.
Congela los artefactos que el proyecto use realmente; no presupongas npm/pip/etc.

### Persistencia
Puede ser relacional, documento, KV, graph, embedded, archivos, object storage u
otro mecanismo. Captura identidad del estado activo, schema/estructura cuando
exista, migraciones/versionado e integridad con probes propios de esa tecnología.

### Integración de servicios
HTTP/gRPC, colas, brokers, auth, caches, cloud APIs, sockets u otros. Congela el
contrato observable y versiones/protocolos sólo donde sean materialmente relevantes.

### Dispositivos/hardware
Si existe periférico, separa dispositivo → driver/servicio → SDK/protocolo →
adapter de aplicación → dominio. Captura sólo identificadores accesibles y
necesarios; nunca inventes qué datos produce el dispositivo.

### Contenedores/virtualización
Activa sólo si imágenes, base image, runtime de contenedor, mounts o networking
forman parte de cómo se ejecuta el sistema.

## Ejemplo de evidencia que originó esta regla (NO gate)

Un proyecto puede dejar de funcionar después de una refactorización aparente si
cambió una precondición ajena al código: por ejemplo, un runtime incompatible con
un módulo nativo o un estado persistente/schema distinto. Ese patrón causal se
generaliza; la skill no debe quedar ligada al runtime, módulo o motor concreto del
caso histórico.
