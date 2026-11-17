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

## 2026-11-16 — V0.2b / extracción privada de ELF — PASS

Validación mediante captura de PowerShell aportada por el usuario, sin acceso al binario.

- **13/13 pruebas sintéticas** superadas en Windows.
- Extracción local correcta desde ISO propia SLES-53346; primer intento usó una ruta incorrecta y falló sin modificar datos, segundo intento PASS.
- Archivo producido solo localmente: `SLES_533.46.elf`.
- Tamaño: **3,330,608 bytes**.
- SHA-256: `74c892105a532309d33e473f82ed712ea671c85d6cf36b7078aada0f138510ca` (coincide con la medición de V0.1).
- No se publicaron datos comerciales ni archivo ELF.

**Resultado**: ya se puede empezar a inspeccionar el ejecutable en Ghidra localmente. No se han localizado todavía funciones del juego ni realizado recompilación nativa.

## 2026-11-16 — V0.2c / importación en Ghidra — PASS parcial

Según captura del usuario del diálogo `About SLES_533.46.elf`:

- Ghidra **12.2**; importación del ELF correcta.
- Language ID `r5900:LE:32:default (1.4)`; procesador **MIPS-R5900**, little-endian, 32 bits.
- Extensión `ghidra-emotionengine-reloaded` seleccionada como fuente del lenguaje y procesador.
- ELF original image base: `0x00100000`.
- SHA-256 visible coincide con la extracción local y el análisis V0.1.
- Estado **Analyzed: false**; 0 instrucciones, 1 función antes del análisis automático. Es normal al importar.
- **Pendiente**: ejecutar Auto Analyze y comprobar número de funciones e instrucciones. El reconocimiento de la arquitectura no demuestra una recompilación funcional.

No se almacenaron rutas privadas ni bytes comerciales.

## 2026-11-16 — V0.2c / Ghidra Auto Analyze — PASS

Resultado aportado mediante captura `About SLES_533.46.elf` en Ghidra 12.2 tras el análisis automático:

- Procesador: `MIPS-R5900` (Language `r5900:LE:32:default (1.4)`), little-endian, 32 bits.
- `Analyzed: true`.
- Instrucciones identificadas: **544,078**.
- Funciones identificadas: **7,328** (candidatas; no validadas individualmente).
- Símbolos: **9,823**.
- Datos definidos: **19,743**.
- Bloques de memoria: 19.
- ELF original image base: `0x00100000`.
- SHA-256 del ejecutable coincide con registros anteriores.
- Se omitieron rutas privadas y no se publicó ELF ni códigos extraídos.

**Interpretación**: análisis estático realizado; el recuento no implica que todas las funciones sean válidas ni que el juego pueda recompilarse ya. Siguiente objetivo: exportar mapa TOML/CSV para PS2Recomp usando su script oficial, manteniendo la exportación local.

## 2026-11-16 — V0.2d / exportación Ghidra PS2Recomp — REPORTADA, pendiente de comprobación

El usuario confirma que obtuvo los dos archivos de salida TOML y CSV de `ExportPS2Functions.java`. No se han visto ni leído esos archivos ni la consola final del exportador. **Siguiente verificación local**: comprobar que ambos existen, tienen tamaño mayor que cero, que el CSV contiene registros y que el TOML incluye una sección `[general]`. No subir los archivos ni compartir rutas locales.
