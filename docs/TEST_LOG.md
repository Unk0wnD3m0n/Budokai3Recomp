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
