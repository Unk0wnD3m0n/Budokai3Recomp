# Hoja de ruta técnica — Budokai3Recomp

**Objetivo inicial:** PS2 Collector's Edition (SLES-53346), no HD Collection. Cada fase necesita evidencia verificable y puede resultar inviable.

| Versión | Objetivo | Condición de avance | Estado |
|---|---|---|---|
| V0.1 | Inspección ISO9660 / BOOT2 / ELF | Tests sintéticos pasan; ISO propia reconocida localmente | PASS — ISO original reconocida localmente en Windows (2026-11-16) |
| V0.2 | Mapa de funciones / Ghidra | Funciones, segmentos y dependencias documentadas | V0.2a PASS (2 LOAD, 1 ejecutable); V0.2b PASS (13 tests; ELF local extraído y hash cotejado); Ghidra 12.2 Auto Analyze PASS (544078 instrucciones, 7328 funciones candidatas); V0.2d PASS (CSV 45170 registros / 1831275 B; TOML 2579 B con [general]); evaluar límites de mapa antes de recompilar |
| V0.3 | Primera recompilación PS2Recomp | Generar C++ y compilar prueba con CMake/MSVC | Recompilador ejecutado hasta fin; varios `unhandled_instruction`; inspección de salida y compilación del C++ pendientes |
| V0.4 | Runtime/arranque | Inicializar código de PS2 y registrar faltantes | Pendiente |
| V0.5 | GS/VU/DMA y gráficos | Primer fotograma reproducible en PC | Pendiente |
| V0.6 | Audio, mando y menús | Navegar menús y probar guardado | Pendiente |
| V0.7 | Combate | Pelea reproducible y estable | Pendiente |
| V1.0 | Port jugable | Instalación a partir de copia propia y pruebas amplias | Meta futura, no garantizada |

## Protocolo

1. Documentar una prueba medible y su versión.
2. Registrar PASS, FAIL o BLOCKED y el motivo.
3. Mantener una versión estable antes de cambiar subsistemas.
4. No declarar que algo funciona solo porque compila.
5. Nunca subir contenido comercial, ni en issues, logs o CI.

## Riesgos

- El PS2 usa EE MIPS R5900, IOP, SPU2, GS, VU y DMA; recompilar instrucciones no sustituye esos sistemas.
- Los offsets y direcciones de Greatest Hits NTSC no tienen por qué coincidir con Collector's Edition PAL.
- El ELF de venta puede carecer de símbolos; la ingeniería inversa puede ser extensa.
- GPL y AGPL de referencias externas requieren una revisión de licencia antes de copiar código.
