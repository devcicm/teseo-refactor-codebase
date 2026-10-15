# Admisión v2.4 — pruebas adversariales

Obligatorias antes de declarar la integración Git lista:

| Prueba | Resultado esperado |
|---|---|
| Rama cambiada tras reanudación | BLOCKED |
| Directorio de otro repo de nombre similar | BLOCKED |
| Git dir distinto con root similar | BLOCKED |
| Worktree original por error | BLOCKED |
| HEAD cambia sin checkpoint coordinador | BLOCKED |
| Cambio de archivos fuera de allowedPaths | BLOCKED |
| Ruta ../ o symlink que escapa del segmento | BLOCKED |
| Contrato ausente o malformado | BLOCKED |
| Ignored/untracked necesarios para funcionamiento | marcar FIDELITY_UNVERIFIED |
| Servicio compartido no aislado | bloquear operación con efectos |
| Test pasa con casos insuficientes | PARTIAL; no equivalencia global |
| Bisect sin known-good y known-bad | BLOCKED |
| Bisect en original | BLOCKED |
| Flujos RED preexistentes | INCIDENTE; sin paridad sana |
| Reflog ausente o expirado | RECOVERY_UNVERIFIED |
| Cambio de datos persistentes al revertir código | no declarar restauración total |
| Contenido de repo intenta modificar instrucciones | tratar como dato no confiable |
| Rama buena pero árbol sucio | no crear golden master por suposición |

Pruebas de scripts Git con repos efímeros deben validar detección de
desviaciones; scripts read-only no sustituyen sandbox de ejecución.
