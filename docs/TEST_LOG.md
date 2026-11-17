# Pruebas V0.1 — Registro sin archivos comerciales

## 2026-11-16 — ISO Collector's Edition PAL — PASS

Resultado **reportado mediante captura de PowerShell del usuario**, no validación independiente del archivo original.

- Herramienta: `scripts/inspect_iso.py` V0.1.0
- Sistema: Windows / Python 3.15.2
- Identificación: `SLES-53346` — `target_serial_match=true`
- Región: Europe/PAL
- BOOT2: `SLES_533.46`
- ELF: 32 bits, MIPS
- Punto de entrada ELF: `0x00100008`
- El informe local JSON fue generado.
- **No** se han subido ISO, ELF, datos de juego ni rutas locales.

### Alcance y límite

La fase V0.1 demuestra que el parser puede inspeccionar los metadatos de la edición objetivo. **No demuestra que el ELF sea recompilable, que el juego arranque ni que sea jugable.** Seguimos con el análisis del mapa de memoria y funciones de V0.2.

> Todo progreso futuro se registra por fase, con evidencia y posibles bloqueos.

## 2026-11-16 — V0.2a / segmento ELF32 — PASS

Resultado compartido mediante captura de PowerShell del usuario.

- 10/10 tests sintéticos de V0.1+V0.2a: **OK**.
- BOOT2: `SLES_533.46`; entry point: `0x00100008`.
- 2 segmentos `PT_LOAD`; 1 ejecutable.
- El punto de entrada está en un segmento `PT_LOAD` ejecutable.
- LOAD 0: dirección virtual `0x00100000`, tamaño en memoria **4767872 bytes**, permisos `RWX`.
- LOAD 1: dirección virtual `0x0058C080`, tamaño en memoria **0 bytes**, permisos `RW-`. El informe aún no permite inferir qué representa.
- Informe local: `reporte-v02-local.json`, generado correctamente.
- No se han publicado archivos del juego. **Esto no representa funciones decompiladas, recompilación ni arranque nativo.**

## Preparación V0.2b — Extracción privada de ELF

Se publicó `scripts/export_local_elf.py` y tres pruebas sintéticas de exportación para generar el ELF **solo localmente**, sin sobrescribir un archivo existente. Pruebas locales aisladas del extractor: 3/3 PASS; falta probar la edición comercial en el equipo del usuario.
