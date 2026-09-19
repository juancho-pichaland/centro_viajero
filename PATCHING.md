# Proceso de patching y mantenimiento de seguridad

Este documento define el procedimiento mínimo para mantener el proyecto actualizado y seguro antes de cualquier despliegue a producción.

## Objetivo

Reducir la exposición del sistema a vulnerabilidades conocidas en dependencias, imágenes base y paquetes del stack.

## Política de actualización

- Dependencias de Python y Node.js se revisarán al menos una vez por semana.
- El proyecto usará Dependabot para detectar actualizaciones y PRs de seguridad.
- No se fusionará un cambio a producción si existe una vulnerabilidad de severidad alta o crítica sin remediar.
- Las dependencias con CVE deben evaluarse dentro del mismo sprint de trabajo.

## Severidades y tiempos de corrección

- Crítica: corrección inmediata, idealmente en 24-72 horas.
- Alta: corrección en la siguiente iteración de despliegue o máximo 7 días.
- Media: corrección antes del siguiente release programado o en un máximo de 30 días.
- Baja: revisar en la siguiente tanda de mantenimiento y documentar si no aplica.

## Requisitos antes de merge

Antes de aprobar una rama hacia producción se debe comprobar:

1. que la auditoría de dependencias no reporta vulnerabilidades críticas o altas sin excepción
2. que todas las pruebas relevantes pasan
3. que el build del frontend y backend funciona
4. que la imagen Docker se construye sin fallos
5. que no existen secretos reales en el repositorio

## Procedimiento de emergencia

Cuando aparezca una CVE activa de alto impacto:

1. crear una rama de emergencia
2. actualizar o parchear la dependencia afectada
3. ejecutar la auditoría y pruebas
4. documentar el riesgo y la corrección
5. desplegar solo tras aprobación del responsable

## Registro

Cada parche debe dejar constancia de:

- paquete afectado
- severidad de la vulnerabilidad
- versión corregida
- fecha de aplicación
- responsables de validación
- enlace al PR o release asociado
