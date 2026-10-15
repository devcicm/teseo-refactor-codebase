# Crosswalk multi-lenguaje

Los criterios son universales; este anexo traduce su DETECCIÓN y su
REFACTOR IDIOMÁTICO a cada lenguaje. Regla: si un lenguaje no está
listado, se razona por paradigma y se añade aquí con formato igual.

## §recursos (RES)

| Lenguaje | Adquisición segura idiomática | Detección de RES-01 |
|---|---|---|
| Python | `with open(...) as f:` | `f = open(...)` sin `with` y sin finally |
| Java | try-with-resources (AutoCloseable) | `.close()` manual; try sin finally; Closeable no gestionado |
| C# | `using` / `await using` (IDisposable/IAsyncDisposable) | Dispose() manual en manos del llamador |
| Go | `defer f.Close()` inmediato tras adquirir | adquirir sin defer en la línea siguiente |
| Rust | RAII: Drop automático por scope | casi imposible por diseño — buscar mem::forget y ciclos de Arc |
| C++ | RAII, unique_ptr/make_unique | new/delete crudos, delete en múltiples returns |
| JS/TS | try/finally, AbortController, [Symbol.dispose] | event listeners sin removeEventListener, timers sin clear |

## §instanciación (OBJ)

| Lenguaje | El `new` antipatrón se ve como | La sustituibilidad se logra con |
|---|---|---|
| Java | `new SqlUserRepository()` en un service | constructor parametrizado, interfaces, framework DI opcional |
| C# | ídem | ídem; `required` + DI integrado |
| JS/TS | `new XMLHttpRequest()` en la lógica cuando el módulo ya estandarizó fetch; `new Dependencia()` acoplada | funciones factory, parámetros por defecto, módulos con inyección ligera |
| Python | instanciar la clase concreta dentro del método de negocio | duck typing + parámetro con default; protocol (typing.Protocol) |
| Go | retornar `&MySQLRepo{}` desde el paquete de negocio | interfaces pequeñas aceptadas como parámetro: `type Store interface { Get(id) }` |
| Rust | `new` no es keyword: el olor es retornar tipo concreto donde se pide trait | `impl Trait`, generics, trait objects (`Box<dyn Store>`) solo donde hay dinámica real |
| PHP | `new` dentro del método del controlador | constructor promotion + inyección |

## §nombres y núcleo (N)

| Smell | Manifestación típica | Refactor idiomático |
|---|---|---|
| N-08 convención rota | Python: mezcla camelCase/snake_case; Go: getters sin prefijo Get; Rust: field público sin criterio | aplicar la guía oficial del lenguaje (PEP8, Effective Go, API guidelines de Rust) |
| N-11 redundancias | `if x == true`, `!= nil` ya filtrado, `then` vacío | el lenguaje tiene su forma canónica; usarla |

## §notas por paradigma

- FUNCIONAL (Haskell, Elixir, F#): DRY de conocimiento aplica igual
  (combinators, una sola definición de la regla); OBJ casi no aplica
  (no hay new de estado); RES se manifiesta como procesos/supervisores
  (un proceso sin supervisor es RES-01 conceptual).
- ORIENTADO A OBJETOS: aplican los 7 dominios completos.
- SISTEMÁTICO/PROCEDURAL (C, Pascal): N, D, ALG, RES aplican; OBJ se
  traduce como "malloc/struct que el módulo esconde" — la
  sustituibilidad es el puntero a función/interfaz manual.
- ORQUESTACIÓN (SQL, Terraform, YAML): D-01 (conocimiento repetido en
  queries/scripts) es el dominio dominante; el refactor idiomático es
  la vista/función/módulo que el motor provee.
