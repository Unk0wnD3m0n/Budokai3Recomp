# Budokai3Recomp 🐉

**CYBER NEXUS — Proyecto experimental de recompilación nativa de Dragon Ball Z: Budokai 3 Collector's Edition (PS2, SLES-53346) para Windows.**

> **V0.1.0 — EXPLORING. Esto NO es todavía un port jugable.**

## Objetivo

Investigar la viabilidad de recompilar el ejecutable de PlayStation 2 a C++ y crear los sistemas de gráficos, sonido, entrada y guardado necesarios para ejecutarlo de forma nativa en Windows. No es un emulador ni una conversión automática de ISOs.

## Primera prueba: analizar tu ISO

Requisitos: Python 3.10+; sin dependencias externas. El analizador solo lee metadatos locales de imágenes ISO9660 de sectores de 2048 bytes.

```powershell
py -3 scripts/inspect_iso.py "D:\Mis Juegos\Budokai 3 Collector's Edition.iso" --report reporte-local.json
```

Pruebas automáticas (utilizan archivos sintéticos, NO datos comerciales):

```powershell
py -3 -m unittest discover -s tests -v
```

Identifica SYSTEM.CNF, BOOT2, ejecutable ELF MIPS, número de serie y hash SHA-256 del ELF. El informe se guarda solo en el PC del usuario. **Que una ISO se reconozca no significa que vaya a recompilarse.**

## Segunda prueba — V0.2a: mapa de memoria ELF32

Descarga la versión más reciente del repositorio y desde PowerShell ejecuta:

```powershell
python .\scripts\inspect_elf_layout.py ".\DragonBall Z - Budokai 3 - Collector's Edition (Europe) (En,Ja,Fr,De,Es,It).iso" --report reporte-v02-local.json
```

Si tu ISO está en otra carpeta, utiliza su ruta. Esto genera únicamente metadatos de segmentos, secciones y permisos de memoria. No recompila ni ejecuta el juego. Detalles en [docs/V02_ANALYSIS.md](docs/V02_ANALYSIS.md).

## Fases

Consulta [docs/ROADMAP.md](docs/ROADMAP.md): inspección de ISO → análisis del ELF → recompilación C++ → runtime → gráficos → controles/audio → primer combate → posible port jugable.

## Referencias

- [PS2Recomp](https://github.com/ran-j/PS2Recomp) — recompilador y runtime experimental (GPL-3.0).
- [Tenkaichi3Decomp](https://github.com/z3xox/Tenkaichi3Decomp) — ejemplo de port nativo de otro juego PS2 (AGPL-3.0).
- [Budokai 3 GH NTSC ELF Decomp](https://github.com/TotallyNotMichael/dbz3-gh-ntsc-elf-decomp) — investigación de otra edición, NO intercambiable automáticamente con SLES-53346.

Estas bases son referencias: **V0.1.0 no incorpora código ajeno**. La licencia MIT del código original de este repositorio no relicencia dependencias GPL/AGPL.

## Seguridad y derechos

Este repositorio no incluye ni acepta ISOs, ROMs, ELFs comerciales, archivos del juego, firmware, claves, músicas, voces o texturas protegidas. Cada usuario debe usar sus propios archivos de forma local y respetar las normas aplicables. No subas informes que contengan rutas personales.

Desarrollado como proyecto independiente por colaboradores de CYBER NEXUS, sin afiliación con Bandai Namco, Atari, Dimps ni otros titulares.
