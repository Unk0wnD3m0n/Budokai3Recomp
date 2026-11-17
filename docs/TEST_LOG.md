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

## 2026-11-16 — V0.2d / validación local de exportación — PASS (estructura)

Verificado mediante captura de PowerShell del usuario:

- `budokai3-functions.csv`: **1,831,275 bytes**; encabezado `Name,Start,End,Size`.
- **45,170 registros CSV** con `Import-Csv`, incluyendo posibles etiquetas/puntos de entrada adicionales.
- `budokai3-functions.toml`: **2,579 bytes**; sección `[general]` en línea 9.
- Archivos guardados en raíz local del proyecto; no publicados en GitHub.
- Los errores previos de `Import-Csv` se debían a una ruta diferente; comando corregido ejecutado correctamente.

**Límite:** no se han validado todas las direcciones/límites ni las rutas `general.input` y `ghidra_output`. Los 45,170 registros no significan 45,170 funciones únicas válidas. La recompilación C++ no ha comenzado.

## 2026-11-16 — V0.3 / primera ejecución de PS2Recomp — FINALIZÓ CON DIAGNÓSTICOS

Según captura de consola x64 Native Tools:

- La ejecución del recompilador terminó e imprimió literalmente `Recompilation completed successfully`.
- Aparecieron **múltiples errores** `[error] unhandled_instruction`, incluyendo `SPECIAL`, `COP0`, `REGIMM`, `FPU`.
- Se repiten errores en `sub_0042C998`, direcciones cercanas a `0x0042CAxx`; se observó también advertencia de `control-flow` por saltos no resueltos.
- **No se ha verificado** el directorio de salida ni cuántos archivos C++ existen; no se ha compilado código generado ni ejecutado Budokai 3 nativamente.
- Se requiere distinguir instrucciones no soportadas de posibles **datos mal clasificados como código / entradas sintéticas** del mapa CSV de Ghidra.

**Estado:** herramienta ejecutó la etapa de traducción hasta su mensaje de fin; recompilación funcional y calidad del C++ **pendientes de validación**. El mensaje de éxito no cancela los diagnósticos.

## 2026-11-16 — V0.3 / generated C++ output verified — PASS (artifact existence)

User ran read-only Python check of local TOML `[general].output`; output:

- Configured output is **outside the project repository**, directly under the local user's home in an `output` directory. Initial search in project folder was therefore mistaken.
- `EXISTE: True`.
- `ARCHIVOS CPP: 5896`.
- `REGISTER: True` for `register_functions.cpp`.
- This **verifies C++ files were generated**; it does not verify compilation, correctness, or runtime.
- Remaining blocker: many `unhandled_instruction` messages in prior run, with suspected misclassification of ELF bytes/labels; inspect without executing or distributing commercial code.

**Next:** read-only verify generated headers and file summary; keep generated C++ private and never commit it to GitHub.

## 2026-11-16 — V0.3 triage / `sub_0042C998` — evidence of misclassified data

Ghidra Listing screenshot at `0x0042C998` shows a **string data item**, symbol `s_amMc.c_0042c998`, directive `ds "amMc.c"`, preceded near `0x0042C980` by `"MC: sceMcInit error\\n"`, followed by untyped zero bytes from `0x0042C9A0`. These are not displayed as R5900 instructions.

PS2Recomp had reported many `unhandled_instruction` diagnostics inside a generated function named `sub_0042C998`; likely the recompiler treats non-code data as code in at least this region. **Do not yet attribute it specifically to the Ghidra CSV**; `sub_...` names can arise from heuristics too. Verify whether the CSV contains a start at `0x0042C998` or a covering range before modifying maps. Keep ELF/TOML/CSV and generated C++ local.

## 2026-11-16 — V0.3 / CSV overlap root-cause triage

User screenshot of read-only PowerShell confirms **one CSV record covers** `0x0042C998`: `entry_0042c020`, `0x0042C020` through `0x0042D000` (end-exclusive), `Size=4064`. `0x0042C998` itself not a CSV start. Generated file `sub_0042C998_0x42c998.cpp` exists (one match). Ghidra Listing at that address shows `ds "amMc.c"` — text data.

This confirms a too-broad pseudo-entry overlaps non-code; it does **not prove** which heuristic produced `sub_0042C998`. Inspect output and map fallback processing. No data, ELF or generated C++ was committed.

## 2026-11-16 — V0.3 — C++ sospechoso inspeccionado (lectura local)

Captura PowerShell del usuario confirmó `sub_0042C998_0x42c998.cpp` (104812 bytes) en carpeta privada de salida. Cabecera generada: `// Function: sub_0042C998` y `// Address: 0x42c998 - 0x42d000`. Includes de runtime (`ps2_runtime.h`, `ps2_recompiled_functions.h`, etc.). En Ghidra la dirección `0x42c998` sigue siendo `ds "amMc.c"` (cadena de texto), no comienzo de una función legítima identificada. 

Se inspeccionó el parser upstream `ran-j/PS2Recomp`: combina datos de CSV con funciones halladas heurísticamente y asigna límites de funciones, de modo que **todavía no está demostrado el origen exacto de `sub_0042C998`**. La entrada CSV `entry_0042c020` abarca hasta `0x42d000`, incluyendo texto, por lo que hay evidencia de alcance excesivo. Pendiente inspeccionar `0x42c020` en Ghidra y aislar si la región es datos/código mixtos. Ningún archivo del juego ni código generado se publicó.

## 2026-11-16 — V0.3 / registration confirms generated ghost function

PowerShell screenshot: `register_functions.cpp` size **31,561,961 bytes** and `sub_0042C998_0x42c998.cpp` size **104,812 bytes**, both LastWriteTime **2026-11-16 20:47:33 (local)**. In function table, entry for `0x42C020` refers to `sub_004249F0_0x4249f0`; entries at `0x42C998` onwards refer to `sub_0042C998_0x42c998`. The ghost function is in the output registry, not just a leftover file. Upstream parser merges ELF, Ghidra CSV, and heuristically discovered entry targets; precise source of this entry **not proven**. Prior Ghidra screenshot shows it starts at string `ds "amMc.c"`. Need confirm map-loading diagnostics and examine function ownership before any destructive changes. No proprietary bytes or generated C++ committed.

## 2026-11-16 — V0.3 / Root-cause candidate: configured CSV does not exist

User read-only TOML and filesystem check: `ELF EXISTE: True`, `CSV EXISTE: False`, `ghidra_output=C:\\Users\\Juan\\budokai3-functions.csv`. The actual CSV was previously confirmed in the desktop project's root. Therefore **the first recompilation did not have access to the intended CSV at the configured path**. Heuristic fallback is a strong explanation for ghost function `sub_0042C998`, but the exact input-map-loading behavior needs confirmation by a fresh log. Planned safe remediation: back up TOML, correct CSV path, set separate private output directory to avoid mixing generated files, revalidate, then rerun and inspect diagnostics. No game data or generated source should be published.

## 2026-11-16 — V0.3 / re-run with corrected CSV path: MAP LOADED

User supplied two matching log lines from the second private recompilation: at line **530**, `[info] ghidra-map - Loaded 45170 functions from Ghidra map`; at line **8180**, `Recompilation completed successfully`. This verifies the fixed TOML config now provides Ghidra map input and that PS2Recomp reached completion. Does **not** validate generated C++ correctness or runtime. New output count and ghost function status not yet received. Next: count .cpp files and unhandled_instruction messages in this fresh run, and check presence of sub_0042C998.

## 2026-11-16 — V0.3 / corrected Ghidra-map rerun: output verified

User screenshot of local PowerShell checks confirms log line 530: 45170 functions loaded from Ghidra map and line 8180: Recompilation completed successfully.

- Fresh isolated output contains 45,171 CPP files, including register_functions.cpp.
- No generated filenames containing 0042C998 in the fresh output.
- Zero matches of unhandled_instruction in the fresh log.

Assessment: the former missing CSV path strongly explains the false-code generation; this symptom is no longer present. Other severity diagnostics and compilation remain unchecked. No proprietary artifacts committed.

## 2026-11-16 — CORRECTION: diagnostic-count spelling mistake

Screenshot shows corrected-map log contains **5,860 [error]** records and **1,786 [warning]** records. First examples are **[error] unhandled-instruction** in `entry_00403fc0` near `0x00403ffc`; they include unsupported SPECIAL decoded patterns. Earlier report of zero `unhandled_instruction` matched the **wrong spelling** (underscore versus hyphen). It does **not** mean instruction errors were resolved. The 45,171 generated CPP files, loaded map and missing `0042C998` filename remain true; function correctness and C++ compilability do not follow. Need group errors by category/function, inspect Ghidra code/data boundaries, and make safe isolated changes. Preserve source and game binary unchanged.

## 2026-11-16 — V0.3 — 5,860 unsupported instructions grouped by entry

PowerShell grouping shared by user: `entry_00403fc0`: **3,897**; `entry_004217d0`: **1,773**; `entry_0042c020`: **190**. Sum **5,860**, the entire count of `unhandled-instruction` messages in the log. The top two entries account for **96.76%** of this specific error category. Hypothesis: synthetic-entry spans may include data; confirmed previously for a portion of `entry_0042c020`, but **unverified** for other two spans. Next: inspect `0x00403fc0` in Ghidra and CSV. No source patches or file deletions authorized/applied.

## 2026-11-16 — V0.3 / Ghidra confirmed three overbroad synthetic entries

User CSV/Ghidra screenshots:
- `entry_00403fc0`: 0x00403FC0–0x00421720; 120,672 bytes, 3,897 errors; 2 disassembled instructions then undefined data.
- `entry_004217d0`: 0x004217D0–0x0042C020; 43,088 bytes, 1,773 errors; 2 disassembled instructions, then undefined data and switch jump table at 0x004217E0.
- `entry_0042c020`: 0x0042C020–0x0042D000; 4,064 bytes, 190 errors; 2 disassembled instructions then undefined bytes/string data.

Upstream PS2Recomp `ExportPS2Functions.java` implementation `collectExecutableLabelRecords` extends synthetic entries up to next known boundary or memory block rather than stopping at Ghidra non-instruction data. These ranges could therefore include bytes that are not code. Not all purported instruction starts are independently verified as executable logic.

Added local-only Python helper `scripts/v03_test_synthetic_ranges.py`, tested with synthetic CSV/TOML (original inputs unchanged, second run refuses overwrite). Generates isolated copies of map and config, experimentally caps exactly these **3** labels to 8 bytes and keeps 45,170 records. This experiment must not be treated as correct game semantics, and no proprietary content is committed. Await A/B run and error comparison before choosing permanent exporter change.

## 2026-11-16 — V0.3 A/B experiment completed: zero logged errors, warnings remain

User screenshot of a local run using the **experimental copies** of CSV/TOML (three 8-byte synthetic-entry caps): exit code **0**, `Loaded 45170 functions from Ghidra map`, `Recompilation completed successfully`; errors tagged `[error]`: **0** (baseline **5,860**); `[warning]`: **1,786** (baseline **1,786**); `unhandled-instruction`: **0** (baseline **5,860**). This confirms a causal link between the three excessive intervals and those diagnostics in this experiment. An arbitrary 8-byte truncation **can suppress legitimate code**, so this is not a proof of correct recompiled program. Outstanding: inspect warning types and completeness of generated files; fix exporter generally, validate control-flow/coverage, then attempt limited compile. No commercial assets committed.

## 2026-11-16 — V0.3 — A/B output verified, all warnings are control-flow

New PowerShell screenshot shows **45,171 CPP files**, **zero empty CPP files**, and `register_functions.cpp` exists in the **experimental** private generated folder. All **1,786 warnings** are categorized `control-flow` (category grouped from log); no errors or `unhandled-instruction` in experimental log. User has not yet provided individual warning messages or branch-target context, so warning severity is **not yet classified**. Need sample lines and aggregation by text/function. The experimental 8-byte truncations remain *unvalidated as semantically correct* and a full native PC build/runtime does not exist yet.

## 2026-11-16 — V0.3 / control-flow warnings examined

User screenshot provided 10 sample `control-flow` warnings. They report unresolved `JR/JALR` sites with promotion of many fallback entries to support indirect execution. Example: `FUN_00103018` unresolved at `0x1030c0`, `0x1030d4`, promoted 135 fallback entries. Other sample functions report 29, 30, 51, 82, 92, 113, 115, 118 fallback entries. Frequency table shows warnings broadly distributed across functions (e.g., `caseD_0`: 4; multiple functions 2), unlike three pseudo-entry ranges explaining unsupported instructions. Need inspect representative cases and quantify fallback cost; zero translation errors cannot establish correct indirect control-flow. No generated proprietary code uploaded.
