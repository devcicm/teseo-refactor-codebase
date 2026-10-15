# Arqueología bidireccional y segmentación

## Dos perspectivas, una sola realidad verificable

```
 TOP-DOWN                       BOTTOM-UP
 capacidad C-01                 funciones + I/O + efectos
     |                                    |
 workflow W-01                  módulos y relaciones
     |                                    |
 contratos K-01                 segmentos SEG-01
     |                                    |
     +------------- evidencia -------------+
                         |
                 [RECONCILIACIÓN]
                         |
          OBSERVED / INFERRED / UNKNOWN
                         |
           cobertura concreta por flujo
```

No imponer patrón arquitectónico ideal. La falta de convergencia no autoriza
crear dependencias nuevas; registrar incertidumbre y bloquear el alcance cuya
seguridad dependa de una inferencia no probada.

## Reflexión y recursión

- Por cada hipótesis, buscar al menos una refutación o contraejemplo.
- Seguir dependencias con control de nodos visitados, profundidad y presupuesto
  de contexto, e informar UNRESOLVED al alcanzar límites.
- Correlación de cambios y fallas es una pista, nunca prueba de causalidad.
- Segmentar por capacidad/contrato y mantener lista de archivos compartidos;
  nunca asumir que un archivo pertenece exclusivamente a un workflow.

## Identidad de segmento y estado

```
SEG-001  -> workflow W-001 -> contrato K-001
   |              |                |
   +------ E-003 --+-------- test T-014
   |
   +--> archivo A:20-80 [OBSERVED]
   +--> módulo B      [INFERRED; evidencia pendiente]
```

Cada paso apunta a un criterio del catálogo existente, una ruta autorizada,
contratos afectados, diagramas AS-IS/AS-BUILT, commit y evidencia. No crear
criterios nuevos para esta capa: es gobernanza transversal.
