# Seguridad de despliegue

Este proyecto incorpora controles mínimos de seguridad para preparar un despliegue profesional antes de llevarlo a producción.

## CI/CD con validación automática

El repositorio incluye flujos de GitHub Actions para validar automáticamente:

- pruebas del backend
- compilación del frontend
- auditoría de dependencias
- escaneo de secretos
- cumplimiento de reglas de seguridad antes de permitir flujos de producción

Archivos relevantes:

- `.github/workflows/ci-security.yml`
- `.github/workflows/production-gate.yml`

## Análisis de dependencias

Se ejecutan revisiones periódicas con Dependabot y auditorías directas:

- Python: `pip-audit -r backend/requirements.txt`
- Node: `npm audit --audit-level=high`

Esto ayuda a detectar paquetes con vulnerabilidades conocidas antes de producir un release.

## Escaneo de vulnerabilidades

Además del análisis de dependencias, se realiza un escaneo de secretos con Gitleaks para detectar credenciales, tokens y valores sensibles en el historial del repositorio.

## Revisión manual antes del merge a producción

El flujo `production-gate.yml` usa un entorno GitHub llamado `production`.

Esto exige que el responsable de despliegue apruebe la promoción antes de continuar con el lanzamiento. En la UI de GitHub se debe configurar:

- proteger la rama `main`
- exigir revisión de pull requests
- requerir aprobaciones antes del merge a producción
- configurar approval reviewers en el entorno `production`

## Hardening de contenedores

Se han aplicado medidas mínimas para reducir la superficie de ataque del despliegue:

- backend y frontend ejecutan como usuarios no privilegiados
- no se usa la cuenta `root` dentro de los contenedores
- se evita la instalación de dependencias con privilegios innecesarios
- se recomienda mantener imágenes base actualizadas y pinadas a versiones conocidas

## Dependencias y CVE

El proceso de seguridad debe incluir:

- revisión semanal de dependencias con Dependabot
- auditoría de paquetes con `pip-audit` y `npm audit --audit-level=high`
- revisión de todas las librerías con vulnerabilidades conocidas (CVE)
- bloqueo del despliegue si una dependencia crítica o alta permanece sin remediar

## Proceso de patching

1. Se revisan alertas de seguridad cada semana.
2. Las vulnerabilidades críticas y de alta severidad se tratan con prioridad inmediata.
3. En caso de CVE en un paquete activo, se actualiza la dependencia o se aplica un parche mínimo en el mismo sprint.
4. Si la actualización requiere cambios de compatibilidad, se documenta el riesgo y se valida en ambiente de pruebas.
5. Se ejecutan las pruebas automáticas y la auditoría de dependencias antes del merge.
6. Se registra la corrección en el changelog del release y en la bitácora del responsable de despliegue.

## Recomendaciones operativas

- no commitear archivos `.env` reales
- usar secretos en GitHub Actions o proveedores de secret management
- mantener `main` protegido
- revisar el changelog y PR antes del despliegue
- validar variables de entorno y certificados TLS en staging antes de producción
